#!/usr/bin/env python3
"""Exercise native dropdown definitions through the isolated catalog path."""
import concurrent.futures
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog, imports, root = map(Path, sys.argv[1:])
spec = importlib.util.spec_from_file_location('dropdown_capture', root / 'scripts/capture-dropdown-menu.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
definitions = capture.definitions()['fixtures']
native = json.loads((root / 'tests/consumer/native-dropdown-menu-witnesses.json').read_text())
expected = {row['configuration']['id']: row for row in native['closed']
    if row['appearance'] == 'light' and row['textScale'] == row['dpr'] == 1}
with tempfile.TemporaryDirectory(prefix='avelino-dropdown-catalog-') as temporary:
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
        identifier = definition['configuration']['id']
        assert result.returncode == 0, (identifier, result.returncode, log)
        assert not any(x in log for x in ['Unable to assign', 'ReferenceError', 'TypeError', 'Error:', 'Binding loop', 'QFont::']), (identifier, log)
        meta = json.loads(Path(str(image) + '.json').read_text())
        state = meta['dropdownMenuState']
        assert state['title'] == expected[identifier]['title'], (identifier, state)
        assert state['count'] == state['distinctIdentities']
        assert state['popupBuiltCount'] == state['labelActions'] == 0
        assert set(meta['dropdownMenuFrame']) == {'body', 'caller', 'label'}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(run, definitions))
    base = next(d for d in definitions if d['configuration']['id'] == 'default')
    invalid = [dict(base, source='unapproved'), dict(base, width=320),
        dict(base, extra=True), dict(base, configuration=[])]
    for key, value in [('controlSize', 'unknown'), ('label', 'unknown'), ('itemMode', 'unknown'),
        ('disabled', 1), ('empty', 'false'), ('parentFont', None), ('title', 3),
        ('width', -1), ('height', '0'), ('extra', True)]:
        item = copy.deepcopy(base)
        item['configuration'][key] = value
        invalid.append(item)
    for key in base:
        if key != 'api':
            item = dict(base)
            del item[key]
            invalid.append(item)
    for index, value in enumerate(invalid):
        inputs.write_text(json.dumps(dict(fixtures=[value])))
        result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', base['fixture'],
            '--case-definitions', str(inputs), '--capture', str(folder / f'invalid-{index}.png')],
            env=environment, capture_output=True)
        assert result.returncode == 6, (value, result.returncode, result.stderr.decode(errors='replace'))
print(f'DropdownMenu catalog: {len(definitions)} native definitions and {len(invalid)} malformed definitions; parity pending')
