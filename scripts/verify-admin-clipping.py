#!/usr/bin/env python3
"""Check native split containment and the Linux paint regression, without parity approval."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / 'evidence/development/admin-shell-clipping-20261020'
OBSERVED_TEST = 'tests/components/tst_admin_shell.qml'
OBSERVED_PRODUCER = '7253695c3e94b0626bcb0612fbc8467fe94445b5'


def read(name):
    return json.loads((CAP / name).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_bytes(expression):
    return subprocess.check_output(['git', 'show', expression], cwd=ROOT)


def source_bytes(name):
    return git_bytes(OBSERVED_PRODUCER + ':' + name) if name == OBSERVED_TEST else (ROOT / name).read_bytes()


def verify():
    files, implementation = read('files.json'), read('implementation-inputs.json')
    assert set(files) == {str(p.relative_to(CAP)) for p in CAP.rglob('*') if p.is_file() and p.name != 'files.json'}
    relative = CAP.relative_to(ROOT)
    members = {str(relative / n) for n in files} | {str(relative / 'files.json')}
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == members, 'Every clipping capsule member must be in the Git index'
    names = sorted(members | set(implementation))
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT, check=True,
                            input=('\n'.join(OBSERVED_PRODUCER + ':' + n if n == OBSERVED_TEST else ':' + n for n in names) + '\n').encode(), stdout=subprocess.PIPE)
    stream = io.BytesIO(result.stdout)
    for name in names:
        header = stream.readline().split()
        assert len(header) == 3 and header[1] == b'blob', 'Required staged clipping input missing: ' + name
        raw = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        assert raw == source_bytes(name), name
        if name in implementation:
            assert sha(raw) == implementation[name], name
        elif name != str(relative / 'files.json'):
            assert sha(raw) == files[str(Path(name).relative_to(relative))], name
    assert not stream.read()
    scope = read('scope.json')
    assert scope['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert scope['sourceUncommittedAtCapture'] and scope['sourceSplitClippingIntegrated']
    assert scope['componentTestsPerScale'] == 266 and scope['scaleFactors'] == [1, 2]
    assert scope['nativeOriginalControlPaths'] == scope['nativeOriginalControlsByteIdentical'] == 12
    for key in ['freshModuleCompilation', 'newInstalledConsumerExecuted', 'newDisplayMatrixExecuted',
                'nativeRasterAccepted', 'iccConversionReviewed', 'physicalInput', 'readerAcceptance',
                'independentMachineReplay', 'accepted']:
        assert scope[key] is False
    images = read('images.json'); dimensions = {}
    assert len(images) == scope['rawImageAliases']
    for stored in {r['stored'] for r in images.values()}:
        path = CAP / stored
        assert path.parent == CAP / 'images' and sha(path.read_bytes()) == path.stem
        with Image.open(path) as image:
            image.load(); assert image.format == 'PNG'; dimensions[stored] = image.size
    assert len(dimensions) == scope['uniquePngBlobs']
    assert set(dimensions) == {str(p.relative_to(CAP)) for p in (CAP / 'images').glob('*.png')}
    for name, row in images.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert row['sha256'] == Path(row['stored']).stem and row['bytes'] == (CAP / row['stored']).stat().st_size
    native = read('native/observations.json'); source = read('native/inputs.json')
    assert native['reference'] == source['reference'] == scope['reference']
    assert source['sourceCallerOverflowDiagnostic'] and source['sourceLibraryChanged'] is False
    assert source['libraryObjectSha256'] == '0d98b215928f864cb6874be5426360db0861eb44a049af40e556aca9e319c025'
    assert len(source['resourceBundleFiles']) == 27
    assert read('native/compile-command.json')['exitCode'] == read('native/capture-command.json')['exitCode'] == 0
    assert read('native/helper-locator.json')['helperSha256'] == source['helperSha256']
    parent = json.loads(git_bytes(scope['baseSourceRevision'] + ':evidence/reference-investigations/admin-shell-materials-20261020/images.json'))
    assert len(native['records']) == 4
    for context in native['records']:
        for key in ['before', 'after', 'chrome']:
            capture = context['state'][key]; name = capture['path']
            assert images['native/' + name]['sha256'] == capture['sha256'] == parent['v3/' + name]['sha256']
    probes = native['overflowClipProbes']; assert len(probes) == 2
    assert [r['paintOverflow'] for r in probes] == [False, True]
    for row in probes:
        split = next(v for v in row['state']['nativeHierarchy'] if v['class'] == 'NSSplitView')
        assert split['hostFrame'] == {'x':30, 'y':30, 'width':360, 'height':180}
        assert split['layer']['masksToBounds'] is True
        for key in ['before', 'after', 'chrome']:
            capture = row['state'][key]
            assert images['native/' + capture['path']]['sha256'] == capture['sha256']
    def image(alias):
        return Image.open(CAP / images[alias]['stored']).convert('RGBA')
    before = image('native/' + probes[0]['state']['before']['path'])
    after = image('native/' + probes[1]['state']['before']['path'])
    assert before.size == after.size == (840, 480)
    bounds = ImageChops.difference(before.convert('RGB'), after.convert('RGB')).getbbox()
    assert bounds and bounds[0] >= 60 and bounds[1] >= 60 and bounds[2] <= 780 and bounds[3] <= 420
    assert ImageChops.difference(before.getchannel('A'), after.getchannel('A')).getbbox() is None
    assert list(bounds) == read('native/clipping-audit.json')['changedBounds']
    assert read('failed-bundle/compile-command.json')['exitCode'] == 0
    assert read('failed-bundle/capture-command.json')['exitCode'] == -5
    assert 'unable to find bundle named Sabella_Sabella' in (CAP / 'failed-bundle/capture.log').read_text()
    invalid = read('runtime/invalid-dpr2-test-v2.json')
    assert invalid['validAsClippingFailure'] is invalid['accepted'] is False
    for number, scale, successful in [(5, 1, True), (6, 2, False), (7, 2, True)]:
        receipt = read(f'runtime/run-v{number}.json')
        assert receipt['exitCode'] == (0 if successful else 1)
        assert receipt['freshCompilation'] is receipt['accepted'] is False
        assert f'QT_SCALE_FACTOR={scale}' in receipt['command']
        log = (CAP / f'runtime/run-v{number}.log').read_text()
        assert ('266 passed, 0 failed' if successful else '265 passed, 1 failed') in log
        original = {n:(CAP / f'runtime/inputs-v{number}' / n).read_bytes() for n in receipt['sourceInputHashes']}
        assert {n:sha(raw) for n, raw in original.items()} == receipt['sourceInputHashes']
        for name, raw in original.items():
            expected = git_bytes(scope['baseSourceRevision'] + ':' + name) if not successful and name == 'src/Avelino/BleeckerAdminShell.qml' else source_bytes(name)
            assert raw == expected, (number, name)
        payload = dict(original)
        payload['tests/components/witnesses.js'] = b'var data = ' + original['tests/consumer/native-admin-shell-witnesses.json'] + b';\n'
        name = 'tests/components/tst_admin_shell.qml'
        text = payload[name].decode().replace('import QtTest', 'import QtTest\nimport "witnesses.js" as Native', 1)
        text = text.replace('    id: root', '    id: root\n    property var nativeAdminShellWitnesses: Native.data', 1)
        text = text.replace('            const after = grabImage(host)', '            const after = grabImage(host)\n            before.save("/evidence/before-v' + str(number) + '.png"); after.save("/evidence/after-v' + str(number) + '.png")', 1)
        payload[name] = text.encode()
        assert {n:sha(raw) for n, raw in payload.items()} == receipt['executedPayloadHashes']
        a, b = image(f'runtime/before-v{number}.png'), image(f'runtime/after-v{number}.png')
        for x, y in ([[10, 10], [15, 100], [405, 100], [210, 230]] if successful else [[10, 10]]):
            point = (x * scale, y * scale)
            assert (a.getpixel(point) == b.getpixel(point)) is successful
    print('Admin split clipping: native margin preserved, original controls identical, prior Linux failure retained and 266 cases at both scales; compiled/package/native acceptance pending')


if __name__ == '__main__':
    verify()
