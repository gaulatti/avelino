#!/usr/bin/env python3
"""Audit native boundary histories and the scoped installed Linux candidate."""
import base64
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/file-input-search-boundary-history-20261022'
PARENT = '823edb18f53d299780e77e99cad4b86b13cde097'
MODULE = '69ba21169f5db955dacb56b83861e7dffe5549f8b5bdaac9aebc88d58cacebd2'
CONSUMER = '080a20b8fb074eddf28a4115fd2b5a9d23adfd9edb7ddaf82e50fa404ab03114'
NATIVE = '502d77b79531d51feaae34a1ae884ae01897a6a33913d5a9b370237ed29e3de8'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
HEADER = 'src/Avelino/filechoosersearchhistory_p.h'
TEXT = {
    'history-before': 'oak \ufffc cedar',
    'history-expanded': 'oak  pine  cedar',
    'history-first-undo': 'oak pine cedar',
    'history-redo': 'oak  pine  cedar',
    'history-redo-X': 'oak  pine X cedar',
    'history-later-undo-1': 'oak  pine  cedar',
    'history-later-undo-2': 'oak pine cedar',
    'history-later-undo-3': 'oak pdar',
    'history-later-redo-1': 'oak pine cedar',
    'history-later-redo-2': 'oak  pine  cedar',
    'history-later-redo-3': 'oak  pine X cedar',
    'prefix-before': 'oak \ufffc', 'prefix-expanded': 'oak  pine',
    'prefix-first-undo': 'oak \ufffc', 'prefix-redo': 'oak  pine',
    'prefix-redo-X': 'oak  Xpine',
}
digest = lambda value: hashlib.sha256(value).hexdigest()


