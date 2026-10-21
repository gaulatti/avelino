#!/usr/bin/env python3
"""Verify ordinary AdminShell colour inputs and raw renders without raster acceptance."""
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / 'evidence/development/admin-source-colour-fixture-20261020'
COLOUR_PRODUCER = '4a0a06bb2d183072a8d000c829b234d14c137a20'
# These recorded inputs have since evolved. Verify their captured bytes at the
# original producer; all other implementation inputs still bind to the index.
EVOLVED = {'src/Avelino/BleeckerAdminShell.qml', 'tests/components/tst_admin_shell.qml',
           'scripts/check-linux.sh'}


def source_bytes(name):
    if name in EVOLVED:
        return subprocess.check_output(['git', 'show', COLOUR_PRODUCER + ':' + name], cwd=ROOT)
    return (ROOT / name).read_bytes()


def read(name):
    return json.loads((CAP / name).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify():
    files = read('files.json'); implementation = read('implementation-inputs.json')
    assert set(files) == {str(p.relative_to(CAP)) for p in CAP.rglob('*') if p.is_file() and p != CAP / 'files.json'}
    relative = CAP.relative_to(ROOT)
    members = sorted({str(relative / name) for name in files} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(members), 'Every colour-fixture capsule member must be in the Git index'
    names = members + sorted(implementation)
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
        input=('\n'.join(COLOUR_PRODUCER + ':' + name if name in EVOLVED else ':' + name for name in names) + '\n').encode(), stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(result.stdout)
    for name in names:
        header = stream.readline().split(); assert len(header) == 3 and header[1] == b'blob', name
        raw = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        assert raw == source_bytes(name), name
        if name in implementation:
            assert sha(raw) == implementation[name]
        elif name != str(relative / 'files.json'):
            assert sha(raw) == files[str(Path(name).relative_to(relative))]
    assert not stream.read()
    scope = read('scope.json')
    assert scope['sourceUncommittedAtCapture'] and scope['sourceColourInputsIntegrated'] and scope['standardSrgbTransferOnly']
    assert scope['scaleFactors'] == [1, 2]
    assert (scope['componentTestsPerScale'], scope['captureTestsPerScale'], scope['rawCapturesPerScale']) == (265, 82, 80)
    assert scope['rawCaptureAliases'] == 160 and scope['visibleCallerPixelSamplesPerScale'] == 158
    for key in ['freshModuleCompilation', 'newInstalledConsumerExecuted', 'nativeRasterAccepted',
                'iccConversionReviewed', 'physicalInput', 'readerAcceptance', 'fullDisplayMatrixPassed', 'accepted']:
        assert scope[key] is False
    binding = read('source-binding.json')
    native = (ROOT / binding['nativeInputPath']).read_bytes()
    assert native == (CAP / 'native-inputs.json').read_bytes() and sha(native) == binding['nativeInputSha256']
    assert json.loads(native)['reference'] == binding['reference']
    historical = subprocess.check_output(['git', 'show', binding['comparatorSourceRevision'] + ':' + binding['comparatorPath']], cwd=ROOT)
    assert sha(historical) == binding['comparatorSha256'] == sha((ROOT / binding['comparatorPath']).read_bytes())
    assert binding['iccConversionPerformed'] is binding['expectedImagesChanged'] is binding['sourcePinsChanged'] is binding['accepted'] is False
    subprocess.run([sys.executable, str(ROOT / 'scripts/generate-admin-shell-colours.py'), '--check'], check=True)
    text = (ROOT / 'tests/consumer/native-admin-shell-colours.js').read_text()
    inputs = json.loads(re.search(r'var environments = (\{.*\});\s*$', text, re.S).group(1))
    for name in ['tests/consumer/CMakeLists.txt', 'samples/AvelinoCatalog/CMakeLists.txt']:
        assert (ROOT / name).read_text().count('native-admin-shell-colours.js') == 1
    base = read('base-module.json')
    published = json.loads((ROOT / 'evidence/development/admin-shell-sessions-20261020/inputs.json').read_text())
    assert base['sha256'] == published['librarySha256'] and base['newQmlInterpreted'] and base['moduleReused']
    assert base['freshCompilation'] is base['accepted'] is False
    failure = read('runtime/inspection-failure-v1.json')
    assert failure['exitCode'] == 1 and failure['resultTrusted'] is failure['accepted'] is False
    assert failure['runtimeCaptureRunsUnaffected'] and failure['controllerSha256'] == sha((CAP / 'runtime/inspect-failed.py.txt').read_bytes())
    inspection = read('runtime/inspection-v2.json')
    assert inspection['exitCode'] == 0 and inspection['accepted'] is False
    assert inspection['controllerSha256'] == sha((CAP / 'runtime/check-renders.py').read_bytes())
    images = read('images.json'); dimensions = {}
    assert len(images) == 160
    for stored in {entry['stored'] for entry in images.values()}:
        raw = (CAP / stored).read_bytes(); assert sha(raw) == Path(stored).stem
        with Image.open(io.BytesIO(raw)) as image:
            image.load(); assert image.format == 'PNG' and 'icc_profile' not in image.info
            dimensions[stored] = image.size
    assert set(dimensions) == {str(p.relative_to(CAP)) for p in (CAP / 'images').glob('*.png')}
    native_profiles = json.loads((ROOT / 'tests/consumer/native-admin-shell-witnesses.json').read_text())['profiles']
    profiles = {row['name']:row for row in native_profiles}
    samples = []
    for scale in [1, 2]:
        receipt = read(f'runtime/run-v{scale}.json')
        assert receipt['exitCode'] == 0 and receipt['freshCompilation'] is receipt['accepted'] is False
        assert f'QT_SCALE_FACTOR={scale}' in receipt['command']
        assert '265 passed, 0 failed' in (CAP / f'runtime/run-v{scale}.log').read_text()
        original = {name:(CAP / f'runtime/inputs-v{scale}' / name).read_bytes() for name in receipt['sourceInputHashes']}
        assert {name:sha(raw) for name,raw in original.items()} == receipt['sourceInputHashes']
        assert all(source_bytes(name) == raw for name,raw in original.items())
        payload = dict(original)
        payload['tests/components/witnesses.js'] = b'var data = ' + original['tests/consumer/native-admin-shell-witnesses.json'] + b';\n'
        name = 'tests/components/tst_admin_shell.qml'
        source = payload[name].decode().replace('import QtTest', 'import QtTest\nimport "witnesses.js" as Native', 1)
        payload[name] = source.replace('    id: root', '    id: root\n    property var nativeAdminShellWitnesses: Native.data', 1).encode()
        assert {name:sha(raw) for name,raw in payload.items()} == receipt['executedPayloadHashes']
        capture = read(f'runtime/capture-dpr{scale}.json')
        assert capture['exitCode'] == 0 and capture['scaleFactor'] == scale and capture['sourceColourInputsIntegrated']
        assert capture['freshCompilation'] is capture['nativeRasterAccepted'] is capture['accepted'] is False
        log = (CAP / f'runtime/capture-dpr{scale}.log').read_text()
        assert '82 passed, 0 failed' in log
        observed = [json.loads(line.split('SOURCE_COLOUR ', 1)[1]) for line in log.splitlines() if 'SOURCE_COLOUR ' in line]
        assert observed == capture['observations'] and {row['name'] for row in observed} == set(profiles)
        for name,digest in capture['sourceInputHashes'].items():
            assert sha(source_bytes(name)) == digest
        for name,digest in capture['executedPayloadHashes'].items():
            assert sha((CAP / f'runtime/capture-inputs-dpr{scale}' / name).read_bytes()) == digest
        for row in observed:
            expected = profiles[row['name']]['state']; actual = row['state']
            assert all(actual[key] == value for key,value in expected.items() if key != 'step')
            logical = f'dpr{scale}/' + row['name'] + '.png'; entry = images[logical]
            raw = (CAP / entry['stored']).read_bytes()
            assert sha(raw) == entry['sha256'] == capture['rawCaptures'][row['name'] + '.png'] and len(raw) == entry['bytes']
            assert dimensions[entry['stored']] == (row['width'] * scale, row['height'] * scale)
            theme = 'dark' if row['dark'] else 'light'
            image = Image.open(io.BytesIO(raw)).convert('RGBA')
            for role, colour in row['colours'].items():
                value = inputs[theme][role]['encodedSRGB']
                assert [round(v * 65535) for v in colour] == [round(v * 65535) for v in value]
                if role == 'root' or (role == 'sidebar' and not actual['displayedNavigation']):
                    continue
                frame = actual['frames'][role]
                x0 = math.ceil(max(0, frame['x']) * scale); y0 = math.ceil(max(0, frame['y']) * scale)
                x1 = math.floor(min(row['width'], frame['x'] + frame['width']) * scale)
                y1 = math.floor(min(row['height'], frame['y'] + frame['height']) * scale)
                if x1 <= x0 or y1 <= y0:
                    continue
                x = x0 + (x1 - x0) // 2; y = y0 + (y1 - y0) // 2
                expected_pixel = [round(v * 255) for v in colour]; pixel = list(image.getpixel((x,y)))
                assert pixel == expected_pixel
                samples.append(dict(scale=scale, name=row['name'], role=role, x=x, y=y,
                                    expectedRGBA=expected_pixel, actualRGBA=pixel))
    render = read('runtime/render-check.json')
    assert render['checks'] == samples and render['mismatches'] == [] and render['pixelSamplesPerScale'] == {'1':158, '2':158}
    assert render['nativeRasterAccepted'] is render['comparisonPolicyChanged'] is render['accepted'] is False
    print('Admin source-colour fixture: 265 tests per DPR, 160 raw captures and 316 exact input pixels; native material/profile acceptance pending')


if __name__ == '__main__':
    verify()
