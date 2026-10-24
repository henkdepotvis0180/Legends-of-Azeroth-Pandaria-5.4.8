#!/usr/bin/env python3
"""Exercise resume, Range fallback, reuse and rejection using a local HTTP source."""
import hashlib
import importlib.util
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest

source = Path(__file__).resolve().parents[1] / 'recovery/download_client_batch.py'
spec = importlib.util.spec_from_file_location('batch_downloader', source)
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)
PAYLOAD = b'MPQ\x1a' + bytes(range(256)) * 1024


class Handler(BaseHTTPRequestHandler):
    mode = 'range'
    requests_seen = []

    def do_GET(self):
        header = self.headers.get('Range')
        Handler.requests_seen.append(header)
        offset = int(header.split('=')[1].split('-')[0]) if header else 0
        if header and Handler.mode != 'ignore':
            self.send_response(206)
            start = offset + 1 if Handler.mode == 'bad-range' else offset
            self.send_header('Content-Range', f'bytes {start}-{len(PAYLOAD)-1}/{len(PAYLOAD)}')
            content = PAYLOAD[offset:]
        else:
            self.send_response(200)
            content = PAYLOAD
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass


class DownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.item = {'file': 'Data/fixture.MPQ', 'bytes': len(PAYLOAD)}
        self.target = self.root / self.item['file']
        self.target.parent.mkdir()
        self.partial = self.target.with_name(self.target.name + '.part')
        Handler.mode = 'range'
        Handler.requests_seen.clear()

    def verify_download(self):
        result = batch.download(self.url, self.root, self.item)
        self.assertEqual(self.target.read_bytes(), PAYLOAD)
        self.assertEqual(result['sha256'], hashlib.sha256(PAYLOAD).hexdigest())
        self.assertFalse(self.partial.exists())
        return result

    def test_fresh(self):
        self.verify_download()
        self.assertEqual(Handler.requests_seen, [None])

    def test_resume(self):
        self.partial.write_bytes(PAYLOAD[:12345])
        self.verify_download()
        self.assertEqual(Handler.requests_seen, ['bytes=12345-'])

    def test_ignored_range_restarts_without_duplicate_bytes(self):
        Handler.mode = 'ignore'
        self.partial.write_bytes(PAYLOAD[:12345])
        self.verify_download()

    def test_bad_range_preserves_existing_partial(self):
        Handler.mode = 'bad-range'
        self.partial.write_bytes(PAYLOAD[:12345])
        with self.assertRaises(ValueError):
            batch.download(self.url, self.root, self.item)
        self.assertEqual(self.partial.read_bytes(), PAYLOAD[:12345])
        self.assertFalse(self.target.exists())

    def test_completed_file_reused_without_network(self):
        self.target.write_bytes(PAYLOAD)
        self.assertTrue(self.verify_download()['reused_completed_file'])
        self.assertEqual(Handler.requests_seen, [])

    def test_wrong_size_completed_file_not_overwritten(self):
        self.target.write_bytes(b'keep')
        with self.assertRaises(ValueError):
            batch.download(self.url, self.root, self.item)
        self.assertEqual(self.target.read_bytes(), b'keep')

    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            batch.download(self.url, self.root, {'file': '../outside', 'bytes': 5})


if __name__ == '__main__':
    unittest.main()
