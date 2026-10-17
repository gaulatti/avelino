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
spec = importlib.util.spec_from_file_location('app_tabs_capture', root / 'scripts/capture-app-tabs.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
definitions = capture.definitions()['fixtures']
with tempfile.TemporaryDirectory(prefix='avelino-app-tabs-catalog-') as temporary:
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
        assert meta['appTabState'] == dict(appearances=1, disappearances=0, wrapperInstances=1)
        frames = meta['appTabFrame']
        assert 'bar' in frames and 'caller' in frames
        assert len([k for k in frames if k.startswith('button-')]) == len(definition['tabs'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run, definitions))
    base = next(d for d in definitions if d['id'] == 'width-300')
    invalid = [dict(base, source='unapproved'), dict(base, tabWidth='300'), dict(base, tabHeight={}),
        dict(base, valueKind='unknown'), dict(base, owner='unknown'), dict(base, disabled=1),
        dict(base, tabs={}), dict(base, width=320), dict(base, extra=True),
        dict(base, tabs=[dict(value='a', label='Home', systemImage='house', badge='9223372036854775808')]),
        dict(base, tabs=[dict(value='a', label='Home', systemImage='house', disabled='false')])]
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
print(f'App tabs catalog: {len(definitions)} native definitions and {len(invalid)} malformed definitions; parity pending')
