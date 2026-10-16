#!/usr/bin/env python3
"""Check real OTP catalog adapters before generating the complete capture matrix."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog, imports, root = map(Path, sys.argv[1:])
spec = importlib.util.spec_from_file_location('otp_capture_inputs', root / 'scripts/capture-otp-cases.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
source = json.loads((capture.SOURCE / 'captures/captures.json').read_text())
definitions = capture.definitions(source)
with tempfile.TemporaryDirectory(prefix='avelino-otp-catalog-') as directory:
    output = Path(directory)
    inputs = output / 'fixtures.json'
    inputs.write_text(json.dumps(definitions, ensure_ascii=False))
    cases = ['default-length', 'nonempty-length-zero', 'unfiltered-initial', 'mathematical', 'width-0', 'width-12', 'parent-font32', 'intrinsic-value']
    for index, name in enumerate(cases):
        row = next(row for row in definitions['fixtures'] if row['fixture'] == name)
        image = output / f'{index}.png'
        environment = dict(os.environ, QML_IMPORT_PATH=str(imports), QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software')
        subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', name, '--case-definitions', str(inputs), '--capture', str(image)],
                       env=environment, check=True, capture_output=True, timeout=20)
        actual = json.loads(image.with_name(image.name + '.json').read_text())
        assert actual['renderedCode'] == actual['renderedFieldValue'] == row['code'], name
        assert actual['renderedLength'] == row['length'] and actual['renderedPlaceholder'] == '•' * row['length'], name
        assert actual['renderedCenterAligned'] and actual['editorMaximumLength'] == 2147483647, name
        width = row['width'] if row['intrinsic'] else max(28, row['proposalWidth'])
        assert actual['componentSize'] == dict(width=width, height=40), (name, actual['componentSize'])
        assert abs(actual['componentOrigin']['x'] - (row['width'] - width) / 2) < 1e-6, name
    forged = next(row for row in definitions['fixtures'] if row['fixture'] == 'width-0')
    forged['expectedEmpty'] = True
    inputs.write_text(json.dumps({'fixtures': [forged]}))
    result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', 'width-0', '--case-definitions', str(inputs),
                             '--capture', str(output / 'forged-empty.png')], env=environment, capture_output=True, timeout=20)
    assert result.returncode == 6 and b'Invalid isolated geometry' in result.stderr, result
print('OTP catalog: eight real metadata/geometry/getter cases passed, including narrow and inherited-font adapters')
