#!/usr/bin/env python3
"""Audit the installed toolchain checkpoint without accepting native parity."""
import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/qt-software-toolchain-20261019'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    read = lambda name: json.loads((CAPSULE / name).read_text())
    files = read('files.json')
    assert set(files) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*')
                          if p.is_file() and p != CAPSULE / 'files.json'}
    for name, row in files.items():
        relative = PurePosixPath(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        path = CAPSULE / name
        assert digest(path) == row['sha256'] and path.stat().st_size == row['bytes'], name
    result = read('result.json')
    assert result['exitCode'] == 0 and result['supportedToolchainRuntimePassed']
    assert not any(result[key] for key in ['accepted', 'nativeAcceptance', 'physicalDisplay',
                                           'physicalListening', 'fullMirrorAccepted'])
    image = result['imageId']
    sdk = read('sdk/actual-image-sdk.json')
    before, after = sdk['sdk-before'], sdk['after']
    assert before.keys() == after.keys() and len(after) == 9236
    changed = [name for name in before if before[name] != after[name]]
    assert changed == ['lib/libQt6Quick.so.6.8.3']
    assert sdk['sdk-changes'] == dict(changed=changed, added=[], removed=[], unchangedEntries=9235, nativeAcceptance=False)
    assert sdk['qt'] == '6.8.3' and sdk['target'] == 'aarch64-linux-gnu' and sdk['preload'] is None
    features = sdk['features']
    assert len(features) == 7 and sum(len(row['sdk']) for row in features) == 49
    for row in features:
        assert row['matches'] and row['source'] == {key: 'ON' if value == '1' else 'OFF'
                                                   for key, value in row['sdk'].items()}
    assert [row['sdk']['QT_FEATURE_qml_jit'] for row in features if 'QT_FEATURE_qml_jit' in row['sdk']] == ['1']
    provenance = sdk['provenance']
    assert after[changed[0]]['sha256'] == provenance['installedLibrarySha256'] == 'aa4568a285661d11667aad745903a6d3dd49045d40ea8008c12dc24015cf3c77'
    assert before[changed[0]]['sha256'] == provenance['originalLibrarySha256']
    assert provenance['runtimePath'] == '$ORIGIN' and provenance['nativeAcceptance'] is False
    assert provenance['archiveSha256'] == '1f03a2b8f5588b4face7da87926e9b2c1372b3a32157c52df07a75067a9db1af'
    assert provenance['patchSha256'] == digest(ROOT / 'tools/qt-software-opacity.patch')
    assert 'undefined symbol' not in sdk['linkage'] and 'not found' not in sdk['linkage']
    assert 'libQt6Qml.so.6 => /opt/qt/lib/' in sdk['linkage']

    frozen = read('provenance/qt-software-final-image-v2/inputs.json')
    assert frozen['sourceRevision'] == result['sourceRevision'] == '2b837a5fd52b462b59d8d66dae4a71a3a88bce20'
    assert len(frozen['files']) == result['frozenSourceFiles'] == 807
    historical = []
    for name, checksum in frozen['files'].items():
        copy = CAPSULE / 'implementation-inputs' / name
        if copy.exists():
            assert digest(copy) == checksum, name
        else:
            assert '\n' not in name and '..' not in PurePosixPath(name).parts
            historical.append(name)
    payload = ''.join(frozen['sourceRevision'] + ':' + name + '\n' for name in historical).encode()
    objects = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT, input=payload,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    stream = io.BytesIO(objects.stdout)
    for name in historical:
        header = stream.readline().split()
        assert len(header) == 3 and header[1] == b'blob', (name, header)
        data = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(data).hexdigest() == frozen['files'][name], name
    assert not stream.read()
    build_inputs = read('provenance/qt-software-toolchain-build-v4/inputs.json')
    for name, checksum in build_inputs.items():
        assert digest(CAPSULE / 'implementation-inputs' / name) == checksum == digest(ROOT / name), name
    # The retained workflow belongs to this toolchain checkpoint. Later CI
    # orchestration repairs have their own live workflow evidence and verifier.
    workflow = subprocess.check_output(['git', 'show',
        '53606010b9e8f7c804275da3f57b543f875afb93:.github/workflows/linux.yml'], cwd=ROOT)
    assert hashlib.sha256(workflow).hexdigest() == digest(CAPSULE / 'implementation-inputs/.github/workflows/linux.yml')
    current_check = (ROOT / 'scripts/check-linux.sh').read_text()
    current_check = current_check.replace('(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --mobile-shell)\n', '', 1)
    current_check = current_check.replace('hero-carousel app-tabs mobile-shell; do', 'hero-carousel app-tabs; do', 1)
    assert hashlib.sha256(current_check.encode()).hexdigest() == digest(CAPSULE / 'implementation-inputs/scripts/check-linux.sh')
    core = read('provenance/core-tests-result.json')
    assert core['exitCode'] == core['failedTests'] == 0 and core['tests'] == result['coreTests'] == 55
    assert core['imageId'] == image and core['qtQuickSha256'] == provenance['installedLibrarySha256']
    assert digest(CAPSULE / 'core/LastTest.log.txt') == core['lastTestLogSha256']
    assert re.search(r'100% tests passed,\s+0 tests failed out of\s+55', (CAPSULE / 'core/linux-core-runtime.log.txt').read_text())
    bindings = read('provenance/source-binding-result.json')
    assert bindings['coreInputsMatched'] == core['coreInputs'] == 607
    assert bindings['consumerInputsMatched'] == core['consumerInputs'] == 150
    assert bindings['driverSourceInputs'] == 807 and bindings['exitCode'] == 0

    spec = importlib.util.spec_from_file_location('qt_source_controls', ROOT / 'scripts/verify-qt-software-source-patch.py')
    controls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(controls)
    controls.CAPSULE = CAPSULE / 'sdk'
    assert controls.profiles('sdk-control', {'xcb-dpr1': 0, 'xcb-dpr2': 0, 'wayland-dpr1': 9}) == (90, 9, 9)
    assert controls.profiles('patched-regression', {name: 0 for name in
        ['xcb-dpr1', 'xcb-dpr2', 'wayland-dpr1', 'wayland-dpr2']}) == (120, 12, 0)
    commands = read('provenance/qt-software-final-image-v2/commands.json')
    assert [(r['name'], r['exitCode']) for r in commands] == [
        ('toolchain-evidence', 0), ('linux-core-runtime', 0), ('independent-consumer-configure', 0),
        ('independent-consumer-build', 0), ('runtime-source-absence', 1)]
    assert 'AssertionError' in (CAPSULE / 'runtime/prior-empty-workdir-failure.log.txt').read_text()
    commands = read('provenance/qt-software-final-image-v3/commands.json')
    assert [(r['name'], r['exitCode']) for r in commands] == [
        ('runtime-source-absence', 0), ('installed-runtime-and-date', 0),
        ('general-display-sessions', 0), ('hero-display-sessions', 0)]
    runtime = read('provenance/qt-software-final-image-v3/result.json')
    assert runtime['imageId'] == image and runtime['independentConsumerBuilt']
    assert runtime['libraryAndConsumerProjectSourcesAbsentAtRuntime'] and runtime['projectSourcePresenceStillRejected']
    inventory = read('runtime/display-files.json')
    contexts = set(itertools.product(['xcb', 'wayland'], ['software', 'opengl'], ['standard', 'scaled']))
    general = [p for p in (CAPSULE / 'runtime/display').glob('*.json') if p.name != 'environment.json']
    assert len(general) == 304
    observed = set()
    for path in general:
        row = json.loads(path.read_text())
        assert row['qt'] == '6.8.3' and row['physicalDisplay'] is row['hardwareAcceleration'] is False
        platform, backend, configuration = path.stem.split('-')[-3:]
        observed.add((platform, backend, configuration))
        assert row['dpr'] == (2 if configuration == 'scaled' else 1)
        assert row['graphicsApi'] == (1 if backend == 'software' else 3)
        capture = path.stem + '.png'
        assert row['windowCaptureSha256'] == inventory[capture]['sha256']
        assert row['sessionCaptureSha256'] == inventory[row['sessionCapture']]['sha256']
    assert observed == contexts
    hero = list((CAPSULE / 'runtime/display/hero-carousel').glob('*.json'))
    hero = [p for p in hero if p.name != 'environment.json']
    assert len(hero) == 8 and {tuple(p.stem.split('-')) for p in hero} == contexts
    for path in hero:
        row = json.loads(path.read_text())
        assert row['accepted'] is False and row['structuralChecks'] == 'passed'
        assert row['displaySession']['physicalDisplay'] is row['displaySession']['hardwareAcceleration'] is False

    date = read('provenance/qt-software-date-replay-v1/result.json')
    cold = read('date/raw-image-comparison.json')
    assert date['imageId'] == image and date['coldByteIdentical'] == result['coldByteIdentical'] == cold['identical'] == 437
    assert cold['parentManifestSha256'] == digest(ROOT / 'evidence/development/date-range-fields-20261018/files.json')
    assert len(cold['rows']) == len({r['path'] for r in cold['rows']}) == 437
    for row in cold['rows']:
        path = CAPSULE / 'date/cold' / row['path']
        assert digest(path) == row['expected'] == row['actual'] and row['identical']
        with Image.open(path) as image_data:
            image_data.load()
            assert image_data.width > 0 and image_data.height > 0
    literal = read('date/literal-validation.json')
    assert literal['checks'] == date['literalChecks'] == result['literalChecks'] == 128
    assert literal['nativeValueComparisons'] == 64 and len(literal['profiles']) == 8
    for profile in literal['profiles']:
        path = CAPSULE / 'date/literal-and-reports' / profile['path']
        assert digest(path) == profile['sha256']
        row = json.loads(path.read_text())
        assert row['accepted'] is False and len(row['literalInput']) == 16
        assert all(r['samePixels'] and r['before'] == r['after'] for r in row['literalInput'])

    reader = read('provenance/qt-software-reader-replay-v1/result.json')
    assert reader['baseImageId'] == image and reader['phases'] == result['readerPhases'] == 42
    assert reader['qtSdkUnchanged'] and not reader['physicalListening']
    assert read('reader/actual-sdk.json') == after
    for name in ['x11-software', 'wayland-opengl-scaled']:
        profile = read('reader/' + name + '/result.json')
        report = read('reader/' + name + '/operator-controls-v1/result.json')
        assert profile == reader['profiles'][name] and profile['exitCode'] == 0
        assert report['status'] == 'passed' and len(report['phases']) == profile['phases'] == 21
        assert profile['nativeKeyFlow'] == profile['directAssistiveTextEdit'] == 'passed'
        assert profile['physicalListening'] is profile['physicalInput'] is False
        speech = (CAPSULE / 'reader' / name / 'orca-debug.log.txt').read_bytes()
        for phase, target in [('go-to-native-arrows-preserve-input', 'Alpine'),
                              ('go-to-assistive-selection-keeps-input', 'Alphabet')]:
            window = profile['speechWindows'][phase]
            data = speech[window['startBytes']:window['endBytes']]
            assert hashlib.sha256(data).hexdigest() == window['sha256']
            assert any('SPEECH OUTPUT:' in line and target in line for line in data.decode().splitlines())
            assert any('SPEECH DISPATCHER: Speaking' in line and target in line for line in data.decode().splitlines())
    print('Supported Qt toolchain:55 tests;9236 SDK entries,only QtQuick changed;437 unchanged cold captures;128 literal checks;42 reader phases. Native and mirror acceptance pending')


if __name__ == '__main__':
    verify()
