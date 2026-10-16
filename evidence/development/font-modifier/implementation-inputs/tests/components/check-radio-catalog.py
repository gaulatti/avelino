#!/usr/bin/env python3
"""Exercise zero-size source cases and subpixel-font metadata through the real catalog."""
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

catalog, imports, repository = map(Path, sys.argv[1:])
spec = importlib.util.spec_from_file_location('radio_capture', repository / 'scripts/capture-radio-cases.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
source = json.loads((capture.SOURCE / 'captures/captures.json').read_text())
with tempfile.TemporaryDirectory(prefix='avelino-radio-catalog-') as name:
    root = Path(name)
    definitions = capture.definitions(source)
    inputs = root / 'inputs.json'
    inputs.write_text(json.dumps(definitions))
    for fixture in ['empty-vertical', 'empty-horizontal', 'primary-font-0.3', 'primary-font-13.5']:
        for dpr in [1, 2]:
            path = root / (fixture + '-' + str(dpr) + '.png')
            environment = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software', QT_SCALE_FACTOR=str(dpr), QML_IMPORT_PATH=str(imports))
            result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', fixture,
                '--case-definitions', str(inputs), '--capture', str(path)], env=environment, capture_output=True, timeout=30)
            assert result.returncode == 0, (fixture, dpr, result.returncode, result.stdout + result.stderr)
            data = json.loads(Path(str(path) + '.json').read_text())
            assert struct.unpack('>II', path.read_bytes()[16:24]) == (720 * dpr, 520 * dpr)
            if fixture.startswith('empty-'):
                assert data['componentSize'] == {'width': 0, 'height': 0} and data['renderedOptions'] == []
            else:
                labels = [row for row in data['labels'] if row['role'] == 'bleeckerRadioTitle']
                assert len(labels) == 3
                assert all(row['resolvedGlyphPixelSize'] == (12 if fixture.endswith('0.3') else 14) for row in labels)
                if fixture.endswith('0.3'):
                    assert all(row['family'] == 'Encode Sans' and row['fontResolutionStatus'] == 'renderer-reported' for row in labels)
                    templates = [row for row in data['labels'] if row['role'].startswith('bleeckerRadioOption')]
                    assert len(templates) == 3 and all(row['family'] is None and row['fontResolutionStatus'].startswith('unavailable') for row in templates)
    # A declared empty contract cannot bless a nonempty group's dimensions.
    bad = next(row for row in definitions['fixtures'] if row['fixture'] == 'vertical')
    bad['expectedEmpty'] = True
    inputs.write_text(json.dumps({'fixtures': [bad]}))
    result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', 'vertical',
        '--case-definitions', str(inputs), '--capture', str(root / 'invalid.png')], env=environment, capture_output=True, timeout=30)
    assert result.returncode == 6 and b'Invalid isolated geometry or expected-empty contract' in result.stderr
print('Radio catalog: eight real captures preserve empty bounds and renderer font resolution; forged empty contract refused')
