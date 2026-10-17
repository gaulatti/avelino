#!/usr/bin/env python3
"""Exercise all native app-tab definitions through the isolated catalog path."""
import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog, imports, root = map(Path, sys.argv[1:])
spec = importlib.util.spec_from_file_location('command_spotlight_capture', root / 'scripts/capture-command-spotlight.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
definitions = capture.definitions()['fixtures']
with tempfile.TemporaryDirectory(prefix='avelino-command-spotlight-catalog-') as temporary:
    folder = Path(temporary)
    inputs = folder / 'fixtures.json'
    inputs.write_text(json.dumps(dict(fixtures=definitions), ensure_ascii=False))
    environment = dict(os.environ, QML_IMPORT_PATH=str(imports), QT_QPA_PLATFORM='offscreen',
        QT_QUICK_BACKEND='software', QT_SCALE_FACTOR='1')

    def run(definition):
        image = folder / (definition['fixture'] + '.png')
        result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', definition['fixture'],
            '--case-definitions', str(inputs), '--capture', str(image)], env=environment, capture_output=True)
        log = (result.stdout + result.stderr).decode(errors='replace')
        assert result.returncode == 0, (definition['id'], result.returncode, log)
        assert not any(x in log for x in ['Unable to assign', 'ReferenceError', 'TypeError', 'Error:', 'Binding loop', 'QFont::']), (definition['id'], log)
        meta = json.loads(Path(str(image) + '.json').read_text())
        assert meta['commandSpotlightState']['lifecycle'] == dict(appearances=1, disappearances=0, wrapperInstances=1)
        frames = meta['commandSpotlightFrame']
        assert frames['body']['width'] == 520 and frames['body']['height'] == 380
        assert all(k in frames for k in ['caller', 'search', 'header', 'separator', 'stack', 'scroll'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run, definitions))
    base = next(d for d in definitions if d['id'] == 'default')
    invalid = [dict(base, source='unapproved'), dict(base, callerWidth='300'), dict(base, callerHeight={}),
        dict(base, valueKind='unknown'), dict(base, owner='unknown'), dict(base, disabled=1),
        dict(base, entries={}), dict(base, width=320), dict(base, extra=True), dict(base, query=None),
        dict(base, entries=[dict(base['entries'][0], id=None)]),
        dict(base, entries=[dict(base['entries'][0], kind='unknown')]),
        dict(base, entries=[dict(base['entries'][0], disabled='false')]),
        dict(base, entries=[dict(base['entries'][0], height=-1)]),
        dict(base, entries=[dict(base['entries'][0], kind='fixed')]),
        dict(base, entries=[base['entries'][0], base['entries'][0]])]
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
print(f'Command spotlight catalog: {len(definitions)} native definitions and {len(invalid)} malformed definitions; parity pending')
