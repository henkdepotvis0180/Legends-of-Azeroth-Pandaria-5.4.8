#!/usr/bin/env python3
"""Download one pinned MoP 18414 source batch, retaining resumable .part files."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import time
import urllib.request


def digest(path, algorithm='sha256'):
    result = hashlib.new(algorithm)
    with path.open('rb') as stream:
        while block := stream.read(4 * 1024 * 1024):
            result.update(block)
    return result.hexdigest()


def download(base, destination, item):
    relative = PurePosixPath(item['file'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe source path')
    target = destination.joinpath(*relative.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    expected = item['bytes']
    reused = target.exists()
    if reused and target.stat().st_size != expected:
        raise ValueError(f'Existing completed file has the wrong size: {relative}')
    if not reused:
        partial = target.with_name(target.name + '.part')
        offset = partial.stat().st_size if partial.exists() else 0
        if offset > expected:
            raise ValueError(f'Partial file is too large: {relative}')
        if offset < expected:
            headers = {'Range': f'bytes={offset}-'} if offset else {}
            with urllib.request.urlopen(urllib.request.Request(base + str(relative), headers=headers), timeout=60) as response:
                if response.status == 206:
                    value = response.headers.get('Content-Range', '')
                    match = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', value)
                    if not match or int(match[1]) != offset or int(match[3]) != expected:
                        raise ValueError(f'Unexpected Content-Range for {relative}')
                    mode = 'ab'
                elif response.status == 200:
                    mode = 'wb'  # Server ignored Range: restart this file safely.
                else:
                    raise ValueError(f'Unexpected HTTP status {response.status}')
                with partial.open(mode) as stream:
                    while block := response.read(1024 * 1024):
                        stream.write(block)
                    stream.flush()
        if partial.stat().st_size != expected:
            raise ValueError(f'Incomplete download retained for resume: {relative}')
        partial.replace(target)
    with target.open('rb') as stream:
        signature = stream.read(4)
    if signature not in (b'MPQ\x1a', b'MPQ\x1b'):
        raise ValueError(f'Unexpected MPQ signature: {relative}')
    return {'file': str(relative), 'bytes': expected, 'sha256': digest(target),
            'mpq_signature_hex': signature.hex(), 'reused_completed_file': reused}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=3, choices=range(1, 5))
    parser.add_argument('--recipe', type=Path, default=Path(__file__).resolve().parents[2] / 'doc/validation/client-data-2026-10-18.json')
    args = parser.parse_args()
    recipe = json.loads(args.recipe.read_text())
    items = [item for item in recipe['files'] if item['file'].startswith('Data/enUS/wow-update-enUS-')
             or item['file'] in ('Data/base-Win.MPQ', 'Updates/wow-0-18414-Win-final.MPQ')]
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = args.output / recipe['source_manifest']
    with urllib.request.urlopen(recipe['source'] + recipe['source_manifest'], timeout=60) as response:
        content = response.read(4 * 1024 * 1024 + 1)
    if hashlib.md5(content).hexdigest() != recipe['manifest_md5']:
        raise ValueError('Pinned source manifest MD5 mismatch')
    manifest.write_bytes(content)
    report = {'status': 'running', 'batch': '02-enus-and-windows-patches',
              'client_build': 18414, 'source': recipe['source'],
              'source_manifest': recipe['source_manifest'], 'manifest_md5_verified': True,
              'manifest_sha256': digest(manifest), 'expected_files': len(items),
              'expected_bytes': sum(item['bytes'] for item in items), 'files': [], 'errors': [],
              'integrity_note': 'Sizes and manifest MD5 match the pinned historical recipe. Recorded SHA-256 hashes identify received bytes; they are not independent upstream digests.'}
    def save():
        temporary = args.output / 'batch-report.json.tmp'
        temporary.write_text(json.dumps(report, indent=2) + '\n')
        temporary.replace(args.output / 'batch-report.json')
    save()
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = {executor.submit(download, recipe['source'], args.output, item): item for item in items}
        for future in as_completed(pending):
            try:
                result = future.result()
                report['files'].append(result)
                print(f"OK {len(report['files'])}/{len(items)} {result['file']}", flush=True)
            except Exception as error:
                report['errors'].append({'file': pending[future]['file'], 'error': str(error)})
                print(f"ERROR {pending[future]['file']}: {error}", flush=True)
            save()
    report['files'].sort(key=lambda item: item['file'])
    report['status'] = 'passed' if not report['errors'] and len(report['files']) == len(items) else 'failed'
    report['completed_at_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    save()
    if report['status'] != 'passed':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
