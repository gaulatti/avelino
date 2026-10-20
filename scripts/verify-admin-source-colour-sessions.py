#!/usr/bin/env python3
"""Verify the source-colour installed display matrix; native gates remain open."""
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/admin-source-colour-sessions-20261020'
PACKAGE = 'evidence/development/admin-source-colour-package-20261020'


def read(name):
    return json.loads((CAPSULE / name).read_text())


def sha(content):
    return hashlib.sha256(content).hexdigest()


def historical(revision, name):
    return subprocess.check_output(['git', 'show', revision + ':' + name], cwd=ROOT)


def verify():
    files = read('files.json')
    actual = {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p != CAPSULE / 'files.json'}
    assert set(files) == actual
    relative = CAPSULE.relative_to(ROOT)
    names = sorted({str(relative / n) for n in files} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(names), 'Every source-colour session capsule member must be in the Git index'
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                            input=('\n'.join(':' + n for n in names) + '\n').encode(), stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(result.stdout)
    for name in names:
        header = stream.readline().split(); assert len(header) == 3 and header[1] == b'blob'
        content = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        assert content == (ROOT / name).read_bytes(), name
        if name != str(relative / 'files.json'):
            assert sha(content) == files[str(Path(name).relative_to(relative))], name
    assert not stream.read()
    execution, inputs, scope = read('result.json'), read('inputs.json'), read('scope.json')
    assert execution['exitCode'] == 0 and execution['binariesUnchangedSinceLaunch']
    assert execution['sourceProjectsMounted'] is execution['productBuildMounted'] is execution['accepted'] is False
    assert inputs['sourceProjectsMounted'] is inputs['productBuildMounted'] is inputs['physicalDisplay'] is inputs['hardwareAcceleration'] is inputs['accepted'] is False
    command = execution['command']
    assert command[:6] == ['docker', '--context', 'colima-avelino-verify', 'run', '--init', '--rm']
    assert command.count('-v') == 1 and command[command.index('-v') + 1].endswith('/admin-source-colour-compiled-v1/output/package:/package')
    assert 'test ! -e /work/src; test ! -e /work/CMakeLists.txt;' in command[-1]
    assert command[-1].endswith('exec bash check-admin-source-colour-sessions-v1.sh /package/admin-source-colour-sessions-v1')
    assert read('output/environment.json') == inputs
    audit = read('artifact-audit.json')
    assert audit['sourceRevision'] == inputs['sourceRevision'] and audit['unchangedSinceSessionLaunch']
    assert audit['binaryPayloadsStored'] is audit['accepted'] is False
    assert audit['files'] == {'consumer-build/InstalledConsumer': inputs['consumerSha256'],
                              'install/lib/qml/Avelino/libAvelino.so': inputs['librarySha256']}
    producer = scope['packageEvidenceRevision']
    package_scope = json.loads(historical(producer, PACKAGE + '/scope.json'))
    artifacts = json.loads(historical(producer, PACKAGE + '/compiled/artifacts.json'))
    build_inputs = json.loads(historical(producer, PACKAGE + '/compiled/inputs.json'))
    assert command[-4] == build_inputs['imageId']
    assert package_scope['sourceRevision'] == inputs['sourceRevision'] == scope['sourceRevision']
    assert package_scope['compiledAdminTestsPerScale'] == 265 and package_scope['offscreenPackageContexts'] == 4
    assert package_scope['allBodiesByteIdenticalToInterpretedSourceColourFixture'] and package_scope['accepted'] is False
    assert all(artifacts[k] == inputs[k] for k in ['consumerSha256', 'librarySha256'])
    canonical = (CAPSULE / 'canonical.sh').read_bytes()
    assert sha(canonical) == inputs['canonicalSessionScriptSha256']
    assert canonical == historical(inputs['sourceRevision'], 'scripts/check-display-sessions.sh')
    filtered, count = re.subn(r'for fixture in [^\n]+; do', 'for fixture in admin-shell; do', canonical.decode(), count=1)
    assert count == 1 and filtered.encode() == (CAPSULE / 'filtered.sh').read_bytes()
    assert sha(filtered.encode()) == inputs['filteredSessionScriptSha256']
    assert (CAPSULE / 'executed.sh').read_bytes() == filtered.encode()
    assert audit['executedScriptSha256'] == inputs['filteredSessionScriptSha256']
    assert scope['contexts'] == scope['completeSessionContexts'] == scope['structuralContextsPassed'] == 8
    assert scope['rawBodyCaptures'] == 640 and scope['windowCaptures'] == scope['compositorCaptures'] == 8
    for key in ['sourceProjectsMounted', 'productBuildMounted', 'nativeRasterAccepted',
                'nativeToolbarEquivalentVerified', 'nativeKeyboardEquivalentVerified', 'iccConversionReviewed',
                'physicalDisplay', 'hardwareAcceleration', 'physicalInput', 'readerAcceptance', 'accepted']:
        assert scope[key] is False
    index = read('images.json'); dimensions = {}
    for stored in {r['stored'] for r in index.values()}:
        path = CAPSULE / stored
        assert path.parent == CAPSULE / 'images' and sha(path.read_bytes()) == path.stem
        with Image.open(path) as image:
            image.load(); assert image.format == 'PNG'; dimensions[stored] = image.size
    assert set(dimensions) == {str(p.relative_to(CAPSULE)) for p in (CAPSULE / 'images').glob('*.png')}
    assert scope['uniquePngBlobs'] == len(dimensions)
    for logical, row in index.items():
        assert not Path(logical).is_absolute() and '..' not in Path(logical).parts
        assert row['sha256'] == Path(row['stored']).stem and row['bytes'] == (CAPSULE / row['stored']).stat().st_size
    native = json.loads(historical(inputs['sourceRevision'], 'tests/consumer/native-admin-shell-witnesses.json'))
    profiles = {r['name']: r for r in native['profiles']}
    expected_images = set()
    for protocol, backend, configuration in itertools.product(['xcb', 'wayland'], ['software', 'opengl'], ['standard', 'scaled']):
        prefix = f'admin-shell-{protocol}-{backend}-{configuration}'
        row = read('output/' + prefix + '.json')
        if backend == 'opengl':
            assert 'Mesa RENDERER: llvmpipe' in (CAPSULE / 'output' / (prefix + '.log')).read_text()
        scale = 1 if configuration == 'standard' else 2
        assert row['platform'] == protocol and row['graphicsApi'] == (1 if backend == 'software' else 3)
        assert row['dpr'] == scale and row['textScale'] == (1 if scale == 1 else 1.5)
        assert row['appearance'] == ('light' if scale == 1 else 'dark')
        assert row['fixture'] == 'admin-shell' and row['structuralChecks'] == 'passed'
        assert row['reference'] == native['reference'] and row['qt'] == '6.8.3'
        assert row['nativeLayouts'] == len(row['layouts']) == 80
        assert {r['name'] for r in row['layouts']} == set(profiles)
        assert row['nativeHistoryStates'] == sum(len(h['states']) for h in row['histories']) == 160
        assert row['nativeDividerCases'] == len(row['boundaries']) == 168
        assert row['qtCallerIdentityRetained'] and row['qtKeyboardActivation'] and row['qtShortcutActivation']
        assert row['qtToolbarPointerActions'] == 4 and row['qtAccessibilityInterfaces'] == 2
        for key in ['nativeToolbarEquivalentVerified', 'nativeKeyboardEquivalentVerified', 'nativeRasterAccepted',
                    'physicalInput', 'physicalDisplay', 'readerAcceptance', 'hardwareAcceleration', 'accepted']:
            assert row[key] is False
        screen_name = prefix + '-session.png'; screen = index[screen_name]
        expected_images.add(screen_name); assert dimensions[screen['stored']] == (2560, 1920)
        window_name = prefix + '.png'; window = index[window_name]; expected_images.add(window_name)
        assert row['sessionCapture'] == screen_name
        assert window['sha256'] == row['windowCaptureSha256'] and screen['sha256'] == row['sessionCaptureSha256']
        assert dimensions[window['stored']] == (row['width'] * scale, row['height'] * scale)
        assert (CAPSULE / 'output' / (prefix + '.captured')).is_file()
        for layout in row['layouts']:
            expected = profiles[layout['name']]['state']
            assert all(layout[k] == v for k, v in expected.items() if k != 'step')
            image = index[layout['capture']]; expected_images.add(layout['capture'])
            assert dimensions[image['stored']] == (layout['pixelWidth'], layout['pixelHeight'])
        for actual, expected in zip(row['histories'], native['histories'], strict=True):
            assert actual['owner'] == expected['owner'] and actual['initial'] == expected['initial']
            assert actual['states'] == expected['states']
        for actual, expected in zip(row['boundaries'], native['boundaries'], strict=True):
            assert all(actual[k] == expected[k] for k in ['columnWidth', 'initial', 'requestedPosition'])
            state = actual['actual']; pane = expected['after'][0]
            assert state['columnWidth'] == pane['width'] and state['displayedNavigation'] == (not pane['collapsed'])
            assert state['navigation'] == expected['navigation'] and state['requests'] == expected['requests']
    assert len(expected_images) == len(index) == 656 and set(index) == expected_images
    review = read('visual-review.json')
    assert review['sourceRevision'] == inputs['sourceRevision']
    assert len(review['reviewedWindowCaptures']) == 2
    for name, checksum in review['reviewedWindowCaptures'].items():
        assert name in index and checksum == index[name]['sha256']
    for key in ['nativeReferenceComparedInThisReview', 'nativeRasterAccepted', 'physicalInput', 'readerAcceptance', 'accepted']:
        assert review[key] is False
    assert (CAPSULE / 'output/weston-version.txt').read_text().strip() == 'weston 13.0.4'
    pointer = dict(line.split('=', 1) for line in (CAPSULE / 'output/native-pointer.txt').read_text().splitlines())
    assert (pointer['X'], pointer['Y'], pointer['SCREEN']) == ('2559', '1919', '0')
    print('Source-colour package: eight X11/Wayland, software/OpenGL and scale contexts verified; native raster, physical input and reader acceptance pending')


if __name__ == '__main__':
    verify()
