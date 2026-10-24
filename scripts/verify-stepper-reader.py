#!/usr/bin/env python3
"""Audit installed Stepper reader observations and their unresolved speech gap."""
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/stepper-reader-20261024'
PRODUCER = ROOT / 'evidence/development/date-range-assistive-lifetime-20261024'
SOURCE = '899f3e8f1fd50bcf9094d417f4c449cea651c36b'
BUILD_IMAGE = 'sha256:c32e246cda73ab6992d808ceb551fa569fdf8ee85308f82d2bf1b15a96e69b14'
IMAGE = 'sha256:e2c92a8b5a48fe0215e9dc42ff81d9d454f3497b4ee7d56bed95647f0cee7d21'
PHASE_VALUES = {
    'caller-ready': '2', 'increase-focused': '2', 'assistive-increment': '3',
    'assistive-decrement': '2', 'lower-bound': '1', 'disabled-decrement': '1',
    'keyboard-increment': '2', 'upper-bound': '10', 'disabled-increment': '10',
    'decrease-focused': '10', 'keyboard-decrement': '9',
    'outside-focused': '9', 'outside-edited': '9',
}
sha = lambda value: hashlib.sha256(value).hexdigest()


class Capsule:
    def __init__(self, directory):
        self.directory = directory
        self.records = json.loads((directory / 'records.json').read_text())

    def raw(self, name):
        row = self.records[name]
        path = self.directory / row['stored']
        value = path.read_bytes()
        if path.suffix == '.gz':
            value = gzip.decompress(value)
        assert len(value) == row['bytes'] and sha(value) == row['sha256'], name
        assert not value.startswith((b'\x7fELF', b'\xcf\xfa\xed\xfe'))
        return value

    def record(self, name):
        return json.loads(self.raw(name))


def limits(value):
    assert value['sourceCommit'] == SOURCE and value['sourceAttempt'] == 8
    assert value['readerAttempts'] == [2, 3] and value['operatorPhasesEach'] == 13
    assert value['retainedFailedReader'] == 1
    assert value['installedPrefixFiles'] == 158 and value['runtimeInputFiles'] == 579
    assert value['priorProtectedFields'] == 31527
    for key in ['accepted', 'applicationSourcesChanged', 'qtSuiteRerunForThisEvidence',
                'nativeRasterAccepted', 'nativeGeometryAccepted', 'nativeReaderAccepted',
                'physicalInputAccepted', 'independentMachineAccepted',
                'numericValueSpeechAccepted', 'numericValueSpeechObservedInActionWindows',
                'expectedImagesChanged']:
        assert value[key] is False, key
    assert value['approvedExceptions'] == []


def walk(value):
    yield value
    for child in value['children']:
        yield from walk(child)


def state(value, name):
    return any('ATSPI_STATE_' + name + ' ' in item for item in value['states'])


def named(tree, name, role):
    values = [item for item in walk(tree) if item['name'] == name and item['role'] == role]
    assert len(values) == 1, (name, role, len(values))
    return values[0]


def snapshot(value, row, pid):
    assert value['accepted'] is False and value['targetPid'] == pid
    assert {key: value[key] for key in row} == row
    tree = value['tree']
    lower = named(tree, 'Decrease Quantity', 'push button')
    upper = named(tree, 'Increase Quantity', 'push button')
    for button in [lower, upper]:
        assert 'Press' in button['actions'] and state(button, 'SHOWING')
    expected = PHASE_VALUES[row['phase']]
    assert state(lower, 'ENABLED') == (expected != '1')
    assert state(upper, 'ENABLED') == (expected != '10')
    left = lower['bounds']; right = upper['bounds']; values = []
    for item in walk(tree):
        if item['role'] != 'label' or not state(item, 'SHOWING'):
            continue
        x, y, width, height = item['bounds']
        if x >= left[0] + left[2] and x + width <= right[0] and abs(y + height / 2 - left[1] - left[3] / 2) < 5:
            values.append(item['name'])
    assert values == [expected], (row['phase'], values, expected)
    if row['phase'] in ['increase-focused', 'keyboard-increment']:
        assert state(upper, 'FOCUSED')
    if row['phase'] in ['decrease-focused', 'keyboard-decrement']:
        assert state(lower, 'FOCUSED')
    if row['phase'] in ['outside-focused', 'outside-edited']:
        assert state(named(tree, 'Continue editing', 'text'), 'FOCUSED')


