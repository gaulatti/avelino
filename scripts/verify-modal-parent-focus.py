#!/usr/bin/env python3
"""Audit the Modal keyboard-focus readiness repair and retained CI failure."""
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/modal-parent-focus-20261022'
PARENT = '6f16b95ad9f9d4e54f8be6c2fb82777d13e8d31a'
MODULE = '05812d809de4187acdc4f40886cf5ce644e2fbe977eee8dec119681187ae9acb'
CONSUMER = '88d98dcdaa4c3adada4e8519bdeee81029d231d7c320ad1482073caec0549b70'
digest = lambda value: hashlib.sha256(value).hexdigest()


def protected_fields(value, path=''):
    result = {}
    if isinstance(value, dict):
        for key, item in value.items():
            if key == 'status' or any(s in key.lower() for s in ['accept', 'capture', 'reference', 'toleran', 'exception', 'mask', 'comparison']):
                result[path + '/' + key] = item
            else:
                result.update(protected_fields(item, path + '/' + key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            result.update(protected_fields(item, path + '/' + str(index)))
    return result


def limits(report):
    assert report['sourceParent'] == PARENT
    assert report['currentAttempt'] == 5 and report['displayProfiles'] == 8
    assert report['availableFileInputPhases'] == 14
    assert report['moduleSha256'] == MODULE and report['consumerSha256'] == CONSUMER
    assert report['priorLinuxConclusion'] == 'failure' and report['priorReferencesConclusion'] == 'success'
    assert report['priorX86Full58Passed'] is report['priorArmFull58Passed'] is True
    for key in ['accepted', 'applicationSourcesChanged', 'expectedImagesChanged',
                'nativeRasterAccepted', 'nativeFocusAccepted', 'readerAccepted',
                'physicalInputAccepted', 'independentMachineAccepted', 'priorX86SessionAccepted']:
        assert report[key] is False, key
    assert report['approvedExceptions'] == []


def focus_report(report):
    assert report['accepted'] is False and report['nativeTypingAcceptance'] == 'pending'
    assert report['modalChecks'] == report['focusChecks'] == report['callerStateChecks'] == 'passed'
    assert report['qtEditorChecks'] == report['qtAccessibilityChecks'] == 'passed'
    assert report['qtEditedAndReopenedValue'] == 'q' and report['separatePresentationWindow'] is True
    assert report['nativeSnapshots'] == 80 and report['clippingQueries'] == 170 and report['glyphQueries'] == 142
    transitions = report['focusTransitions']
    negative = [row for row in transitions if row['phase'] == 'sheet-focus-negative-control']
    assert len(negative) == 11
    assert all(row['parentChainActive'] and row['sheetIsFocusWindow'] and row['parentKeyboardReady'] is False for row in negative)
    positive = [row for row in transitions if row['phase'] != 'sheet-focus-negative-control']
    assert all(row['parentIsFocusWindow'] and row['parentRootActiveFocus'] for row in positive)
    assert {'after-sheet-close', 'before-parent-traversal', 'before-gallery-editor'} <= {row['phase'] for row in positive}


def verify():
    files = json.loads((DIRECTORY / 'files.json').read_text())
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        value = (DIRECTORY / name).read_bytes()
        assert len(value) == row['bytes'] and digest(value) == row['sha256'], name
    records = json.loads((DIRECTORY / 'records.json').read_text())
    used = set()
    def raw(name):
        row = records[name]
        assert row['stored'] in files
        used.add(row['stored'])
        value = (DIRECTORY / row['stored']).read_bytes()
        if row['stored'].endswith('.gz'):
            value = gzip.decompress(value)
        assert digest(value) == row['sha256'] and len(value) == row['bytes'], name
        assert Path(row['stored']).stem == row['sha256'] and not value.startswith(b'\x7fELF')
        return value
    record = lambda name: json.loads(raw(name))
    for name in records:
        raw(name)
    assert used == {name for name in files if name.startswith(('blobs/', 'images/'))}
    report = json.loads((DIRECTORY / 'validation.json').read_text())
    limits(report)
    ci = record('ci/ci-state.json')
    assert ci['head'] == ci['references']['head'] == PARENT
    assert ci['conclusion'] == 'failure' and ci['references']['conclusion'] == 'success'
    jobs = {row['id']: row for row in ci['jobs']}
    assert jobs[119538478376]['conclusion'] == 'failure'
    assert jobs[119538478376]['failedSteps'] == ['Consumer with source and build trees absent']
    assert jobs[119538478635]['conclusion'] == 'success'
    for name in ['ci/failed.log', 'ci/arm-job.log']:
        assert b'100% tests passed, 0 tests failed out of 58' in raw(name)
    assert b'Installed Modal: Parent Close focus and caller traversal availability' in raw('ci/failed.log')
    assert b'Installed consumer exited with status 255' in raw('ci/failed.log')
    assert ci['artifact']['sha256'] == '2539b5bb1bb01146dda57b4d077d6a4b3768d553b1ab02005694caddbf6d207b'

    frozen = json.loads((DIRECTORY / 'compiled-inputs.json').read_text())
    sources = {n: record(f'attempt{n}/controller/inputs.json') for n in range(1, 6)}
    names = set(frozen['files']) | {'tests/consumer/' + name for source in sources.values() for name in source['sourceFiles']}
    base = {}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for name in sorted(names):
            assert not Path(name).is_absolute() and '..' not in Path(name).parts and '\n' not in name
            process.stdin.write((PARENT + ':' + name + '\n').encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            assert len(header) == 3 and header[1] == b'blob', name
            base[name] = digest(process.stdout.read(int(header[2])))
            assert process.stdout.read(1) == b'\n'
        process.stdin.close()
        assert process.wait() == 0
    for n in range(1, 6):
        prefix = f'attempt{n}/'
        inputs = sources[n]
        assert inputs['moduleSha256'] == MODULE
        assert record(prefix + 'controller/build-result.json')['exitCode'] == 0
        for name, expected in inputs['sourceFiles'].items():
            if name == 'modalchecks.h':
                assert digest(raw(prefix + 'source/modalchecks.h')) == expected
            else:
                assert base['tests/consumer/' + name] == expected, (n, name)
    for n in [2, 3]:
        result = record(f'attempt{n}/controller/result.json')
        assert result['attempts'] == 3 and result['failed'] == 0
        assert all(row['exitCode'] == 0 for row in record(f'attempt{n}/controller/commands.json'))
    negative = record('attempt4/controller/commands.json')
    assert len(negative) == 1 and negative[0]['exitCode'] == 255
    assert b'Transient sheet focus satisfied parent keyboard readiness' in raw('attempt4/proof/replay1.log')
    observations = []
    for attempt in [2, 3]:
        for n in range(1, 4):
            for line in raw(f'attempt{attempt}/proof/replay{n}.log').splitlines():
                if line.startswith(b'MODAL_PARENT_FOCUS '):
                    observations.append(json.loads(line.split(b' ', 1)[1]))
    assert any(row['parentActive'] and not row['parentIsFocusWindow'] for row in observations)

    inputs = record('attempt5/controller/inputs.json')
    runtime = record('attempt5/controller/runtime-inputs.json')
    result = record('attempt5/controller/validation-result.json')
    assert result['exitCode'] == 0 and result['runtimeFilesUnchanged'] is True
    assert result['consumerSha256'] == CONSUMER and result['moduleSha256'] == MODULE
    for key in ['libraryProjectMounted', 'consumerProjectMounted', 'productBuildMounted']:
        assert result[key] is runtime[key] is False
    mapping = runtime['runtimeFiles']
    assert len(mapping) == 162 and mapping['consumer-build/InstalledConsumer'] == CONSUMER
    assert {name[8:]: value for name, value in mapping.items() if name.startswith('install/')} == inputs['installedPrefixFiles']
    assert len(inputs['installedPrefixFiles']) == 158
    assert mapping['install/lib/qml/Avelino/libAvelino.so'] == MODULE
    published_records = json.loads(subprocess.check_output([
        'git', 'show', PARENT + ':evidence/development/file-input-search-atomic-integration-20261021/records.json'
    ], cwd=ROOT))
    assert digest(raw('previous/source47-prefix.json')) == published_records['source47/installed-prefix.json']['sha256']
    assert record('previous/source47-prefix.json') == inputs['installedPrefixFiles']
    commands = record('attempt5/controller/validation-commands.json')
    assert len(commands) == 5 and all(row['exitCode'] == 0 for row in commands)
    for row in commands:
        command = row['command']
        mounts = [command[i + 1] for i, value in enumerate(command) if value == '--mount']
        assert len(mounts) == 2 and ',target=/package,readonly' in mounts[0] and ',target=/proof' in mounts[1]
    profiles = [name for name in records if name.startswith('attempt5/proof/display/modal-') and name.endswith('.json')]
    assert len(profiles) == 8
    for name in profiles:
        value = record(name)
        focus_report(value)
        assert value['qt'] == '6.8.3' and value['physicalDisplay'] is value['hardwareAcceleration'] is False
        prefix = name[:-5]
        assert digest(raw(prefix + '.png')) == value['windowCaptureSha256']
        assert digest(raw('attempt5/proof/display/' + value['sessionCapture'])) == value['sessionCaptureSha256']
        assert struct.unpack('>II', raw(prefix + '.png')[16:24]) == (value['width'] * value['dpr'], value['height'] * value['dpr'])
    available = record('attempt5/proof/file-search-available.json')
    assert len(available['phases']) == 14 and available['accepted'] is False
    for phase in ['compound-mixed', 'compound-everything', 'compound-undo']:
        assert next(row for row in available['phases'] if row['phase'] == phase)['names'] == ['pine-only.txt']
    assert record('attempt5/proof/file-search-unavailable.json')['providerUnavailable'] is True
    assert len(frozen['files']) == 599 and frozen['sourceParent'] == PARENT
    assert frozen['differencesFromPublished47'] == ['tests/consumer/modalchecks.h']
    for name, expected in frozen['files'].items():
        actual = digest(raw('attempt5/source/modalchecks.h')) if name == 'tests/consumer/modalchecks.h' else base[name]
        assert actual == expected, name
    assert digest(raw('attempt5/source/modalchecks.h')) == inputs['sourceFiles']['modalchecks.h']
    assert b'counter->hasActiveFocus()' in raw('attempt5/source/modalchecks.h')
    assert b'Qt::Key_Backtab' in raw('attempt5/source/modalchecks.h')
    invariance = json.loads((DIRECTORY / 'inventory-invariance.json').read_text())
    before = protected_fields(json.loads(subprocess.check_output(['git', 'show', PARENT + ':docs/parity-inventory.json'], cwd=ROOT)))
    after = protected_fields(record('candidate/docs/parity-inventory.json'))
    assert invariance['base'] == PARENT and invariance['existingProtectedFields'] == len(before) == 31503
    assert all(name in after and after[name] == value for name, value in before.items())
    print('Modal parent focus: retained x86 failure, three diagnostic replays, actual transient negative control and eight current source-free profiles verified; native acceptance remains pending')


if __name__ == '__main__':
    verify()
