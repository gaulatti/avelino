#!/usr/bin/env python3
"""Audit integrated atomic-search evidence without promoting native acceptance."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/file-input-search-atomic-integration-20261021'
NATIVE = ROOT / 'evidence/reference-investigations/file-input-search-atomic-20261021'
PARENT = '8fc387453b53a8c12c2e3d5ce70e29d11beb0ebf'
MODULE = '05812d809de4187acdc4f40886cf5ce644e2fbe977eee8dec119681187ae9acb'
CONSUMER = 'ad67695c70c75f0722f37e3f603ef4973dbea6a2c29ccb5429792a257f2b0a6f'
CATALOG = 'fc33a75d393ca924170360c16c3c7697a8068c86fd300c59f3c277f00b7d494d'
PREVIOUS_MODULE = 'f33140033d4f81fd73182439b521886b03cfdabb17d2edc182548fdb82a2e44c'
PHASES = ['global', 'folder', 'filename', 'token-replacement', 'token-undo',
          'token-redo', 'compound-mixed', 'compound-everything',
          'compound-replacement', 'compound-undo', 'compound-redo', 'selected',
          'owner-result', 'cancelled-query']
READER_PHASES = ['caller-ready', 'global-results', 'filename-token',
                 'filename-token-menu', 'everything-token-menu',
                 'token-replacement', 'token-undo', 'token-redo', 'everything-folder',
                 'compound-draft', 'compound-filename', 'compound-token-menu',
                 'compound-everything', 'compound-replacement', 'compound-undo',
                 'compound-redo', 'compound-assistive-delete', 'compound-delete-undo',
                 'offscreen-selection', 'multiple-selection', 'focused-result-speech',
                 'keyboard-result-speech', 'owner-result', 'editable-text-query',
                 'editable-text-undo-redo', 'cancel-preserves-owner']
digest = lambda value: hashlib.sha256(value).hexdigest()


def audit_files(directory):
    files = json.loads((directory / 'files.json').read_text())
    assert set(files) == {str(p.relative_to(directory)) for p in directory.rglob('*')
                          if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        value = (directory / name).read_bytes()
        assert len(value) == row['bytes'] and digest(value) == row['sha256'], name
    return files


def protected_fields(value, path=''):
    result = {}
    if isinstance(value, dict):
        for key, item in value.items():
            if key == 'status' or any(s in key.lower() for s in
                    ['accept', 'capture', 'reference', 'toleran', 'exception', 'mask', 'comparison']):
                result[path + '/' + key] = item
            else:
                result.update(protected_fields(item, path + '/' + key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            result.update(protected_fields(item, path + '/' + str(index)))
    return result


def candidate_limits(report):
    for key in ['nativeLibraryIndependentlyRebuilt', 'nativeKeyboardRoutingEstablished',
                'nativeReadinessAccepted', 'nativeRasterAccepted', 'nativeReaderAccepted',
                'completeA11yEventDeliveryAccepted', 'physicalInputAccepted',
                'independentMachineAccepted', 'expectedImagesChanged', 'accepted']:
        assert report[key] is False, key
    assert report['approvedExceptions'] == [] and report['prototypeOnly'] is False
    assert report['currentSourceAttempt'] == 47 and report['sourceParent'] == PARENT
    assert report['full58ExecutedOnSource'] == 45 and report['full58Groups'] == 58
    assert report['currentFocusedGroups'] == 9
    assert report['currentIndexedCasesPassed'] == 23 and report['currentIndexedCasesSkipped'] == 1
    assert report['readerAttempts'] == [17, 18] and report['readerSourceAttempt'] == 47
    assert report['historicalReaderAttempts'] == [15, 16] and report['historicalReaderSource'] == 45
    assert report['readerPhasesEach'] == 26 and report['availableConsumerPhases'] == 14
    assert report['portableAttempt'] == report['closedAttempt'] == 9
    assert report['portableSource'] == 47 and report['displayProfiles'] == 8
    assert report['displayPhasesEach'] == 15 and report['closedPairs'] == 256
    assert report['allSelected45and46InputsIdentical'] is False
    assert (report['moduleSha256'], report['consumerSha256'], report['catalogSha256']) == (MODULE, CONSUMER, CATALOG)
    assert report['remaining']


def absent_projects(report):
    for key in ['libraryProjectMounted', 'consumerProjectMounted', 'productBuildMounted']:
        assert report[key] is False, key


def bind_mounts(command):
    result = {}
    for index, argument in enumerate(command):
        if argument == '--mount':
            fields = dict(part.split('=', 1) for part in command[index + 1].split(',') if '=' in part)
            assert fields['type'] == 'bind' and fields['target'] not in result
            result[fields['target']] = fields['source']
        assert argument not in ['-v', '--volume'], 'Source-free receipts use explicit bind mounts'
    return result


def phase_checks(report, display=False):
    assert report['accepted'] is False
    for key in ['nativeRasterAccepted', 'readerAcceptance', 'physicalInput']:
        assert report[key] is False
    assert [row['phase'] for row in report['phases']] == PHASES + (['session-selected'] if display else [])
    phases = {row['phase']: row for row in report['phases']}
    assert all(not row['busy'] and not row['error'] for row in phases.values())
    token = lambda mode, query: {'kind': 'token', 'mode': mode, 'query': query}
    first = token('everything', 'avelinoulnacerulean')
    for name, mode in [('compound-mixed', 'filename'), ('compound-everything', 'everything'),
                       ('compound-undo', 'everything'), ('selected', 'everything')]:
        row = phases[name]
        assert row['expression'] == [first, token(mode, 'pine')], name
        assert row['names'] == ['pine-only.txt'] and row['folderOnly'] is True, name
        assert row['editorText'] == '\ufffc\ufffc', name
    for name in ['compound-replacement', 'compound-redo']:
        row = phases[name]
        assert row['expression'] == [{'kind': 'text', 'text': 'name'}, token('everything', 'pine')]
        assert row['editorText'] == 'name\ufffc'
    assert phases['compound-undo']['selectedText'] == '\ufffc'
    owner = phases['owner-result']['state']
    assert owner['pickerVisible'] is False and owner['visibleAtCallback'] is True
    assert len(owner['results']) == 1 and owner['results'][0]['kind'] == 'success'
    assert len(owner['results'][0]['urls']) == 1 and owner['results'][0]['urls'][0].endswith('/inside/pine-only.txt')
    assert phases['cancelled-query']['state']['results'] == owner['results']


def verify():
    files = audit_files(DIRECTORY)
    records = json.loads((DIRECTORY / 'records.json').read_text())
    used = set()
    def raw(name):
        row = records[name]
        stored = row['stored']
        assert stored in files
        used.add(stored)
        payload = (DIRECTORY / stored).read_bytes()
        value = gzip.decompress(payload) if stored.endswith('.gz') else payload
        assert digest(value) == row['sha256'] and len(value) == row['bytes'], name
        assert Path(stored).stem == row['sha256'] and not value.startswith(b'\x7fELF'), name
        return value
    record = lambda name: json.loads(raw(name))
    for name in records:
        raw(name)
    assert used == {name for name in files if name.startswith(('images/', 'blobs/'))}
    report = json.loads((DIRECTORY / 'validation.json').read_text())
    candidate_limits(report)
    audit_files(NATIVE)
    native_manifest = (NATIVE / 'files.json').read_bytes()
    assert raw('native-manifest.json') == native_manifest
    assert digest(native_manifest) == report['nativeManifestSha256']
    assert native_manifest == subprocess.check_output(
        ['git', 'show', PARENT + ':' + str((NATIVE / 'files.json').relative_to(ROOT))], cwd=ROOT)

    specs = json.loads((DIRECTORY / 'source-overrides.json').read_text())
    sources = {n: record(f'source{n}/controller/inputs.json') for n in range(41, 48)}
    names = sorted(set().union(*(set(source['sourceFiles']) for source in sources.values())))
    base = {}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for name in names:
            assert not Path(name).is_absolute() and '..' not in Path(name).parts and '\n' not in name
            process.stdin.write((PARENT + ':' + name + '\n').encode())
            process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) == 3 and header[1] == b'blob':
                base[name] = digest(process.stdout.read(int(header[2])))
                assert process.stdout.read(1) == b'\n'
            else:
                assert header[-1] == b'missing'
                base[name] = None
        process.stdin.close()
        assert process.wait() == 0
    for n, source in sources.items():
        spec = specs[str(n)]
        assert source['parent'] == spec['parent'] == PARENT
        assert len(source['sourceFiles']) == spec['selectedFiles']
        assert set(spec['overrides']) == {name for name, expected in source['sourceFiles'].items() if base[name] != expected}
        for name, expected in source['sourceFiles'].items():
            actual = digest(raw(f'source{n}/overrides/' + name)) if name in spec['overrides'] else base[name]
            assert actual == expected, (n, name)
        result = record(f'source{n}/controller/result.json')
        assert result['accepted'] is False and result['sourceUnchanged'] is True
        expected_exit = {41: 8, 42: 8, 43: 1, 44: 8}.get(n, 0)
        assert result['exitCode'] == expected_exit
        commands = record(f'source{n}/controller/commands.json')
        assert commands[0]['exitCode'] == 0
        assert next(row for row in commands if row['name'] == 'build')['exitCode'] == (1 if n == 43 else 0)
        if n == 43:
            assert f'source{n}/binary.json' not in records
        else:
            assert record(f'source{n}/binary.json')['binaryPublished'] is False
    assert len(re.findall(rb'^FAIL!', raw('source41/controller/search-dpr1.log'), re.M)) == 3
    assert b'15 passed, 3 failed, 1 skipped' in raw('source41/controller/search-dpr1.log')
    assert b'clientExitCode": 139' in raw('source42/controller/search-dpr1.log')
    assert b'QAccessibleInterface::actionInterface' in raw('debug2/debug.log') and b'SIGSEGV' in raw('debug2/debug.log')
    assert record('debug2/result.json')['gdbProcessExitCode'] == 0
    assert b'final' in raw('source43/controller/build.log')
    assert b'21 passed, 1 failed, 1 skipped' in raw('source44/controller/search-dpr1.log')
    assert b'23 passed, 0 failed, 1 skipped' in raw('source47/controller/search-dpr1-raw.log')
    for name in ['light', 'dark']:
        assert f'atomicReplacementSelectionUndoAndHistory({name})'.encode() in raw('source47/controller/search-dpr1-raw.log')
    assert report['negativeSource41ExitCode'] == report['crashSource42ExitCode'] == report['assistiveDeletionSource44ExitCode'] == 8
    assert report['registrationSource43ExitCode'] == 1

    prefixes = {}
    for n in [45, 46, 47]:
        prefix = f'source{n}/controller/validation/'
        module = MODULE if n == 47 else PREVIOUS_MODULE
        for name in ['result.json', 'focused/result.json', 'consumer/result.json']:
            assert record(prefix + name)['exitCode'] == 0
        assert b'100% tests passed, 0 tests failed out of 9' in raw(prefix + 'focused/runtime.log')
        producer = record(prefix + 'package-producer.json')
        assert producer['librarySha256'] == module and producer['sourceParent'] == PARENT
        assert producer['accepted'] is False
        for name, expected in producer['consumerSourceFiles'].items():
            assert digest(raw(f'source{n}/package/consumer/' + name)) == expected
            assert sources[n]['sourceFiles']['tests/consumer/' + name] == expected
        transformation = record(f'source{n}/install-rpath-transformation.json')
        assert transformation['builtModuleSha256'] == record(f'source{n}/binary.json')['moduleSha256']
        assert transformation['installedModuleSha256'] == transformation['normalizedBuiltSha256'] == module
        assert transformation['sourceAttempt'] == n and transformation['binaryPublished'] is False
        assert transformation['sameByteLength'] is transformation['zeroPadded'] is transformation['allOtherBytesIdentical'] is True
        assert transformation['oldRpath'] == '/opt/qt/lib:' and transformation['installedRpath'] == '$ORIGIN'
        install_script = raw(f'source{n}/cmake-install.cmake')
        assert b'OLD_RPATH "/opt/qt/lib:"' in install_script and b'NEW_RPATH "\\$ORIGIN"' in install_script
        prefixes[n] = record(f'source{n}/installed-prefix.json')
        assert len(prefixes[n]) == 158 and prefixes[n]['lib/qml/Avelino/libAvelino.so'] == module
        assert prefixes[n]['bin/AvelinoCatalog'] == CATALOG
        consumer = record(prefix + 'consumer/result.json')
        assert consumer['consumerSha256'] == CONSUMER and consumer['moduleHashes']['libAvelino.so'] == module
        phase_checks(consumer['availableReport'])
        assert consumer['unavailableReport']['providerUnavailable'] is True
        for command in record(prefix + 'consumer/commands.json'):
            assert command['exitCode'] == 0
        if n == 45:
            correction = record(prefix + 'consumer/mount-scope-correction.json')
            assert correction['rawResultSha256'] == digest(raw(prefix + 'consumer/result.json'))
            assert correction['rawResultUnmodified'] is True and correction['correctValue'] is True
            assert correction['libraryProjectMounted'] is False and correction['productionConsumerProjectMounted'] is True
            assert correction['bothProductionProjectsAbsent'] is False
        else:
            assert consumer['sourceProjectsMounted'] is True and consumer['productionConsumerProjectMounted'] is True
            assert consumer['libraryProjectMounted'] is consumer['productBuildMounted'] is consumer['bothProductionProjectsAbsent'] is False
    assert record('source45/controller/validation/ctest/result.json')['exitCode'] == 0
    assert b'100% tests passed, 0 tests failed out of 57' in raw('source45/controller/validation/ctest/full-remaining-tests.log')
    assert not any(name.startswith('source47/controller/validation/ctest/') for name in records)
    identity = record('source46/controller/validation/runtime-identity-v45-v46.json')
    differences = {name: {'45': sources[45]['sourceFiles'].get(name), '46': sources[46]['sourceFiles'].get(name)}
                   for name in set(sources[45]['sourceFiles']) | set(sources[46]['sourceFiles'])
                   if sources[45]['sourceFiles'].get(name) != sources[46]['sourceFiles'].get(name)}
    assert set(differences) == {'docs/file-input-search.md', 'docs/parity-inventory.json', 'scripts/check-display-sessions-file-search.sh'}
    assert identity['selectedSourceInputDifferences'] == differences
    assert identity['allSelectedSourceInputsIdentical'] is identity['executionsRelabelled'] is False
    assert identity['allInstalledPrefixBytesIdentical'] is True
    assert all(sources[45]['sourceFiles'][name] == sources[46]['sourceFiles'][name]
               for name in sources[45]['sourceFiles'] if name.startswith(('src/', 'tests/components/', 'tests/consumer/')))
    runtime_changes = {name for name in sources[47]['sourceFiles']
                       if name.startswith(('src/', 'tests/')) and sources[46]['sourceFiles'].get(name) != sources[47]['sourceFiles'][name]}
    assert runtime_changes == {'src/Avelino/FileChooserSearchInput.qml', 'tests/components/filesearch.cpp'}
    measurements = record('source46/controller/validation/installed-prefix-hash-measurements-v45-v46.json')['filesBySource']
    assert measurements['45'] == measurements['46'] == prefixes[45] == prefixes[46]

    for attempt, source_number in [(15, 45), (16, 45), (17, 47), (18, 47)]:
        prefix = f'reader{attempt}/'
        inputs, result = record(prefix + 'controller/inputs.json'), record(prefix + 'controller/result.json')
        module = MODULE if source_number == 47 else PREVIOUS_MODULE
        assert inputs['sourceAttempt'] == result['sourceAttempt'] == source_number
        assert inputs['moduleSha256'] == module and inputs['catalogSha256'] == result['catalogSha256'] == CATALOG
        assert inputs['installedPrefixFiles'] == prefixes[source_number]
        absent_projects(inputs)
        mounts = bind_mounts(inputs['command'])
        assert mounts == {'/package/install': sources[source_number]['output'] + '/package/install',
                          '/probe': str(Path(sources[source_number]['output']).parent / f'file-search-a11y-v{attempt}')}
        assert result['exitCode'] == 0 and result['operatorPhases'] == 26
        assert result['installedModuleUnchanged'] is result['installedPrefixUnchanged'] is result['probeSourcesUnchanged'] is True
        for name, expected in inputs['probeFiles'].items():
            assert digest(raw(prefix + 'output/' + name)) == expected
        operator = record(prefix + 'output/operator-report.json')
        assert operator['status'] == 'passed' and [p['phase'] for p in operator['phases']] == READER_PHASES
        for key in ['accepted', 'physicalInput', 'readerNativeComparisonAccepted', 'speechEngineAudioAccepted']:
            assert operator[key] is False
        phases = {row['phase']: row for row in operator['phases']}
        for name in ['compound-filename', 'compound-everything']:
            assert phases[name]['observations']['names'] == ['pine-only.txt']
        for name in ['compound-undo', 'compound-delete-undo']:
            assert phases[name]['observations']['text'] == '\ufffc\ufffc'
            assert phases[name]['observations']['selectedRange'] == [0, 1]
        assert phases['compound-assistive-delete']['observations']['text'] == '\ufffc'
        speech = raw(prefix + 'output/orca-debug.log')
        for name, target in [('focused-result-speech', 'pine-only.txt'),
                             ('keyboard-result-speech', 'avelinoulnacerulean-name.txt')]:
            phase = phases[name]
            window = speech[phase['observations']['speechOffset']:phase['readerLogBytes']]
            for marker in [b'SPEECH OUTPUT:', b'SPEECH DISPATCHER: Speaking']:
                assert any(marker in line and target.encode() in line for line in window.splitlines())
        caches = record(prefix + 'generated-caches.json')
        assert caches['originalFilesUnchanged'] is True
        assert all(row['name'] not in inputs['probeFiles'] and row['name'].endswith('.pyc') for row in caches['undeclaredGeneratedCaches'])

    for attempt, source_number in [(8, 46), (9, 47)]:
        prefix = f'portable{attempt}/'
        result, inputs = record(prefix + 'controller/result.json'), record(prefix + 'controller/inputs.json')
        module = MODULE if source_number == 47 else PREVIOUS_MODULE
        assert result['exitCode'] == 0 and result['sourceAttempt'] == source_number
        assert result['moduleSha256'] == inputs['moduleSha256'] == module
        assert result['consumerSha256'] == inputs['consumerSha256'] == CONSUMER
        assert result['runtimeFilesUnchanged'] is True
        absent_projects(result)
        absent_projects(inputs)
        portable_root = Path(sources[source_number]['output']).parent / f'file-search-portable-v{attempt}'
        assert bind_mounts(inputs['commandPrefix']) == {'/package': str(portable_root / 'runtime'), '/proof': str(portable_root / 'proof')}
        mapping = inputs['runtimeFiles']
        assert len(mapping) == 162 and mapping['consumer-build/InstalledConsumer'] == CONSUMER
        assert {name[8:]: value for name, value in mapping.items() if name.startswith('install/')} == prefixes[source_number]
        for name in ['run-file-search.py', 'check-display-sessions-file-search.sh', 'environment.json']:
            assert digest(raw(prefix + 'runtime/' + name)) == mapping[name]
        for row in record(prefix + 'controller/commands.json'):
            assert row['exitCode'] == 0
        phase_checks(record(prefix + 'output/available.json'))
        profiles = [name for name in records if name.startswith(prefix + 'output/display/') and name.endswith(('-standard.json', '-scaled.json'))]
        assert len(profiles) == 8
        for name in profiles:
            value = record(name)
            assert value['structuralChecks'] == 'passed'
            for key in ['accepted', 'physicalInput', 'nativeRasterAccepted', 'readerAcceptance']:
                assert value[key] is False
            phase_checks(value, display=True)
            session = value['displaySession']
            for key in ['physicalDisplay', 'hardwareAcceleration', 'physicalInput']:
                assert session[key] is False
            for field in ['sessionCapture', 'finalWindowCapture']:
                png = raw(prefix + 'output/display/' + session[field])
                assert digest(png) == session[field + 'Sha256']
                dimensions = struct.unpack('>II', png[16:24])
                if field == 'sessionCapture':
                    assert list(dimensions) == session['sessionOutputSize'] == [2560, 1920]
                else:
                    assert dimensions == (880 * value['dpr'], 448 * value['dpr'])
                    assert dimensions[0] + 40 <= session['clientOutputSize'][0]
                    assert dimensions[1] + 60 <= session['clientOutputSize'][1]
        closed_prefix = f'closed{attempt}/'
        comparison = record(closed_prefix + 'controller/result.json')
        assert comparison['exitCode'] == 0 and comparison['sourceAttempt'] == source_number
        assert comparison['newModuleSha256'] == module and comparison['consumerSha256'] == CONSUMER
        assert comparison['oldModuleSha256'] == '2a5a3b01f82d5acb961e1e5f9a3e6f970c6649e12a9c4db00ac0b34b34ac2f51'
        absent_projects(comparison)
        assert comparison['byteIdentical'] == comparison['frameAndStateIdentical'] == len(comparison['closedComparisons']) == 256
        assert len(record(closed_prefix + 'controller/commands.json')) == 16
        assert all(row['exitCode'] == 0 for row in record(closed_prefix + 'controller/commands.json'))
        for command in record(closed_prefix + 'controller/commands.json'):
            mounts = bind_mounts(command['command'])
            assert set(mounts) == {'/package', '/package/install', '/comparison'}
            assert mounts['/package'] == str(portable_root / 'runtime')
            assert mounts['/comparison'] == sources[source_number]['output'] + '/closed-regression'
            assert mounts['/package/install'].endswith('/package/install')
            if command['label'] == 'new':
                assert mounts['/package/install'] == sources[source_number]['output'] + '/package/install'
        for row in comparison['closedComparisons']:
            location = closed_prefix + 'output/' + row['context'] + '/'
            a, b = raw(location + 'old-' + row['id'] + '.png'), raw(location + 'new-' + row['id'] + '.png')
            assert a == b and digest(a) == row['oldSha256'] == row['newSha256']
            assert record(location + 'old.json')['closed'] == record(location + 'new.json')['closed']

    binding = json.loads((DIRECTORY / 'product-binding.json').read_text())
    assert binding['sourceAttempt'] == 47 and binding['accepted'] is False
    scope = lambda name: name.startswith(('src/', 'tests/components/', 'tests/consumer/', 'tools/', 'samples/', 'cmake/', 'tokens/', 'assets/')) or name in ['CMakeLists.txt', 'CMakePresets.json'] or name.startswith('scripts/check-')
    assert binding['files'] == {name: value for name, value in sources[47]['sourceFiles'].items() if scope(name)}
    for name, expected in binding['files'].items():
        assert digest((ROOT / name).read_bytes()) == expected, name
    before = protected_fields(json.loads(subprocess.check_output(['git', 'show', PARENT + ':docs/parity-inventory.json'], cwd=ROOT)))
    after = protected_fields(json.loads((ROOT / 'docs/parity-inventory.json').read_text()))
    assert len(before) == 31503
    assert all(name in after and after[name] == value for name, value in before.items())
    candidate = json.loads((DIRECTORY / 'candidate-input-binding.json').read_text())
    assert candidate['producerInputSha256'] == digest(raw('source47/controller/inputs.json'))
    assert candidate['allSelectedCompiledInputsMatch'] is True
    assert set(candidate['postExecutionDocumentationDifferences']) == {
        'docs/file-input-search.md', 'docs/file-input-search-atomic.md', 'docs/parity-inventory.json'}
    for name, pair in candidate['postExecutionDocumentationDifferences'].items():
        assert pair['producer'] == sources[47]['sourceFiles'][name]
        assert pair['current'] == digest(raw('candidate/' + name))
    assert set(candidate['postExecutionAuditFiles']) == {
        'scripts/verify-file-input-search-atomic-integration.py',
        'tests/contracts/test_file_search_atomic_integration_evidence.py', '.github/workflows/references.yml'}
    for name, expected in candidate['postExecutionAuditFiles'].items():
        assert digest(raw('candidate/' + name)) == expected
    invariance = json.loads((DIRECTORY / 'inventory-invariance.json').read_text())
    assert invariance['base'] == PARENT and invariance['existingProtectedFields'] == len(before)
    frozen = protected_fields(record('candidate/docs/parity-inventory.json'))
    assert all(name in frozen and frozen[name] == value for name, value in before.items())
    print('Atomic search integration: exact41-47 sources, full58 on45, current47 Qt/consumer/reader/display checks and256 closed pairs verified; native acceptance remains pending')


if __name__ == '__main__':
    verify()
