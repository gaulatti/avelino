#!/usr/bin/env python3
"""Exercise the real ActivityItem catalog adapters before the complete capture run."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog, imports, root = map(Path, sys.argv[1:])
spec = importlib.util.spec_from_file_location('activity_capture_inputs', root / 'scripts/capture-activity-cases.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
source = json.loads((capture.SOURCE / 'captures/captures.json').read_text())
definitions = capture.definitions(source)
cases = ['default-icon', 'width-0', 'width-12', 'width-109', 'width-240', 'all-empty',
         'actions-multi-direct', 'actions-empty-direct', 'actions-counter', 'actions-hidden',
         'symbol-empty', 'intrinsic', 'locale-ar', 'parent-font32-plain', 'rtl']
with tempfile.TemporaryDirectory(prefix='avelino-activity-catalog-') as temporary:
    directory = Path(temporary)
    inputs = directory / 'fixtures.json'
    inputs.write_text(json.dumps(definitions, ensure_ascii=False))
    environment = dict(os.environ, QML_IMPORT_PATH=str(imports), QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software', QT_SCALE_FACTOR='1')
    for index, name in enumerate(cases):
        row = next(row for row in definitions['fixtures'] if row['fixture'] == name)
        native = next(row for row in source['captures'] if row['fixture'] == name and row['appearance'] == 'light' and row['textScale'] == 1 and row['dpr'] == 1)
        image = directory / f'{index}.png'
        subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', name, '--case-definitions', str(inputs), '--capture', str(image)],
                       env=environment, check=True, capture_output=True, timeout=20)
        actual = json.loads(image.with_name(image.name + '.json').read_text())
        for field in ['title', 'detail', 'timestamp']:
            assert actual['rendered' + field.title()] == row[field], (name, field)
        assert actual['renderedActionMode'] == row['actions'] and actual['renderedDisabled'] == row['disabled'] and actual['renderedRtl'] == row['rtl'], name
        assert actual['componentSize'] == {key: native['componentRect'][key] for key in ['width', 'height']}, (name, actual['componentSize'])
        assert actual['componentOrigin'] == {key: native['componentRect'][key] for key in ['x', 'y']}, (name, actual['componentOrigin'])
        labels = {row['role']: row for row in actual['labels']}
        for label, pixels in [('Title', 14), ('Detail', 12), ('Timestamp', 10)]:
            assert labels['bleeckerActivity' + label]['resolvedGlyphPixelSize'] == pixels, (name, label)
        if name == 'parent-font32-plain':
            assert labels['activityActionPlainText']['requestedLogicalPixelSize'] == 32
        if name == 'actions-counter':
            assert actual['actionLocalValue'] == 0 and actual['actionAppears'] == 1
        if row['actions'] in ['empty', 'empty-direct']:
            assert not any(key.startswith('action-') for key in actual['layoutWitnessRects'])
    forged = dict(next(row for row in definitions['fixtures'] if row['fixture'] == 'width-0'), expectedEmpty=True)
    inputs.write_text(json.dumps({'fixtures': [forged]}))
    result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', 'width-0', '--case-definitions', str(inputs),
                             '--capture', str(directory / 'forged.png')], env=environment, capture_output=True, timeout=20)
    assert result.returncode == 6 and b'Invalid isolated geometry' in result.stderr, result
print('ActivityItem catalog: 15 public state/font/slot/geometry adapters and forged-empty refusal passed')
