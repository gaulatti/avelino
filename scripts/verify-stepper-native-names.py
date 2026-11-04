#!/usr/bin/env python3
"""Audit native Stepper names and the separately frozen Linux execution domains."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/stepper-native-action-names-20261024'
NATIVE = ROOT / 'evidence/reference-investigations/stepper-accessibility-20261024'
PARENT = 'cc1047e29eac2ec4ee3e8d0a18f92ec68b6f23bc'
MODULE = 'fe5314b3a9328f0ad2de046a2393f62e5b3832f934b0fba810040855ec72f5f0'
CONSUMER = 'e0e80da814c12409eec7c990d65369bd44276ac9f31b091c97919c7bc54d66c7'
DELTA = ['src/Avelino/BleeckerStepper.qml', 'tests/components/tst_stepper.qml', 'tests/consumer/stepperchecks.h']
sha = lambda value: hashlib.sha256(value).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


OLD = load('stepper_reader_history', ROOT / 'scripts/verify-stepper-reader.py')
Capsule = OLD.Capsule


def manifest(directory):
    files = json.loads((directory / 'files.json').read_text())
    assert set(files) == {str(path.relative_to(directory)) for path in directory.rglob('*')
                          if path.is_file() and path != directory / 'files.json'}
    for name, row in files.items():
        value = (directory / name).read_bytes()
        assert sha(value) == row['sha256'] and len(value) == row['bytes'], name
    capsule = Capsule(directory)
    for name in capsule.records:
        value = capsule.raw(name)
        if value.startswith(b'\x89PNG\r\n\x1a\n'):
            with Image.open(io.BytesIO(value)) as image:
                image.load()
    return capsule


def git_files(revision, names):
    result = {}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for name in names:
            assert '\n' not in name and '\r' not in name
            process.stdin.write((revision + ':' + name + '\n').encode()); process.stdin.flush()
            header = process.stdout.readline().split(); assert len(header) == 3 and header[1] == b'blob', name
            result[name] = process.stdout.read(int(header[2]))
            assert process.stdout.read(1) == b'\n'
        process.stdin.close(); assert process.wait() == 0
    return result


def limits(value):
    assert value['sourceParent'] == PARENT and value['librarySourceAttempt'] == 2
    for key, expected in [('qtChecksPerDpr', 159), ('readerPhasesEach', 13), ('consumerProfiles', 2),
                          ('consumerNativeActionTracesEach', 25), ('consumerFormatterWitnessesEach', 126),
                          ('runtimeInputFiles', 579), ('installedFiles', 158), ('priorProtectedFields', 31530),
                          ('rawLinuxFramePairs', 26), ('rawLinuxExactPairs', 14)]:
        assert value[key] == expected, key
    assert value['dprs'] == [1, 2] and value['nativeNames'] == ['Remove', 'Add']
    assert value['nativeEvidence'] == str(NATIVE.relative_to(ROOT))
    for key in ['accepted', 'nativeReaderAccepted', 'numericSpeechAccepted', 'nativeRasterAccepted',
                'rawLinuxImagesAllExact', 'physicalInputAccepted', 'independentMachineAccepted',
                'fullQt58Rerun', 'consumerLibraryBuildRerun', 'expectedImagesChanged']:
        assert value[key] is False, key
    assert value['approvedExceptions'] == []


def native_calls(calls, responses, states):
    assert len(calls) == len(responses) == 6
    texts = []
    for call, response in zip(calls, responses):
        a = call['payload']; b = response['payload']
        assert a['call_id'] == b['call_id']
        assert a['namespace'] == 'mcp__cua_repl' and a['name'] == 'js'
        text = '\n'.join(item['text'] for item in b['output'] if 'text' in item)
        assert 'button Add' in text and re.search(r'button(?: \(disabled\))? Remove', text)
        texts.append(text)
    assert [int(re.search(r'\n\t\t4 text (\d+)\n', text)[1]) for text in texts] == [2, 3, 2, 1, 1, 1]
    code = [json.loads(row['payload']['arguments'])['code'] for row in calls]
    assert 'cua.getApp(' in code[0] and 'PinnedStepperReader20261024v2.app' in code[0]
    assert '.click(5)' in code[1] and all('.click(3)' in row for row in code[2:4])
    assert "pressKey('Tab')" in code[4] and "typeText('Native reader')" in code[5]
    assert 'button (disabled) Remove' in texts[3]
    assert 'focused UI element is 7 text field' in texts[4]
    assert 'Value: Native reader, Placeholder: Continue editing' in texts[5]
    for name, value, requests in [('add', 3, [3]), ('remove', 2, [3, 2]), ('lower', 1, [3, 2, 1]), ('outside', 1, [3, 2, 1])]:
        row = states[name]
        assert row['value'] == value and row['requests'] == requests and row['accepted'] is False
        assert row['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert states['outside']['outside'] == 'Native reader'


def native_provenance(value):
    assert value['referenceRevision'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    path = ROOT / value['sourceIdentity']
    assert sha(path.read_bytes()) == value['sourceIdentitySha256']
    identity = json.loads(path.read_text())
    assert value['sourceFiles'] == {row['path']: row['sha256'] for row in identity['files']}
    assert len(value['sourceFiles']) == 89 and value['sourceArchiveSha256'] == identity['fullArchiveSha256']
    original = json.loads((ROOT / 'evidence/reference-investigations/stepper-20261016/tooling-provenance.json').read_text())
    assert value['originalToolArchiveSha256'] == original['toolArtifact']['sha256']
    assert len(value['wrapperFailures']) == 3
    for row in value['wrapperFailures']:
        assert row['signal'] == 'SIGTRAP' and row['exception'] == 'EXC_BREAKPOINT'
        assert any(frame.get('sourceFile') == 'resource_bundle_accessor.swift' for frame in row['frames'])
    for key in ['accepted', 'appleSourceOrBinariesIncluded', 'nativeSpeechMeasured', 'nativeKeyboardAccepted', 'physicalInputAccepted']:
        assert value[key] is False, key
    assert value['approvedExceptions'] == []


def library_change(before, after):
    expected = before.replace(b'Accessible.name:qsTr("Decrease %1").arg(control.label)', b'Accessible.name:qsTr("Remove")')
    expected = expected.replace(b'Accessible.name:qsTr("Increase %1").arg(control.label)', b'Accessible.name:qsTr("Add")')
    assert before != expected and after == expected


def binding(capsule, value):
    assert value['sourceParent'] == PARENT and value['librarySourceAttempt'] == 2 and value['accepted'] is False
    assert value['runtimeDeltaPaths'] == DELTA and value['consumerOverridePaths'] == [DELTA[2]]
    assert len(value['files']) == 579
    parent = git_files(PARENT, value['files'])
    first = capsule.record('source1/inputs.json')['sourceFiles']
    second = capsule.record('source2/inputs.json')['sourceFiles']
    patches = {name: capsule.raw('source2/implementation/' + name) for name in DELTA[:2]}
    patches[DELTA[2]] = capsule.raw('consumer/implementation/stepperchecks.h')
    library_change(parent[DELTA[0]], patches[DELTA[0]])
    assert capsule.raw('source1/implementation/' + DELTA[0]) == parent[DELTA[0]]
    assert capsule.raw('source1/implementation/' + DELTA[1]) == patches[DELTA[1]]
    assert sorted(name for name in value['files'] if first[name] != sha(parent[name])) == [DELTA[1]]
    assert sorted(name for name in value['files'] if second[name] != sha(parent[name])) == DELTA[:2]
    assert second == capsule.record('reader1/output/producer-inputs.json')['sourceFiles']
    assert second == capsule.record('reader2/output/producer-inputs.json')['sourceFiles']
    expected = {name: sha(patches.get(name, content)) for name, content in parent.items()}
    assert value['files'] == expected
    assert sorted(name for name in value['files'] if second[name] != value['files'][name]) == [DELTA[2]]
    consumer = capsule.record('consumer1/controller/inputs.json')
    assert consumer['consumerDifferencesFromLibrarySnapshot'] == ['stepperchecks.h']
    originals = git_files(PARENT, ['tests/consumer/' + name for name in consumer['consumerSourceFiles']])
    assert consumer['consumerSourceFiles'] == {
        name.removeprefix('tests/consumer/'): sha(patches.get(name, content)) for name, content in originals.items()}
    return expected


def candidate(current, executed):
    assert current == executed, 'Current runtime differs from the retained execution; collect new evidence'


def inventory_snapshot(value, current=False):
    assert value['sourceParent'] == PARENT and value['accepted'] is False
    assert re.fullmatch(r'[0-9a-f]{40}', value['candidateGitBlob'])
    data = subprocess.check_output(['git', 'cat-file', 'blob', value['candidateGitBlob']], cwd=ROOT)
    assert sha(data) == value['candidateSha256']
    protected = load('protected_inventory', ROOT / 'scripts/verify-modal-parent-focus.py').protected_fields
    before = protected(json.loads(git_files(PARENT, ['docs/parity-inventory.json'])['docs/parity-inventory.json']))
    after = protected(json.loads(data))
    assert len(before) == value['priorProtectedFields'] == 31530
    assert len(after) == value['candidateProtectedFields'] == 31532
    assert all(after.get(name) == field for name, field in before.items())
    if current:
        assert sha((ROOT / 'docs/parity-inventory.json').read_bytes()) == value['candidateSha256']


def buttons(tree):
    label = OLD.named(tree, 'Quantity', 'label'); ax, ay, aw, ah = label['bounds']
    result = {}
    for name in ['Remove', 'Add']:
        values = []
        for item in OLD.walk(tree):
            if item['name'] != name or item['role'] != 'push button' or not OLD.state(item, 'SHOWING'):
                continue
            x, y, width, height = item['bounds']
            if x >= ax + aw and abs(y + height / 2 - ay - ah / 2) < 5:
                values.append((x, item))
        assert values, name
        result[name] = min(values, key=lambda row: row[0])[1]
    return result


def snapshot(value, row, pid):
    assert value['targetPid'] == pid and value['accepted'] is False
    assert {key: value[key] for key in row} == row
    actions = buttons(value['tree']); expected = OLD.PHASE_VALUES[row['phase']]
    lower, upper = actions['Remove'], actions['Add']
    assert OLD.state(lower, 'ENABLED') == (expected != '1')
    assert OLD.state(upper, 'ENABLED') == (expected != '10')
    assert all('Press' in item['actions'] for item in actions.values())
    left = lower['bounds']; right = upper['bounds']; values = []
    for item in OLD.walk(value['tree']):
        if item['role'] == 'label' and OLD.state(item, 'SHOWING'):
            x, y, width, height = item['bounds']
            if x >= left[0] + left[2] and x + width <= right[0] and abs(y + height / 2 - left[1] - left[3] / 2) < 5:
                values.append(item['name'])
    assert values == [expected]
    focus = {'increase-focused': upper, 'keyboard-increment': upper,
             'decrease-focused': lower, 'keyboard-decrement': lower}
    if row['phase'] in focus:
        assert OLD.state(focus[row['phase']], 'FOCUSED')
    if row['phase'].startswith('outside-'):
        assert OLD.state(OLD.named(value['tree'], 'Continue editing', 'text'), 'FOCUSED')


def reader(report, log):
    assert report['status'] == 'passed' and report['accepted'] is report['physicalInput'] is report['nativeReaderAcceptance'] is False
    assert [row['phase'] for row in report['phases']] == list(OLD.PHASE_VALUES)
    previous = 0
    for row in report['phases']:
        phase = row['phase']; observed = row['observations']
        assert observed['value'] == OLD.PHASE_VALUES[phase]
        assert previous <= row['readerLogBytes'] <= len(log)
        if phase in ['increase-focused', 'decrease-focused']:
            name = 'Add' if phase == 'increase-focused' else 'Remove'
            assert observed['button'] == name and observed['speechOutputAndDispatcher'] is True
            assert previous <= observed['speechOffset'] <= row['readerLogBytes']
            fragment = log[observed['speechOffset']:row['readerLogBytes']].splitlines()
            for prefix in [b'SPEECH OUTPUT:', b'SPEECH DISPATCHER: Speaking']:
                assert any(prefix in line and re.search(rb'\b' + name.encode() + rb'\b', line) for line in fragment)
        if phase.startswith('disabled-'):
            assert observed['remainsDisabled'] is True
            assert isinstance(observed['disabledActionBridgeReturn'], bool)
        if phase.startswith('keyboard-'):
            assert observed['focused'] is True
        if phase == 'outside-edited':
            assert observed['text'] == 'Stepper reader'
        previous = row['readerLogBytes']
    OLD.speech_gap(report, log)


def package_inputs(value, installed):
    assert value['sourceAttempt'] == 2 and value['imageId'] == OLD.IMAGE
    assert value['installedPrefixFiles'] == installed
    for key in ['accepted', 'sourceProjectsMounted', 'libraryProjectMounted', 'consumerProjectMounted', 'productBuildMounted']:
        assert value[key] is False, key
    command = value['command']
    mounts = [command[index + 1] for index, word in enumerate(command) if word == '--mount']
    assert len(mounts) == 2
    assert sum('target=/package/install,readonly' in mount for mount in mounts) == 1
    assert sum(mount.endswith('target=/probe') for mount in mounts) == 1
    assert command[-3:] == [OLD.IMAGE, 'python3', '/probe/bootstrap.py']


def consumer_report(report, dpr):
    for key in ['stepperChecks', 'callerBindingChecks', 'focusChecks', 'qtAccessibilityChecks']:
        assert report[key] == 'passed'
    assert report['platform'] == 'xcb' and report['graphicsApi'] == 1 and report['qt'] == '6.8.3'
    assert report['dpr'] == dpr and report['textScale'] == (1 if dpr == 1 else 1.5)
    assert report['appearance'] == ('light' if dpr == 1 else 'dark')
    assert report['matchingNativeIntegerFormatterWitnesses'] == 126
    witness = json.loads(git_files(PARENT, ['tests/consumer/native-stepper-witnesses.json'])['tests/consumer/native-stepper-witnesses.json'])
    assert len(report['nativeBehaviorTraces']) == len(witness['traces']) == 25
    for actual, expected in zip(report['nativeBehaviorTraces'], witness['traces']):
        assert actual == {'fixture': expected['fixture'], 'status': 'passed', 'requests': expected['requests'], 'finalValue': expected['finalValue']}


def capture(value):
    assert value['exitCode'] == value['captureExitCode'] == 0
    assert value['acknowledgedAfterActualSessionCapture'] is True
    assert value['sourceProjectsMounted'] is value['physicalInput'] is value['accepted'] is False
    assert value['captureCommand'] == ['import', '-window', 'root', '/probe/full-session.png']


def visual(capsule):
    previous = Capsule(ROOT / 'evidence/development/stepper-reader-20261024')
    report = capsule.record('visual/comparison.json')
    expected = [(old, new, phase) for old, new in [(2, 1), (3, 2)] for phase in OLD.PHASE_VALUES]
    assert [(row['oldReader'], row['newReader'], row['phase']) for row in report['readerPairs']] == expected
    equal = pixel_equal = 0
    for row in report['readerPairs']:
        a = previous.raw(f"reader{row['oldReader']}/output/{row['phase']}.png")
        b = capsule.raw(f"reader{row['newReader']}/output/{row['phase']}.png")
        assert sha(a) == row['oldSha256'] and sha(b) == row['newSha256']
        changed = 0
        if a != b:
            with Image.open(io.BytesIO(a)) as left, Image.open(io.BytesIO(b)) as right:
                assert left.size == right.size == (2560, 1920)
                for item in [left, right]:
                    assert item.convert('RGBA').getchannel('A').getextrema() == (255, 255)
                delta = ImageChops.difference(left.convert('RGB'), right.convert('RGB'))
                box = delta.getbbox()
                if box:
                    red, green, blue = delta.crop(box).split()
                    maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
                    changed = maximum.width * maximum.height - maximum.histogram()[0]
        assert row['changedPixels'] == changed and row['bytesEqual'] == (a == b)
        equal += a == b
        pixel_equal += changed == 0
    assert report['bytesEqual'] == equal == 14 and report['pixelExact'] == pixel_equal == 14
    assert report['total'] == 26 and report['accepted'] is report['nativeImagesCompared'] is False


def verify(current=False):
    native = manifest(NATIVE); capsule = manifest(DIRECTORY)
    limits(json.loads((DIRECTORY / 'validation.json').read_text()))
    native_provenance(json.loads((NATIVE / 'provenance.json').read_text()))
    native_calls(native.record('native-cua-calls.json'), native.record('native-cua-responses.json'),
                 {name: native.record(name + '-state.json') for name in ['add', 'remove', 'lower', 'outside']})
    close = native.record('native-close.json')
    assert close['processTerminalVerified'] is close['ownedFinderWindowClosed'] is True
    provenance = native.record('native-cua-provenance.json')
    assert provenance['retainedResponses'] == 6 and provenance['responseSha256'] == sha(native.raw('native-cua-responses.json'))
    expected = binding(capsule, json.loads((DIRECTORY / 'runtime-binding.json').read_text()))
    if current:
        candidate({name: sha((ROOT / name).read_bytes()) for name in expected}, expected)
    assert capsule.record('source1/result.json')['exitCode'] == 2
    negative = capsule.raw('source1/native-accessible-names.log')
    assert b'Actual   (): Decrease Quantity' in negative and b'Expected (): Remove' in negative
    assert b'Actual   (): Increase Quantity' in negative and b'Expected (): Add' in negative
    for number in [1, 2]:
        assert capsule.record(f'source{number}/result.json')['sourceUnchanged'] is True
    assert capsule.record('source2/result.json')['exitCode'] == 0
    assert all(row['exitCode'] == 0 for row in capsule.record('source2/commands.json'))
    for dpr in [1, 2]:
        assert b'Totals: 159 passed, 0 failed, 0 skipped' in capsule.raw(f'source2/stepper-dpr{dpr}.log')
    installed = capsule.record('source2/package-producer.json')['installedFiles']
    assert len(installed) == 158 and installed['lib/qml/Avelino/libAvelino.so'] == MODULE
    for number in [1, 2]:
        prefix = f'reader{number}/output/'
        result = capsule.record(f'reader{number}/controller/result.json')
        assert result['exitCode'] == 0 and result['operatorPhases'] == 13
        assert result['installedPrefixUnchanged'] is result['probeSourcesUnchanged'] is True
        config = capsule.record(f'reader{number}/controller/inputs.json'); package_inputs(config, installed)
        for name, digest in config['probeFiles'].items():
            assert sha(capsule.raw(prefix + name)) == digest
        report = capsule.record(prefix + 'operator-report.json'); reader(report, capsule.raw(prefix + 'orca-debug.log'))
        assert capsule.record(prefix + 'session-result.json')['exitCode'] == 0
        profile = capsule.record(prefix + 'profile.json')
        assert profile == {'protocol': 'xcb' if number == 1 else 'wayland', 'backend': 'software' if number == 1 else 'opengl', 'scaled': number == 2, 'accepted': False}
        environment = capsule.record(prefix + 'session-env.json')
        assert environment['QT_QPA_PLATFORM'] == profile['protocol'] and environment['QT_SCALE_FACTOR'] == str(number)
        client = capsule.raw(prefix + 'client.log')
        assert (b'Loading backend software' if number == 1 else b'Creating QRhi with backend OpenGL') in client
        assert b'ValueChanged event and no ValueInterface or ComboBox' in client
        pid = capsule.record(prefix + 'client-pid.json')['pid']
        for row in report['phases']:
            snapshot(capsule.record(prefix + row['phase'] + '.json'), row, pid)
    failed = capsule.record('consumer1/controller/result.json')
    assert failed['exitCode'] == 248 and failed['consumerSourceUnchanged'] is failed['installedPrefixUnchanged'] is True
    assert failed['consumerSha256'] == CONSUMER
    assert b'main.cpp.o' in capsule.raw('consumer1/controller/consumer-build.log')
    assert b'Qt pointer/keyboard/accessibility paths passed' in capsule.raw('consumer1/controller/consumer-dpr1.log')
    assert capsule.record('consumer1/controller/inputs.json')['installedFiles'] == installed
    result = capsule.record('consumer2/controller/result.json')
    assert result['exitCode'] == 0 and result['profilesPassed'] == 2
    assert result['consumerUnchanged'] is result['installedPrefixUnchanged'] is True
    assert result['sourceProjectsMounted'] is result['productBuildMounted'] is False
    inputs = capsule.record('consumer2/controller/inputs.json')
    assert inputs['consumerSha256'] == CONSUMER and inputs['installedFiles'] == installed
    assert all(row['exitCode'] == 0 for row in capsule.record('consumer2/controller/commands.json'))
    for dpr in [1, 2]:
        prefix = f'consumer2/runtime/dpr{dpr}/'
        consumer_report(capsule.record(prefix + 'report.json'), dpr)
        capture(capsule.record(prefix + 'capture-result.json'))
        assert sha(capsule.raw(prefix + 'capture.py')) == inputs['captureScriptSha256']
        with Image.open(io.BytesIO(capsule.raw(prefix + 'full-session.png'))) as image:
            assert image.size == (2560, 1920)
    visual(capsule)
    inventory_snapshot(json.loads((DIRECTORY / 'inventory-binding.json').read_text()), current=current)
    print('Stepper native names: native AX, test-first repair, installed Qt/reader/consumer paths and raw image differences verified; complete parity pending')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--current', action='store_true', help='Also require current runtime inputs to match the executed candidate')
    verify(current=parser.parse_args().current)
