#!/usr/bin/env python3
"""Audit retained DateRange assistive lifetime evidence without granting parity."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/date-range-assistive-lifetime-20261024'
PARENT = '601436f5cfb3551872ff1a397f606829cbfcba39'
PUBLISHED = '899f3e8f1fd50bcf9094d417f4c449cea651c36b'
CHANGED = ['src/Avelino/daterangeinput.cpp', 'tests/components/daterangeui.cpp',
           'tests/consumer/DateRangePicker.qml', 'tests/consumer/daterangechecks.h']
PHASES = ['caller-ready', 'leap-loaded', 'from-focused', 'from-replaced', 'to-focused',
          'to-deleted', 'to-inserted', 'ignored-edit', 'delayed-edit', 'pending-applied',
          'disabled-rejected', 'reset-focused']
digest = lambda value: hashlib.sha256(value).hexdigest()


def limits(value):
    assert value['sourceParent'] == PARENT and value['sourceAttempt'] == 8
    assert value['fullSuiteSource'] == 7 and value['ctestGroupsPassed'] == 58
    assert value['qtSuiteRerunOnCurrent'] is False
    assert value['readerAttempts'] == [6, 7] and value['readerPhases'] == [12, 12]
    assert value['displayProfiles'] == 8 and value['assistiveEditsPerProfile'] == 6
    assert value['priorProtectedFields'] == 31524
    for key in ['accepted', 'nativeRasterAccepted', 'nativeGeometryAccepted',
                'nativeReaderAccepted', 'physicalInputAccepted', 'independentMachineAccepted',
                'expectedImagesChanged', 'nativeImePreeditAccepted']:
        assert value[key] is False, key
    assert value['approvedExceptions'] == []


def comparability(value):
    assert value['fullSuiteSource'] == 7 and value['currentSource'] == 8
    assert value['qtSuiteRerunOnCurrent'] is False
    assert value['sourceDifferences'] == ['tests/consumer/DateRangePicker.qml']
    assert value['unchangedCompiledTestFiles']
    assert value['fullSuiteCommand']['name'] == 'full-ctest'
    assert value['fullSuiteCommand']['exitCode'] == 0 and value['accepted'] is False


def assistive(report):
    assert report['accepted'] is False and report['structuralChecks'] == 'passed'
    rows = report['assistiveInput']
    assert len(rows) == 6
    assert {(row['owner'], row['endpoint']) for row in rows} == {
        (owner, endpoint) for owner in ['echo', 'ignore', 'delay'] for endpoint in ['start', 'end']}
    for row in rows:
        actual = row['actual']; model = actual['model']; endpoint = row['endpoint']
        peer = 'end' if endpoint == 'start' else 'start'; index = 0 if endpoint == 'start' else 1
        assert model[endpoint] == (1680264000.625 if row['owner'] == 'echo' else 1679832000.625)
        assert model[peer] == 1679832000.625
        assert actual['displayed'][index] == 1680264000.625
        assert actual['editorText'][index] == '闰二月初十'
        assert len(model['requests']) == 1
        request = model['requests'][0]
        assert request['endpoint'] == endpoint and request['requested'] == 1680264000.625
        if row['owner'] == 'delay':
            assert model['pending'] == {endpoint: 1680264000.625}
        else:
            assert model['pending'] == {}


def reader(report, log):
    assert report['status'] == 'passed' and report['accepted'] is False
    assert report['physicalInput'] is report['nativeReaderAcceptance'] is False
    assert [row['phase'] for row in report['phases']] == PHASES
    rows = {row['phase']: row for row in report['phases']}
    for phase, name in [('from-focused', 'From'), ('to-focused', 'To'), ('reset-focused', 'From')]:
        row = rows[phase]; data = row['observations']
        assert data['speechOutputAndDispatcher'] is True
        assert data['peerFocusBeforeProbe'] == ('To' if name == 'From' else 'From')
        fragment = log[data['speechOffset']:row['readerLogBytes']].splitlines()
        assert any(b'SPEECH OUTPUT:' in line and name.encode() in line for line in fragment)
        assert any(b'SPEECH DISPATCHER: Speaking' in line and name.encode() in line for line in fragment)
    a = rows['from-replaced']['observations']; b = rows['to-inserted']['observations']
    assert a['fromText'] == b['fromText'] == '闰二月初十'
    assert b['toText'] == '闰二月初六' and a['owner']['From'] == b['owner']['From']
    assert rows['ignored-edit']['observations']['fromText'] == '闰二月初七'
    assert rows['ignored-edit']['observations']['owner'] == b['owner']
    a = rows['delayed-edit']['observations']; b = rows['pending-applied']['observations']
    assert a['fromText'] == b['fromText'] == '\u20073/11/2024'
    assert a['owner']['From'] != b['owner']['From'] and a['owner']['To'] == b['owner']['To']
    c = rows['disabled-rejected']['observations']
    assert c['fromText'] == b['fromText'] and c['owner'] == b['owner']


def verify():
    manifest = json.loads((DIRECTORY / 'files.json').read_text())
    assert set(manifest) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*')
                             if p.is_file() and p != DIRECTORY / 'files.json'}
    for name, row in manifest.items():
        value = (DIRECTORY / name).read_bytes()
        assert len(value) == row['bytes'] and digest(value) == row['sha256'], name
    records = json.loads((DIRECTORY / 'records.json').read_text())

    def raw(name):
        row = records[name]; path = DIRECTORY / row['stored']; value = path.read_bytes()
        if path.suffix == '.gz':
            value = gzip.decompress(value)
        assert len(value) == row['bytes'] and digest(value) == row['sha256'], name
        assert not value.startswith((b'\x7fELF', b'\xcf\xfa\xed\xfe'))
        return value

    def record(name):
        return json.loads(raw(name))

    for name in records:
        raw(name)
    validation = json.loads((DIRECTORY / 'validation.json').read_text()); limits(validation)
    for number in [1, 3]:
        assert record(f'source{number}/result.json')['exitCode'] == 139
        assert record(f'source{number}/result.json')['sourceUnchanged'] is True
        assert b'Received signal 11 (SIGSEGV)' in raw(f'source{number}/date-assistive-destruction.log')
    assert record('source2/result.json')['exitCode'] == 1
    assert record('source2/qualification.json')['applicationExecuted'] is False
    assert record('source2/qualification.json')['configureExecuted'] is False
    assert record('source2/commands.json')[0]['exitCode'] == 1
    original = subprocess.check_output(['git', 'show', PARENT + ':src/Avelino/daterangeinput.cpp'], cwd=ROOT)
    assert raw('source1/implementation/src/Avelino/daterangeinput.cpp') == original
    assert raw('source3/implementation/src/Avelino/daterangeinput.cpp') != original
    for number in [4, 5, 6, 7, 8]:
        result = record(f'source{number}/result.json')
        assert result['exitCode'] == 0 and result['sourceUnchanged'] is True
        assert all(row['exitCode'] == 0 for row in record(f'source{number}/commands.json'))
    assert record('source7/validation/result.json')['exitCode'] == 0
    log = raw('source7/validation/full-ctest.log').decode()
    assert '100% tests passed, 0 tests failed out of 58' in log
    date_log = raw('source7/validation/full-last-test.log').decode()
    blocks = re.findall(r'\*+ Start testing of DateRangeUiTests \*+.*?\*+ Finished testing of DateRangeUiTests \*+', date_log, re.S)
    assert len(blocks) == 2
    for block in blocks:
        for name, count in [('assistiveSelectionAllowsSynchronousDestruction', 10), ('assistiveEditsRespectOwners', 12),
                            ('assistiveSelectionCallbacksCancelStaleReplacement', 4), ('assistiveReplacementRetainsQtEditHistory', 1)]:
            assert len(re.findall(r'PASS\s+: DateRangeUiTests::' + name + r'\(', block)) == count
        assert '0 failed, 0 skipped' in block
    current = record('source8/validation/result.json')
    assert current['exitCode'] == 0 and current['sourceUnchanged'] is current['installedPrefixUnchanged'] is True
    assert current['fullSuiteSource'] == 7 and current['qtSuiteRerunOnCurrent'] is False
    assert current['librarySha256'] == validation['moduleSha256']
    assert current['consumerSha256'] == validation['consumerSha256']
    reuse = record('source8/validation/source7-suite-comparability.json'); comparability(reuse)
    assert reuse['fullSuiteLogSha256'] == digest(raw('source7/validation/full-ctest.log'))
    assert reuse['librarySha256'] == validation['moduleSha256']
    assert all(row['exitCode'] == 0 for row in record('source8/validation/commands.json'))
    assistive(record('package/date-runtime.json'))
    for protocol in ['xcb', 'wayland']:
        for backend in ['software', 'opengl']:
            for profile in ['standard', 'scaled']:
                report = record(f'package/date-display-v1/{protocol}-{backend}-{profile}.json'); assistive(report)
                assert report['platform'] == protocol and report['graphicsApi'] == (1 if backend == 'software' else 3)
                assert report['dpr'] == (1 if profile == 'standard' else 2)
                assert report['textScale'] == (1 if profile == 'standard' else 1.5)
                assert len(report['closed']) == 48 and len(report['literalInput']) == 16
    for number in [1, 2, 3, 4, 5]:
        assert record(f'reader{number}/controller/result.json')['exitCode'] == 1
    assert record('reader5/output/session-result.json')['exitCode'] == 0
    assert record('reader5/output/operator-report.json')['status'] == 'passed'
    assert b'speechd.sock' in raw('reader5/controller/run.log')
    for number in [6, 7]:
        result = record(f'reader{number}/controller/result.json')
        assert result['exitCode'] == 0 and result['operatorPhases'] == 12
        assert result['installedPrefixUnchanged'] is result['probeSourcesUnchanged'] is True
        reader(record(f'reader{number}/output/operator-report.json'), raw(f'reader{number}/output/orca-debug.log'))
        assert all(name.startswith('runtime/') for name in record(f'reader{number}/output/runtime-sockets.json')['notCopied'])
    binding = json.loads((DIRECTORY / 'runtime-binding.json').read_text())
    assert binding['sourceParent'] == PARENT and binding['sourceAttempt'] == 8 and len(binding['files']) == 579
    base, published = {}, {}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for revision, target in [(PARENT, base), (PUBLISHED, published)]:
            for name in binding['files']:
                process.stdin.write((revision + ':' + name + '\n').encode()); process.stdin.flush()
                header = process.stdout.readline().split(); assert len(header) == 3 and header[1] == b'blob'
                target[name] = digest(process.stdout.read(int(header[2]))); assert process.stdout.read(1) == b'\n'
        process.stdin.close(); assert process.wait() == 0
    assert binding['changesFromParent'] == sorted(CHANGED)
    assert sorted(name for name in binding['files'] if binding['files'][name] != base[name]) == sorted(CHANGED)
    assert binding['files'] == published
    source_files = record('source8/inputs.json')['sourceFiles']
    assert binding['files'] == {name: source_files[name] for name in binding['files']}
    spec = importlib.util.spec_from_file_location('date_protected_fields', ROOT / 'scripts/verify-modal-parent-focus.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    before = module.protected_fields(json.loads(subprocess.check_output(['git', 'show', PARENT + ':docs/parity-inventory.json'], cwd=ROOT)))
    after = module.protected_fields(json.loads((ROOT / 'docs/parity-inventory.json').read_text()))
    assert len(before) == 31524 and all(after.get(key) == value for key, value in before.items())
    print('DateRange assistive lifetime: retained crashes, current Qt/consumer/display/reader evidence verified; native acceptance pending')


if __name__ == '__main__':
    verify()