def reader(report, log):
    assert report['accepted'] is report['physicalInput'] is report['nativeReaderAcceptance'] is False
    assert report['status'] == 'passed'
    assert [row['phase'] for row in report['phases']] == list(PHASE_VALUES)
    previous = 0
    for row in report['phases']:
        phase = row['phase']; observed = row['observations']
        assert observed['value'] == PHASE_VALUES[phase]
        assert previous <= row['readerLogBytes'] <= len(log)
        if phase in ['increase-focused', 'decrease-focused']:
            name = 'Increase Quantity' if phase == 'increase-focused' else 'Decrease Quantity'
            assert observed['button'] == name and observed['speechOutputAndDispatcher'] is True
            assert previous <= observed['speechOffset'] <= row['readerLogBytes']
            fragment = log[observed['speechOffset']:row['readerLogBytes']].splitlines()
            assert any(b'SPEECH OUTPUT:' in line and name.encode() in line for line in fragment)
            assert any(b'SPEECH DISPATCHER: Speaking' in line and name.encode() in line for line in fragment)
        if phase in ['disabled-decrement', 'disabled-increment']:
            assert observed['remainsDisabled'] is True
            assert isinstance(observed['disabledActionBridgeReturn'], bool)
        if phase in ['keyboard-increment', 'keyboard-decrement']:
            assert observed['focused'] is True
        if phase == 'outside-edited':
            assert observed['text'] == 'Stepper reader'
        previous = row['readerLogBytes']


def speech_gap(report, log):
    """Retain the observed absence only within the measured action windows."""
    previous = 0
    for row in report['phases']:
        if row['phase'] in ['assistive-increment', 'assistive-decrement', 'lower-bound',
                            'disabled-decrement', 'upper-bound', 'disabled-increment']:
            assert b'SPEECH OUTPUT:' not in log[previous:row['readerLogBytes']]
        previous = row['readerLogBytes']


def inputs(value, installed):
    assert value['imageId'] == IMAGE and value['sourceAttempt'] == 8
    assert value['installedPrefixFiles'] == installed and len(installed) == 158
    for key in ['accepted', 'sourceProjectsMounted', 'libraryProjectMounted',
                'consumerProjectMounted', 'productBuildMounted']:
        assert value[key] is False, key
    command = value['command']
    assert command[:4] == ['docker', '--context', 'colima-avelino-verify', 'run']
    mounts = [command[index + 1] for index, word in enumerate(command) if word == '--mount']
    assert len(mounts) == 2
    assert sum('target=/package/install,readonly' in mount for mount in mounts) == 1
    assert sum(mount.endswith('target=/probe') for mount in mounts) == 1
    assert command[-3:] == [IMAGE, 'python3', '/probe/bootstrap.py']


def producer_binding(binding, producer_files):
    assert binding['sourceCommit'] == SOURCE and binding['sourceAttempt'] == 8
    assert binding['accepted'] is False and len(binding['files']) == 579
    assert binding['producerCapsule'] == str(PRODUCER.relative_to(ROOT))
    for filename, field in [('runtime-binding.json', 'producerBindingSha256'), ('validation.json', 'producerValidationSha256')]:
        assert sha((PRODUCER / filename).read_bytes()) == binding[field]
    assert binding['files'] == json.loads((PRODUCER / 'runtime-binding.json').read_text())['files']
    assert binding['files'] == {name: producer_files[name] for name in binding['files']}
    published = {}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for name in binding['files']:
            assert '\n' not in name and '\r' not in name
            process.stdin.write((SOURCE + ':' + name + '\n').encode()); process.stdin.flush()
            header = process.stdout.readline().split(); assert len(header) == 3 and header[1] == b'blob'
            published[name] = sha(process.stdout.read(int(header[2])))
            assert process.stdout.read(1) == b'\n'
        process.stdin.close(); assert process.wait() == 0
    assert binding['files'] == published


