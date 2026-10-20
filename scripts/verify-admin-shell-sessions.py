#!/usr/bin/env python3
"""Check installed AdminShell session evidence; physical/native gates stay open."""
import argparse
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/admin-shell-sessions-20261020'


def read(name):
    return json.loads((CAPSULE / name).read_text())


def sha(content):
    return hashlib.sha256(content).hexdigest()


def verify(failed=False):
    files = read('files.json')
    assert set(files) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p != CAPSULE / 'files.json'}
    relative = CAPSULE.relative_to(ROOT)
    names = sorted({str(relative / n) for n in files} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(names), 'Every session capsule member must be in the Git index'
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
    execution, inputs = read('result.json'), read('inputs.json')
    assert execution['exitCode'] == (1 if failed else 0)
    assert not execution['sourceProjectsMounted'] and not execution['productBuildMounted']
    if failed:
        failure_log = (CAPSULE / 'sessions.log').read_text()
        assert 'FileNotFoundError' in failure_log and "admin-shell-wayland-opengl-scaled.png'" in failure_log
    assert inputs['sourceProjectsMounted'] is inputs['productBuildMounted'] is inputs['physicalDisplay'] is inputs['hardwareAcceleration'] is inputs['accepted'] is False
    command = execution['command']
    assert command[:6] == ['docker', '--context', 'colima-avelino-verify', 'run', '--init', '--rm']
    assert command.count('-v') == 1 and command[command.index('-v') + 1].endswith('/output/package:/package')
    assert 'test ! -e /work/src; test ! -e /work/CMakeLists.txt;' in command[-1]
    assert read('output/environment.json') == inputs
    artifact_audit = read('artifact-audit.json')
    assert artifact_audit['sourceRevision'] == inputs['sourceRevision']
    assert artifact_audit['unchangedSinceSessionLaunch'] is True
    assert artifact_audit['binaryPayloadsStored'] is artifact_audit['accepted'] is False
    assert artifact_audit['files'] == {
        'consumer-build/InstalledConsumer': inputs['consumerSha256'],
        'install/lib/qml/Avelino/libAvelino.so': inputs['librarySha256'],
    }
    if not failed:
        build = read('readiness-build-v5/result.json')
        assert build['sourceRevision'] == inputs['sourceRevision'] and build['exitCode'] == 0
        assert build['sourceInputsUnchanged'] and build['coreLibrariesUnchanged'] and build['consumerBuildPassed']
        assert build['installedConsumerExecuted'] is build['accepted'] is False
        artifacts = read('readiness-build-v5/artifacts.json')
        assert artifacts == {k: inputs[k] for k in ['consumerSha256', 'librarySha256', 'accepted']}
        build_inputs = read('readiness-build-v5/inputs.json')
        assert build_inputs['sourceRevision'] == inputs['sourceRevision']
        assert build_inputs['coreLibraryChanged'] is build_inputs['accepted'] is False
        for name, digest in build_inputs['sourceFiles'].items():
            content = subprocess.check_output(['git', 'show', inputs['sourceRevision'] + ':' + name], cwd=ROOT)
            assert sha(content) == digest
        assert read('readiness-build-v5/command.json')['exitCode'] == 0
    canonical = (CAPSULE / 'canonical.sh').read_bytes()
    assert sha(canonical) == inputs['canonicalSessionScriptSha256']
    historical = subprocess.check_output(['git', 'show', inputs['sourceRevision'] + ':scripts/check-display-sessions.sh'], cwd=ROOT)
    assert canonical == historical
    filtered, count = re.subn(r'for fixture in [^\n]+; do', 'for fixture in admin-shell; do', canonical.decode(), count=1)
    assert count == 1 and filtered.encode() == (CAPSULE / 'filtered.sh').read_bytes()
    assert sha(filtered.encode()) == inputs['filteredSessionScriptSha256']
    index = read('images.json'); dimensions = {}
    scope = read('scope.json')
    assert scope['sourceRevision'] == inputs['sourceRevision'] and scope['contexts'] == 8
    assert scope['rawBodyCaptures'] == 640 and scope['windowCaptures'] == (7 if failed else 8)
    assert scope['compositorCaptures'] == 8
    for key in ['sourceProjectsMounted', 'productBuildMounted', 'nativeRasterAccepted',
                'nativeToolbarEquivalentVerified', 'nativeKeyboardEquivalentVerified',
                'physicalDisplay', 'hardwareAcceleration', 'physicalInput', 'readerAcceptance', 'accepted']:
        assert scope[key] is False
    if failed:
        assert scope['completeSessionContexts'] == 7 and scope['structuralContextsPassed'] == 8
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
    native = json.loads(subprocess.check_output(['git', 'show', inputs['sourceRevision'] + ':tests/consumer/native-admin-shell-witnesses.json'], cwd=ROOT))
    profiles = {r['name']: r for r in native['profiles']}
    expected_images = set()
    records = []
    for protocol, backend, configuration in itertools.product(['xcb', 'wayland'], ['software', 'opengl'], ['standard', 'scaled']):
        prefix = f'admin-shell-{protocol}-{backend}-{configuration}'
        row = read('output/' + prefix + '.json'); records.append(row)
        incomplete = failed and (protocol, backend, configuration) == ('wayland', 'opengl', 'scaled')
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
        assert row['qtToolbarPointerActions'] == 4
        assert row['qtAccessibilityInterfaces'] == 2
        for key in ['nativeToolbarEquivalentVerified', 'nativeKeyboardEquivalentVerified', 'nativeRasterAccepted',
                    'physicalInput', 'physicalDisplay', 'readerAcceptance', 'accepted']:
            assert row[key] is False
        screen_name = prefix + '-session.png'
        screen = index[screen_name]
        expected_images.add(screen_name)
        assert dimensions[screen['stored']] == (2560, 1920)
        if incomplete:
            assert prefix + '.png' not in index
            assert 'windowCaptureSha256' not in row and 'sessionCapture' not in row
            assert not (CAPSULE / 'output' / (prefix + '.captured')).exists()
        else:
            assert row['hardwareAcceleration'] is False
            window = index[prefix + '.png']
            expected_images.add(prefix + '.png')
            assert row['sessionCapture'] == screen_name
            assert window['sha256'] == row['windowCaptureSha256'] and screen['sha256'] == row['sessionCaptureSha256']
            assert dimensions[window['stored']] == (row['width'] * scale, row['height'] * scale)
            assert (CAPSULE / 'output' / (prefix + '.captured')).is_file()
        for layout in row['layouts']:
            expected = profiles[layout['name']]['state']
            assert all(layout[k] == v for k, v in expected.items() if k != 'step')
            image = index[layout['capture']]
            expected_images.add(layout['capture'])
            assert dimensions[image['stored']] == (layout['pixelWidth'], layout['pixelHeight'])
        for actual, expected in zip(row['histories'], native['histories'], strict=True):
            assert actual['owner'] == expected['owner'] and actual['initial'] == expected['initial']
            assert actual['states'] == expected['states']
        for actual, expected in zip(row['boundaries'], native['boundaries'], strict=True):
            assert all(actual[k] == expected[k] for k in ['columnWidth', 'initial', 'requestedPosition'])
            state = actual['actual']; pane = expected['after'][0]
            assert state['columnWidth'] == pane['width'] and state['displayedNavigation'] == (not pane['collapsed'])
            assert state['navigation'] == expected['navigation'] and state['requests'] == expected['requests']
    assert len(records) == 8
    assert len(expected_images) == (655 if failed else 656) and set(index) == expected_images
    assert (CAPSULE / 'output/weston-version.txt').read_text().strip() == 'weston 13.0.4'
    pointer = dict(line.split('=', 1) for line in (CAPSULE / 'output/native-pointer.txt').read_text().splitlines())
    assert (pointer['X'], pointer['Y'], pointer['SCREEN']) == ('2559', '1919', '0')
    if failed:
        print('Installed AdminShell failed attempt retained: 7 complete sessions, 8 structural passes; final window capture missing; no session-matrix acceptance')
    else:
        print('Installed AdminShell: 8 X11/Wayland software/OpenGL/scale contexts; native data matched; physical and raster parity pending')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--failed-attempt', action='store_true', help='Verify the preserved readiness failure, not a successful matrix')
    args = parser.parse_args()
    if args.failed_attempt:
        CAPSULE = ROOT / 'evidence/development/admin-shell-sessions-failure-20261020'
    verify(args.failed_attempt)
