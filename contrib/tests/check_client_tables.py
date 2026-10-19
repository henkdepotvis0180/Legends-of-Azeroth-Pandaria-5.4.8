#!/usr/bin/env python3
"""Validate extracted 5.4.8 table payloads and active core load formats, without a worldserver."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

MARKERS = {'BattlePetAbility.db2':1238, 'BattlePetSpecies.db2':1386,
           'BattlePetState.db2':176, 'BroadcastText.db2':77161, 'Item.db2':112353,
           'ItemExtendedCost.db2':5280, 'QuestPackageItem.db2':2256, 'SceneScript.db2':11156}


def uncomment(text):
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)


def core_formats(root):
    folder = root / 'src/server/game/DataStores'
    formats = {}
    for name in ['DBCfmt.h', 'DB2fmt.h']:
        formats.update(re.findall(r'(\w+)\s*\[\s*\]\s*=\s*"([^"]*)"', uncomment((folder/name).read_text())))
    dbc = uncomment((folder/'DBCStores.cpp').read_text())
    stores = dict(re.findall(r'DBCStorage\s*<[^>]+>\s*(\w+)\s*\(\s*(\w+)', dbc))
    required = {}
    for store, name in re.findall(r'(?:LOAD_DBC|LoadDBC)\(\s*availableDbcLocales\s*,\s*bad_dbc_files\s*,\s*(\w+)\s*,\s*dbcPath\s*,\s*"([^"]+\.dbc)"', dbc):
        required[name] = formats[stores[store]]
    db2 = uncomment((folder/'DB2Stores.cpp').read_text())
    stores = {store:(name,fmt) for store,name,fmt in re.findall(r'DB2Storage\s*<[^>]+>\s*(\w+)\s*\(\s*"([^"]+\.db2)"\s*,\s*(\w+)', db2)}
    for store in re.findall(r'LoadDB2\(\s*availableDb2Locales\s*,\s*bad_db2_files\s*,\s*_stores\s*,\s*&(\w+)', db2):
        name, fmt = stores[store]
        required[name] = formats[fmt]
    if not required:
        raise ValueError('No active core formats found')
    return required


def header(data):
    if len(data) < 20:
        raise ValueError('Truncated header')
    magic, rows, fields, width, strings = struct.unpack_from('<4s4I', data)
    start = 20
    if magic == b'WDB2':
        if len(data) < 48:
            raise ValueError('Truncated DB2 header')
        build = struct.unpack_from('<I', data, 24)[0]
        if build <= 12880:
            raise ValueError('Unsupported old DB2 header')
        low, high = struct.unpack_from('<ii', data, 32)
        start = 48
        if high:
            if low < 0 or high < low:
                raise ValueError('Invalid DB2 index range')
            start += (high-low+1)*6
    elif magic != b'WDBC':
        raise ValueError(f'Unsupported signature {magic!r}')
    if not fields or not width or start + rows*width + strings > len(data):
        raise ValueError('Invalid dimensions or truncated payload')
    return rows, fields, width, strings, start


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    required = core_formats(args.source)
    inventory = []; extras = []; non_required_issues = []; seen = set(); markers = {}
    for path in sorted((args.data/'dbc').rglob('*')):
        if path.suffix.lower() not in ('.dbc', '.db2'):
            continue
        data = path.read_bytes()
        name = path.name
        try:
            rows, fields, width, strings, start = header(data)
        except ValueError as error:
            if name in required:
                raise ValueError(f'{name}: {error}') from error
            non_required_issues.append({'file':name,'bytes':len(data),'issue':str(error)})
            inventory.append({'file':str(path.relative_to(args.data)), 'bytes':len(data),
                              'sha256':hashlib.sha256(data).hexdigest(), 'header_valid':False})
            continue
        if path.suffix.lower() == '.db2' and path.parent.name != 'enUS':
            raise ValueError(f'DB2 outside enUS directory: {path}')
        if name in required:
            fmt = required[name]
            expected_width = sum(1 if c in 'bX' else 4 for c in fmt)
            if len(fmt) != fields or width < expected_width:
                raise ValueError(f'Core format mismatch: {name}')
            offset = 0
            for char in fmt:
                if char == 's':
                    for row in range(rows):
                        ref = struct.unpack_from('<I', data, start+row*width+offset)[0]
                        if ref >= strings:
                            raise ValueError(f'String offset out of bounds: {name}')
                offset += 1 if char in 'bX' else 4
            if width > expected_width:
                extras.append({'file':name,'record_bytes':width,'format_bytes':expected_width})
            seen.add(name)
        if name in MARKERS:
            ids = [struct.unpack_from('<I', data, start+row*width)[0] for row in range(rows)]
            if MARKERS[name] not in ids or max(ids) != MARKERS[name]:
                raise ValueError(f'5.4.8 version marker mismatch: {name}')
            markers[name] = MARKERS[name]
        inventory.append({'file':str(path.relative_to(args.data)), 'bytes':len(data),
                          'sha256':hashlib.sha256(data).hexdigest(), 'rows':rows})
    if seen != set(required) or markers != MARKERS:
        raise ValueError(f'Missing required tables or markers: {sorted(set(required)-seen)}')
    report = {'status':'passed', 'scope':'Required active core tables: headers/payload sizes, formats, minimum record width and string offset bounds; eight 5.4.8 marker IDs. Non-required table issues are reported separately. No native server start or gameplay test.',
              'dbc_files':sum(x['file'].endswith('.dbc') for x in inventory),
              'db2_files':sum(x['file'].endswith('.db2') for x in inventory),
              'required_dbc_files':sum(n.endswith('.dbc') for n in required),
              'required_db2_files':sum(n.endswith('.db2') for n in required),
              'extra_record_bytes_notes':extras, 'non_required_table_issues':non_required_issues, 'version_markers':markers, 'files':inventory}
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))


if __name__ == '__main__':
    main()
