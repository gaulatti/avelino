#!/usr/bin/env python3
"""Exercise real Modal capture adapters, including zero body and outer allocation."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog, imports, root = map(Path, sys.argv[1:])
spec = importlib.util.spec_from_file_location('modal_capture_inputs', root / 'scripts/capture-modal-cases.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
source = json.loads((capture.SOURCE / 'captures/captures.json').read_text())
definitions = capture.definitions(source)
cases = ['default', 'width-0', 'width-12', 'width-80', 'offer-0', 'offer-160', 'offer-800',
         'title-empty', 'title-long', 'title-lines', 'content-empty', 'content-zero', 'content-hidden',
         'content-wide', 'content-fills', 'content-multi', 'content-vstack', 'content-hstack',
         'content-counter', 'content-editor', 'disabled', 'rtl', 'rtl-narrow']
with tempfile.TemporaryDirectory(prefix='avelino-modal-catalog-') as temporary:
    directory = Path(temporary)
    inputs = directory / 'fixtures.json'
    inputs.write_text(json.dumps(definitions, ensure_ascii=False))
    environment = dict(os.environ, QML_IMPORT_PATH=str(imports), QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software', QT_SCALE_FACTOR='1')
    for index, name in enumerate(cases):
        row = next(row for row in definitions['fixtures'] if row['fixture'] == name)
        native = next(row for row in source['captures'] if row['configuration']['fixture'] == name
                      and row['appearance'] == 'light' and row['textScale'] == 1 and row['dpr'] == 1)
        image = directory / f'{index}.png'
        subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', name, '--case-definitions', str(inputs), '--capture', str(image)],
                       env=environment, check=True, capture_output=True, timeout=20)
        actual = json.loads(image.with_name(image.name + '.json').read_text())
        for field in ['title', 'modalWidth', 'content', 'disabled', 'rtl']:
            assert actual['rendered' + field[0].upper() + field[1:]] == row[field], (name, field)
        assert actual['componentSize'] == {key: native['witness']['parts']['root'][key] for key in ['width', 'height']}, (name, actual['componentSize'])
        assert actual['componentOrigin'] == {key: native['witness']['parts']['root'][key] for key in ['x', 'y']}, (name, actual['componentOrigin'])
        offered = row['modalWidth'] if row['outerOffer'] is None else row['outerOffer']
        assert actual['offeredFrameSize']['width'] == offered, (name, actual['offeredFrameSize'])
        for key, expected in native['witness']['parts'].items():
            assert actual['layoutWitnessRects'][key] == expected, (name, key, actual['layoutWitnessRects'][key], expected)
    default = next(row for row in definitions['fixtures'] if row['fixture'] == 'default')
    zero = next(row for row in definitions['fixtures'] if row['fixture'] == 'width-0')
    for index, forged in enumerate([dict(default, expectedEmpty=True), dict(zero, expectedEmpty=False), dict(default, modalWidth=-1)]):
        inputs.write_text(json.dumps({'fixtures': [forged]}))
        result = subprocess.run([str(catalog), '--fixture', 'reference-case', '--case', forged['fixture'], '--case-definitions', str(inputs),
                                '--capture', str(directory / f'forged-{index}.png')], env=environment, capture_output=True, timeout=20)
        assert result.returncode == 6, (forged, result.returncode, result.stderr)
print('Modal catalog: 23 public state/slot/geometry adapters and three malformed/forged-empty refusals passed')
