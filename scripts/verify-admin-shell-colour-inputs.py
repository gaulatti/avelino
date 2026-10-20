#!/usr/bin/env python3
"""Verify resolved source inputs without accepting Linux pixels or changing references."""
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/reference-investigations/admin-shell-colour-inputs-20261020'
PARENT = ROOT / 'evidence/reference-investigations/admin-shell-pinned-matrix-20261020'


def read(name):
    return json.loads((CAPSULE / name).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify():
    files = read('files.json')
    assert set(files) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p.name != 'files.json'}
    relative = CAPSULE.relative_to(ROOT)
    names = sorted({str(relative / n) for n in files} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(names), 'Every colour capsule member must be in the Git index'
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                            input=('\n'.join(':' + n for n in names) + '\n').encode(), stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(result.stdout)
    for name in names:
        header = stream.readline().split(); assert len(header) == 3 and header[1] == b'blob'
        content = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        assert content == (ROOT / name).read_bytes()
        if name != str(relative / 'files.json'):
            assert sha(content) == files[str(Path(name).relative_to(relative))]
    assert not stream.read()

    inputs, observations, scope = read('probe-inputs.json'), read('observations.json'), read('scope.json')
    parent_inputs = json.loads((PARENT / 'inputs.json').read_text())
    assert inputs['parentInputsSha256'] == sha((PARENT / 'inputs.json').read_bytes())
    assert inputs['parentHelperSha256'] == parent_inputs['helperSha256']
    assert inputs['objectSha256'] == parent_inputs['libraryObjectSha256']
    assert inputs['captureProfileSha256'] == parent_inputs['captureProfileSha256']
    assert inputs['reference'] == observations['reference'] == scope['reference'] == parent_inputs['reference']
    assert inputs['libraryRebuilt'] is observations['libraryRebuilt'] is scope['independentLibraryRebuild'] is False
    assert inputs['accepted'] is observations['accepted'] is False
    for key in ['inputsIntegratedIntoLinuxFixtures', 'nativeRasterAccepted', 'physicalInput', 'readerAcceptance', 'accepted']:
        assert scope[key] is False
    assert (scope['fixtures'], scope['themes'], scope['visibilityValues'], scope['observedStates']) == (1, 2, 2, 4)
    assert scope['originalControlImages'] == scope['byteIdenticalControlImages'] == 12
    assert scope['unchangedGeometryAndCallbacks'] is True
    command = read('compile-command.json')
    assert command['exitCode'] == read('capture-command.json')['exitCode'] == 0
    expected_command = json.loads((PARENT / 'compile-command.json').read_text())['command']
    helper_index = next(i for i, value in enumerate(expected_command) if value.endswith('/ShellHost.swift'))
    executable_index = expected_command.index('-o') + 1
    expected_command[helper_index] = command['command'][helper_index]
    expected_command[executable_index] = command['command'][executable_index]
    assert command['command'] == expected_command
    assert expected_command[helper_index].endswith('/ShellInputs.swift')
    assert read('capture-command.json')['command'][0] == expected_command[executable_index]

    images, dimensions = read('images.json'), {}
    parent_images = json.loads((PARENT / 'images.json').read_text())
    assert len(images) == 12
    for stored in {row['stored'] for row in images.values()}:
        path = CAPSULE / stored
        assert path.parent == CAPSULE / 'images' and sha(path.read_bytes()) == path.stem
        with Image.open(path) as image:
            image.load(); assert image.format == 'PNG'
            assert sha(image.info['icc_profile']) == inputs['captureProfileSha256']
            dimensions[stored] = image.size
    assert set(dimensions) == {str(p.relative_to(CAPSULE)) for p in (CAPSULE / 'images').glob('*.png')}
    for name, row in images.items():
        assert row['sha256'] == Path(row['stored']).stem == parent_images[name]['sha256']
        raw = (CAPSULE / row['stored']).read_bytes()
        assert raw == (PARENT / parent_images[name]['stored']).read_bytes() and len(raw) == row['bytes']

    audit = read('audit.json')
    assert audit['all12ControlsByteIdentical'] is True and audit['accepted'] is False
    assert len(audit['controls']) == 12
    for row in audit['controls']:
        assert row['identical'] is True and row['newSha256'] == row['oldSha256'] == images[row['path']]['sha256']
    projection = read('resolved-inputs.json')
    assert projection['reference'] == inputs['reference'] and projection['accepted'] is False
    parent = json.loads((PARENT / 'measurements.json').read_text())
    records = observations['records']; assert len(records) == 4
    assert {(r['dark'], r['initial']) for r in records} == {(False, False), (False, True), (True, False), (True, True)}
    expected_images = set()
    for row in records:
        original = next(r for r in parent['profiles'] if r['case'] == 'standard' and r['dark'] == row['dark']
                        and r['initial'] == row['initial'] and r['measured'])
        for key in ['requests', 'navigation', 'pending', 'bodyFramesFromGlobal', 'lastLayoutFrames', 'arrangedSubviews']:
            assert row['state'][key] == original['state'][key]
        for kind in ['before', 'after', 'chrome']:
            capture = row['state'][kind]; expected_images.add(capture['path'])
            assert images[capture['path']]['sha256'] == capture['sha256'] == original['state'][kind]['sha256']
            assert dimensions[images[capture['path']]['stored']] == (capture['width'], capture['height'])
        colors = row['resolvedInputs']; assert set(colors) == {'sidebar', 'header', 'content', 'root'}
        theme = 'dark' if row['dark'] else 'light'
        assert colors == projection['environments'][theme]
        for color in colors.values():
            values = color['linearSRGB']; bits = color['float32Bits']
            assert len(values) == len(bits) == 4 and all(math.isfinite(x) for x in values)
            assert [struct.unpack('>f', bytes.fromhex(value))[0] for value in bits] == values
            assert values[3] == 1 and color['colorScheme'] == theme
            assert color['colorSchemeContrast'] == 'standard' and color['controlActiveState'] == 'inactive'
            assert color['displayScale'] == 2
        assert colors['root']['linearSRGB'] == [1, 1, 1, 1]
    assert expected_images == set(images)
    light, dark = (projection['environments'][theme] for theme in ['light', 'dark'])
    for role, pure in [('sidebar', [0, 1, 0, 1]), ('header', [1, 0, 0, 1]), ('content', [0, 0, 1, 1])]:
        assert light[role]['linearSRGB'] != dark[role]['linearSRGB']
        assert light[role]['linearSRGB'] != pure and dark[role]['linearSRGB'] != pure
    print('AdminShell source colour inputs: 4 actual environments; 12 controls byte-identical; Linux input bridge and raster acceptance pending')


if __name__ == '__main__':
    verify()