def verify():
    manifest = json.loads((DIRECTORY / 'files.json').read_text())
    assert set(manifest) == {str(path.relative_to(DIRECTORY)) for path in DIRECTORY.rglob('*')
                             if path.is_file() and path != DIRECTORY / 'files.json'}
    for name, row in manifest.items():
        value = (DIRECTORY / name).read_bytes()
        assert len(value) == row['bytes'] and sha(value) == row['sha256'], name
    capsule = Capsule(DIRECTORY)
    for name in capsule.records:
        value = capsule.raw(name)
        if value.startswith(b'\x89PNG\r\n\x1a\n'):
            with Image.open(io.BytesIO(value)) as image:
                image.load(); assert image.size == (2560, 1920)
    validation = json.loads((DIRECTORY / 'validation.json').read_text()); limits(validation)
    producer = Capsule(PRODUCER)
    package = producer.record('source8/validation/package-producer.json')
    installed = package['installedFiles']
    assert package['imageId'] == BUILD_IMAGE and package['accepted'] is False
    assert producer.record('reader6/controller/inputs.json')['imageId'] == IMAGE
    assert installed['lib/qml/Avelino/libAvelino.so'] == validation['moduleSha256']
    assert installed['bin/AvelinoCatalog'] == validation['catalogSha256']
    binding = json.loads((DIRECTORY / 'runtime-binding.json').read_text())
    old = capsule.record('reader1/controller/result.json')
    assert old['exitCode'] == 1 and old['installedPrefixUnchanged'] is old['probeSourcesUnchanged'] is True
    failed = capsule.record('reader1/output/operator-report.json')
    assert failed['status'] == 'running' and [row['phase'] for row in failed['phases']] == list(PHASE_VALUES)[:6]
    assert b'Increase Quantity named speech absent' in capsule.raw('reader1/output/exercise.log')
    assert capsule.record('reader1/output/session-result.json')['exitCode'] == 1
    for number in [1, 2, 3]:
        config = capsule.record(f'reader{number}/controller/inputs.json'); inputs(config, installed)
        for name, digest in config['probeFiles'].items():
            assert sha(capsule.raw(f'reader{number}/output/{name}')) == digest
        source = capsule.record(f'reader{number}/output/producer-inputs.json')
        producer_binding(binding, source['sourceFiles'])
        runtime = capsule.record(f'reader{number}/output/runtime-sockets.json')
        assert all(name.startswith('runtime/') for name in runtime['notCopied'])
        if number == 1:
            continue
        prefix = f'reader{number}/output/'
        result = capsule.record(f'reader{number}/controller/result.json')
        assert result['exitCode'] == 0 and result['operatorPhases'] == 13
        assert result['installedPrefixUnchanged'] is result['probeSourcesUnchanged'] is True
        assert capsule.record(prefix + 'session-result.json')['exitCode'] == 0
        assert capsule.record(prefix + 'local-execution.json')['allOutputsCopiedAfterChildrenStop'] is True
        profile = capsule.record(prefix + 'profile.json')
        assert profile == {'protocol': 'xcb' if number == 2 else 'wayland',
                           'backend': 'software' if number == 2 else 'opengl',
                           'scaled': number == 3, 'accepted': False}
        env = capsule.record(prefix + 'session-env.json')
        assert env['QT_QPA_PLATFORM'] == profile['protocol']
        assert env['QT_SCALE_FACTOR'] == ('1' if number == 2 else '2')
        client = capsule.raw(prefix + 'client.log')
        assert (b'Loading backend software' if number == 2 else b'Creating QRhi with backend OpenGL') in client
        assert b'ValueChanged event and no ValueInterface or ComboBox' in client
        commands = capsule.record(prefix + 'children-before-cleanup.json')
        command = next(row['command'] for row in commands if row['command'][0] == '/package/install/bin/AvelinoCatalog')
        assert command == ['/package/install/bin/AvelinoCatalog', '--fixture', 'stepper'] + ([] if number == 2 else ['--dark', '--text-scale', '1.5'])
        report = capsule.record(prefix + 'operator-report.json'); log = capsule.raw(prefix + 'orca-debug.log')
        reader(report, log); speech_gap(report, log)
        pid = capsule.record(prefix + 'client-pid.json')['pid']
        for row in report['phases']:
            snapshot(capsule.record(prefix + row['phase'] + '.json'), row, pid)
    spec = importlib.util.spec_from_file_location('protected', ROOT / 'scripts/verify-modal-parent-focus.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    before = module.protected_fields(json.loads(subprocess.check_output(['git', 'show', SOURCE + ':docs/parity-inventory.json'], cwd=ROOT)))
    after = module.protected_fields(json.loads((ROOT / 'docs/parity-inventory.json').read_text()))
    assert len(before) == validation['priorProtectedFields'] and all(after.get(key) == value for key, value in before.items())
    print('Stepper: two installed 13-phase reader observations verified; numeric speech and native acceptance remain unresolved')


if __name__ == '__main__':
    verify()