def load_script(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def limits(value):
    assert value['sourceParent'] == PARENT and value['sourceAttempt'] == 62
    assert value['moduleSha256'] == MODULE and value['consumerSha256'] == CONSUMER
    assert value['indexedPassed'] == 58 and value['indexedExpectedSkips'] == 1
    assert value['fullSuiteSource'] == 61 and value['ctestGroupsPassed'] == 58
    assert value['qtSuiteRerunOnCurrent'] is False
    assert value['fullSuiteReusedByExactComparability'] is True
    assert value['consumerPhases'] == 37 and value['phasesPerDisplayProfile'] == 38
    assert value['displayProfiles'] == 8 and value['readerPhases'] == [42, 42]
    assert value['readerAttempts'] == [30, 31]
    assert value['closedIdentical'] == 256
    for key in ['accepted', 'nativeRasterAccepted', 'nativeGeometryAccepted',
                'nativeReaderAccepted', 'physicalInputAccepted',
                'independentMachineAccepted', 'expectedImagesChanged',
                'generalNativeHistoryAccepted', 'nativeImePreeditAccepted']:
        assert value[key] is False, key
    assert value['approvedExceptions'] == []



def comparability(value):
    assert value['sourceAttempt'] == 62 and value['fullSuiteSource'] == 61
    assert value['all158FilesIdenticalTo61'] is value['allOtherRuntimeInputsSame'] is True
    assert value['runtimeInputDifferences'] == ['tests/consumer/fileinputchecks.h']
    assert value['consumerOnlyChange'] is True and value['qtSuiteRerunOn62'] is False
    assert len(value['installedPrefixFiles']) == 158
    assert value['installedPrefixFiles']['lib/qml/Avelino/libAvelino.so'] == MODULE
    assert value['accepted'] is False


def phases(value, display=False):
    pointer = load_script('verify-file-input-search-pointer')
    assert [row['phase'] for row in value['phases']] == pointer.PHASES + list(TEXT) + (['session-selected'] if display else [])
    prior = copy.deepcopy(value)
    prior['phases'] = prior['phases'][:len(pointer.PHASES)]
    pointer.phases(prior)
    rows = {row['phase']: row for row in value['phases']}
    assert all(not row['busy'] and not row['error'] for row in rows.values())
    for name, text in TEXT.items():
        assert rows[name]['editorText'] == text, name
        if '\ufffc' not in text:
            assert rows[name]['expression'] == [{'kind': 'text', 'text': text}], name
    assert rows['history-before']['expression'] == [
        {'kind': 'text', 'text': 'oak '}, {'kind': 'token', 'mode': 'filename', 'query': 'pine'},
        {'kind': 'text', 'text': ' cedar'}]
    assert rows['prefix-before']['expression'] == rows['prefix-first-undo']['expression'] == [
        {'kind': 'text', 'text': 'oak '}, {'kind': 'token', 'mode': 'everything', 'query': 'pine'}]
    for name in ['history-expanded', 'prefix-expanded']:
        assert rows[name]['selectedText'] == 'pine'
        assert (rows[name]['selectionStart'], rows[name]['selectionEnd']) == (5, 9)
    assert rows['history-first-undo']['selectedText'] == ''
    assert rows['prefix-first-undo']['selectedText'] == '\ufffc'
    for name, position in [('history-redo', 10), ('prefix-redo', 5)]:
        assert rows[name]['selectedText'] == '' and rows[name]['cursorPosition'] == position


def projection(value, call, raw_call):
    assert digest(raw_call) == value['rawCallSha256']
    assert call['sourceByteOffset'] == value['sourceByteOffset']
    assert call['call']['payload']['namespace'] == 'mcp__cua_repl'
    assert call['call']['payload']['call_id'] == call['output']['payload']['call_id']
    blocks = call['output']['payload']['output']
    if 'outputBlockIndex' in value:
        text = blocks[value['outputBlockIndex']]['text'][value['textStart']:value['textEnd']]
        assert digest(text.encode()) == value['datasetTextSha256']
        assert json.loads(text) == value['dataset']
    else:
        assert any(block['type'] == 'input_text' and block.get('text', '').strip().startswith('{')
                   and json.loads(block['text']) == value['dataset'] for block in blocks)
    assert value['dataset']['reference'] == REFERENCE
    assert value['dataset']['libraryObjectSha256'] == NATIVE


def verify():
    files = json.loads((DIRECTORY / 'files.json').read_text())
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, entry in files.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        data = (DIRECTORY / name).read_bytes()
        assert len(data) == entry['bytes'] and digest(data) == entry['sha256'], name
    records = json.loads((DIRECTORY / 'records.json').read_text())
    used = set()

    def raw(name):
        entry = records[name]
        used.add(entry['stored'])
        data = (DIRECTORY / entry['stored']).read_bytes()
        if entry['stored'].endswith('.gz'):
            data = gzip.decompress(data)
        assert len(data) == entry['bytes'] and digest(data) == entry['sha256'], name
        assert Path(entry['stored']).stem == entry['sha256']
        assert not data.startswith((b'\x7fELF', b'\xcf\xfa\xed\xfe'))
        return data

    record = lambda name: json.loads(raw(name))
    for name in records:
        raw(name)
    assert used == {name for name in files if name.startswith(('blobs/', 'images/'))}
    validation = json.loads((DIRECTORY / 'validation.json').read_text())
    limits(validation)
    fresh = record('fresh-native/inputs.json')
    assert fresh['reference'] == REFERENCE and len(fresh['sourceFiles']) == 89
    assert fresh['archiveSha256'] == '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
    assert fresh['byteIdenticalToFreshPinnedGitArchive'] is True
    assert fresh['prebuiltSabellaInputs'] is fresh['copiedBuildCache'] is False
    assert record('fresh-native/result.json')['exitCode'] == 0
    for number, count in [(8, 50), (9, 12), (10, 9)]:
        alias = f'native{number}/'
        build = record(alias + 'build.json')
        after = record(alias + 'post-run-binding.json')
        assert build['reference'] == REFERENCE and build['libraryObjectSha256'] == NATIVE
        assert build['independentNativeLibraryRebuild'] is True
        assert build['independentMachineAccepted'] is False
        assert len(build['resourceFiles']) == 27 and after['resourceFiles'] == build['resourceFiles']
        assert after['libraryObjectSha256'] == NATIVE and after['libraryUnchangedAfterLaunch'] is True
        assert after['all27ResourceFilesUnchangedAfterLaunch'] is True
        assert record(alias + 'closure.json')['processAbsent'] is True
        assert record(alias + 'observations.json')['captureRecords'] == count
        selected = record(alias + 'case-projections.json')
        name = alias + 'captured/' + selected['rawCall']
        projection(selected, record(name), raw(name))
        calls = [name for name in records if name.startswith(alias + 'captured/call-') and name.endswith('.json')]
        assert len(calls) == count
        images = {entry['sha256'] for name, entry in records.items() if name.startswith(alias + 'captured/') and name.endswith('.jpg')}
        for name in calls:
            call = record(name)
            assert call['call']['payload']['call_id'] == call['output']['payload']['call_id']
            for block in call['output']['payload']['output']:
                if block['type'] == 'input_image':
                    url = block['image_url']
                    url = url['url'] if isinstance(url, dict) else url
                    assert digest(base64.b64decode(url.split(',', 1)[1], validate=True)) in images
        dataset = selected['dataset']
        if number in [9, 10]:
            assert dataset['freshProcess'] is dataset['firstPanel'] is True
            assert dataset['searchAXSetterUsed'] is False
            expected = {name.removeprefix('history-' if number == 9 else 'prefix-'): text
                        for name, text in TEXT.items() if name.startswith('history-' if number == 9 else 'prefix-')}
            assert {row['phase']: row['value'] for row in dataset['rows']} == expected
        else:
            cases = {row['name']: row for row in dataset['cases']}
            assert len(cases) == 8
            for name, query in [('combining-single', 'avelinoe\u0301'), ('supplementary-single', 'avelino\U0001f426')]:
                case = cases[name]
                assert case['query'] == query
                rows = {row['phase']: row for row in case['rows']}
                assert rows['expanded']['value'] == rows['redo']['value'] == query
                assert rows['expanded']['selectedText'] == query and rows['undo']['selectedText'] == '\ufffc'
                assert rows['redo-X']['value'] == query + 'X'
                for row in rows.values():
                    assert row['utf16Length'] == len(row['value'].encode('utf-16-le')) // 2

    for attempt in [1, 2, 3, 4]:
        result = record(f'mechanism{attempt}/controller/result.json')
        assert result['prototypeOnly'] is True and result['accepted'] is False
        assert result['sourceInputsUnchanged'] is True
        assert result['exitCode'] == (1 if attempt in [1, 3] else 0)
        if attempt != 3:
            report = result['report']
            assert report['mismatches'] == (1 if attempt == 1 else 0)
            assert report['caretPositionVerified'] is report['quickInputVerified'] is False
        if attempt == 4:
            assert len(report['rows']) == 11
            assert all(row['peerFormatAndIdentityRetained'] for row in report['rows'])

    assert record('collection/avelino-file-search-history-pipeline-20261022-v1/result.json')['exitCode'] == 99
    assert record('closed/attempt1/controller/result.json')['exitCode'] == 99
    assert record('closed/attempt2/controller/result.json')['exitCode'] == 99
    for number in [23, 24, 25]:
        result = record(f'reader{number}/controller/result.json')
        assert result['exitCode'] == 1 and result['installedPrefixUnchanged'] is True
        assert 'operatorPhases' not in result
        assert b'Process did not become ready' in raw(f'reader{number}/controller/run.log')
    for number in [27, 28, 29]:
        assert record(f'reader{number}/controller/result.json')['exitCode'] == 1
    assert record('reader26/controller/result.json')['operatorPhases'] == 42
    readiness = record('speech-readiness/output/report.json')
    assert readiness['qtAppLaunched'] is False and readiness['same15sBound'] is True
    assert readiness['accepted'] is False
    assert [row['label'] for row in readiness['rows']] == ['local5', 'mounted5']
    assert all(row['ready'] and row['seconds'] < 15 for row in readiness['rows'])

    binding = json.loads((DIRECTORY / 'runtime-binding.json').read_text())
    assert binding['sourceParent'] == PARENT and binding['sourceAttempt'] == 62
    assert len(binding['files']) == 579 and HEADER in binding['files']
    base = {}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for name in sorted(binding['files']):
            assert not Path(name).is_absolute() and '..' not in Path(name).parts and '\n' not in name
            process.stdin.write((PARENT + ':' + name + '\n').encode()); process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) == 2 and header[1] == b'missing':
                assert name == HEADER
                base[name] = None
            else:
                assert len(header) == 3 and header[1] == b'blob'
                base[name] = digest(process.stdout.read(int(header[2])))
                assert process.stdout.read(1) == b'\n'
        process.stdin.close(); assert process.wait() == 0
    for attempt, summary in [(57, '42 passed, 1 failed, 1 skipped'), (58, '42 passed, 4 failed, 1 skipped'),
                             (59, '58 passed, 0 failed, 1 skipped'), (60, '58 passed, 0 failed, 1 skipped'),
                             (61, '58 passed, 0 failed, 1 skipped'), (62, '58 passed, 0 failed, 1 skipped')]:
        inputs = record(f'source{attempt}/inputs.json')
        result = record(f'source{attempt}/result.json')
        assert inputs['parent'] == PARENT and result['sourceUnchanged'] is True
        assert result['exitCode'] == (8 if attempt in [57, 58] else 0)
        assert summary.encode() in raw(f'source{attempt}/indexed-last-test.log')
        for name, original in base.items():
            expected = inputs['sourceFiles'].get(name)
            if expected is None:
                assert attempt in [57, 58] and name == HEADER
                continue
            assert (digest(raw(f'source{attempt}/override/' + name)) if expected != original else original) == expected
    assert all(digest((ROOT / name).read_bytes()) == value for name, value in binding['files'].items())
    comparability(record('source62/source61-comparability.json'))
    previous = record('source61/installed-prefix.json')
    assert previous == record('source62/installed-prefix.json')
    current = record('source62/inputs.json')
    assert {name: current['sourceFiles'][name] for name in binding['files']} == binding['files']
    prior = record('source61/inputs.json')
    assert sorted(name for name in binding['files'] if current['sourceFiles'][name] != prior['sourceFiles'][name]) == ['tests/consumer/fileinputchecks.h']
    assert b'58 passed, 0 failed, 1 skipped' in raw('source62/pointer-dpr2-v1/last-test.log')
    suite = record('source61/validation/ctest/result.json')
    assert suite['exitCode'] == 0 and suite['runtimeCorpusUnchanged'] is suite['sourceInputsUnchanged'] is True
    tests = re.findall(rb'^\s*\d+/57 Test\s+#\d+:\s+(\S+).*?\b(Passed|Failed)\b', raw('source61/validation/ctest/full-remaining-tests.log'), re.M)
    assert len(tests) == 57 and all(status == b'Passed' for name, status in tests)
    prefix = record('source62/installed-prefix.json')
    assert len(prefix) == 158 and prefix['lib/qml/Avelino/libAvelino.so'] == MODULE
    rpath = record('source62/install-rpath-transformation.json')
    assert rpath['installedModuleSha256'] == rpath['normalizedBuiltSha256'] == MODULE
    assert rpath['allOtherBytesIdentical'] is rpath['zeroPadded'] is True
    assert rpath['oldRpath'] == '/opt/qt/lib:' and rpath['installedRpath'] == '$ORIGIN'
    assert rpath['transformationProofSource'] == 61 and rpath['identicalBuiltAndInstalledBinaryHashesTo61'] is True
    old_rpath = record('source61/install-rpath-transformation.json')
    assert rpath['builtModuleSha256'] == old_rpath['builtModuleSha256'] == record('source62/pointer-dpr2-v1/result.json')['builtModuleSha256']
    assert old_rpath['installedModuleSha256'] == old_rpath['normalizedBuiltSha256'] == MODULE
    consumer = record('source62/validation/consumer/result.json')
    assert consumer['exitCode'] == 0 and consumer['consumerSha256'] == CONSUMER
    assert consumer['installedConsumerSourcesUnchanged'] is consumer['sourceInputsUnchanged'] is consumer['installedModuleUnchanged'] is True
    phases(consumer['availableReport'])
    assert consumer['unavailableReport']['providerUnavailable'] is True
    portable = record('portable/controller/result.json')
    load_script('verify-file-input-search-pointer').absent(portable)
    assert portable['exitCode'] == 0 and portable['sourceAttempt'] == 62 and portable['runtimeFilesUnchanged'] is True
    assert portable['moduleSha256'] == MODULE and portable['consumerSha256'] == CONSUMER
    assert portable['displayProfiles'] == 8 and portable['phasesPerDisplayProfile'] == 38
    phases(record('portable/output/available.json'))
    displays = [name for name in records if name.startswith('portable/output/display/') and re.search(r'-(standard|scaled)\.json$', name)]
    assert len(displays) == 8
    for name in displays:
        phases(record(name), display=True)
    for number in validation['readerAttempts']:
        inputs = record(f'reader{number}/controller/inputs.json')
        load_script('verify-file-input-search-pointer').absent(inputs)
        assert inputs['sourceAttempt'] == 62 and inputs['moduleSha256'] == MODULE
        assert inputs['installedPrefixFiles'] == prefix
        result = record(f'reader{number}/controller/result.json')
        assert result['exitCode'] == 0 and result['operatorPhases'] == 42
        assert result['installedPrefixUnchanged'] is result['probeSourcesUnchanged'] is True
        profile = record(f'reader{number}/output/profile.json')
        assert (profile['protocol'], profile['backend'], profile['scaled']) == (
            ('xcb', 'software', False) if number == 31 else ('wayland', 'opengl', True))
        operator = record(f'reader{number}/output/operator-report.json')
        assert operator['status'] == 'passed' and len(operator['phases']) == 42
        rows = {row['phase']: row['observations'] for row in operator['phases']}
        for name, text in TEXT.items():
            assert rows[name]['text'] == text
        assert rows['prefix-redo']['caret'] == 5 and rows['history-redo']['caret'] == 10
        assert rows['prefix-first-undo']['selectedRange'] == [4, 5]
        assert b'Everything: pine' in raw(f'reader{number}/output/prefix-first-undo.json')
        for key in ['accepted', 'physicalInput', 'readerNativeComparisonAccepted', 'speechEngineAudioAccepted']:
            assert operator[key] is False
        local = record(f'reader{number}/output/local-execution.json')
        assert local['exitCode'] == 0 and local['allOutputsCopiedAfterChildrenStop'] is True
        assert local['inputAssertionsAndDeadlinesChanged'] is local['accepted'] is False
        if number == 30:
            for phase in ['history-before', 'prefix-before']:
                calibration = record(f'reader30/output/{phase}-pointer-calibration.json')
                assert calibration['accepted'] is calibration['accessibilityGeometryAccepted'] is False
                assert calibration['scale'] == 2
                assert digest(raw('reader30/output/' + calibration['image'])) == calibration['imageSha256']
                left, top, right, bottom = calibration['focusRing']
                token, clear = calibration['tokenBounds'], calibration['clearBounds']
                x = right - 2 * ((clear[0] + clear[2] + 4) - (token[0] + token[2] - 4))
                assert calibration['target'] == [x, (top + bottom) // 2]
                assert left < x < right
    closed = record('closed/qualification.json')
    assert closed['sourceAttempt'] == 62 and closed['byteIdentical'] == closed['frameAndStateIdentical'] == 256
    assert closed['moduleSha256'] == MODULE and closed['consumerSha256'] == CONSUMER
    for row in closed['comparisons']:
        a, b = raw(row['oldRecord']), raw(row['newRecord'])
        assert a == b and digest(a) == row['oldSha256'] == row['newSha256']
    fields = load_script('verify-modal-parent-focus').protected_fields
    before = fields(json.loads(subprocess.check_output(['git', 'show', PARENT + ':docs/parity-inventory.json'], cwd=ROOT)))
    after = fields(json.loads((ROOT / 'docs/parity-inventory.json').read_text()))
    assert len(before) == 31515 and all(after.get(name) == value for name, value in before.items())
    print('FileInput boundary history: bound native text, retained failures, current Qt/consumer/display/readers and closed checks verified; native acceptance pending')


if __name__ == '__main__':
    verify()
