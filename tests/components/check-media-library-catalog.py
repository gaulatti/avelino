#!/usr/bin/env python3
"""Keep every native MediaLibrary input addressable through the catalog."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog, imports, root = map(Path, sys.argv[1:])
projection = json.loads((root / 'tests/consumer/native-media-library-witnesses.json').read_text())
rows = [r for r in projection['closed'] + projection['edges']
    if (r['appearance'], r['textScale'], r['dpr']) == ('light', 1, 1)]
assert len(rows) == 76
definitions = [dict(r['configuration'], api='BleeckerMediaLibrary', source=projection['reference'],
    fixture='media-' + r['configuration']['id'], libraryWidth=r['configuration']['width'],
    libraryHeight=r['configuration'].get('height'), width=640, height=400) for r in rows]
with tempfile.TemporaryDirectory(prefix='avelino-media-catalog-') as temporary:
    folder = Path(temporary)
    inputs = folder / 'fixtures.json'
    inputs.write_text(json.dumps(dict(fixtures=definitions), ensure_ascii=False))
    environment = dict(os.environ, QML_IMPORT_PATH=str(imports), QT_QPA_PLATFORM='offscreen',
        QT_QUICK_BACKEND='software', QT_SCALE_FACTOR='1')
    def run(pair):
        row, definition = pair
        image = folder / (definition['fixture'] + '.png')
        result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', definition['fixture'],
            '--case-definitions', str(inputs), '--capture', str(image)], env=environment, capture_output=True)
        log = (result.stdout + result.stderr).decode(errors='replace')
        if row.get('nativeExitCode', 0):
            assert result.returncode != 0 and 'minimumTileWidth -16' in log and not image.exists(), (definition, result.returncode, log)
            return
        assert result.returncode == 0, (definition['id'], result.returncode, log)
        assert not any(x in log for x in ['Unable to assign', 'ReferenceError', 'TypeError', 'Error:', 'Binding loop', 'QFont::']), (definition['id'], log)
        meta = json.loads(Path(str(image) + '.json').read_text())
        assert meta['mediaState']['appearances'] == meta['mediaState']['wrapperInstances'] == 1
        assert meta['mediaState']['disappearances'] == 0
        assert len(meta['mediaMetrics']['entries']) == len(definition['items'])
        assert meta['mediaMetrics']['nativeRasterAcceptance'] == 'pending'
        assert set(meta['mediaFrame']) == {'caller', 'grid', 'tiles'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run, zip(rows, definitions)))
    base = definitions[0]
    invalid = [dict(base, source='unapproved'), dict(base, libraryWidth='460'), dict(base, libraryHeight={}),
        dict(base, minimumTileWidth='NaN'), dict(base, slot='unknown'), dict(base, disabled=1),
        dict(base, items={}), dict(base, width=320), dict(base, extra=True),
        dict(base, items=[dict(id='a', title='A', width=10, height=-1, color=0)]),
        dict(base, items=[dict(id='a', title='A', width=10, height=20, color=0.5)])]
    for key in base:
        if key == 'api':
            continue
        value = dict(base)
        del value[key]
        invalid.append(value)
    for index, value in enumerate(invalid):
        inputs.write_text(json.dumps(dict(fixtures=[value])))
        result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', base['fixture'],
            '--case-definitions', str(inputs), '--capture', str(folder / f'invalid-{index}.png')],
            env=environment, capture_output=True)
        assert result.returncode == 6, (value, result.returncode, result.stderr.decode(errors='replace'))
print(f'MediaLibrary catalog: 75 successful native inputs, one isolated fatal input and {len(invalid)} malformed definitions; parity pending')
