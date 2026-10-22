#!/usr/bin/env python3
"""Audit scoped native pointer observations and the installed Linux candidate."""
import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/file-input-search-pointer-20261022'
PARENT = '4f720b5eee7623e57f0dc263514eba85c464cffb'
MODULE = '02bae12541ae5c422a21902344a6deb359c217f515321c4f3d254fe20d4b53b4'
CONSUMER = '2df640c4d991f985ca1b1b4f93ac8ee2c5b209f26bbb720cddbba6b9282a1395'
NATIVE = '502d77b79531d51feaae34a1ae884ae01897a6a33913d5a9b370237ed29e3de8'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
PHASES = ['global', 'folder', 'filename', 'query-selected', 'query-expanded',
          'query-expand-undo', 'query-expand-redo', 'token-replacement', 'token-undo',
          'token-redo', 'compound-mixed', 'compound-query-expanded', 'compound-query-undo',
          'compound-query-redo', 'compound-everything', 'compound-replacement',
          'compound-undo', 'compound-redo', 'selected', 'owner-result', 'cancelled-query']
digest = lambda value: hashlib.sha256(value).hexdigest()


def limits(value):
    assert value['sourceParent'] == PARENT and value['sourceAttempt'] == 56
    assert value['moduleSha256'] == MODULE and value['consumerSha256'] == CONSUMER
    assert value['indexedPassed'] == 42 and value['indexedExpectedSkips'] == 1
    assert value['fullSuiteSource'] == 56 and value['ctestGroupsPassed'] == 58
    assert value['displayProfiles'] == 8 and value['phasesPerDisplayProfile'] == 22
    assert value['readerPhases'] == [26, 26] and value['closedIdentical'] == 256
    for key in ['accepted', 'nativeRasterAccepted', 'nativeGeometryAccepted',
                'nativeReaderAccepted', 'physicalInputAccepted',
                'independentMachineAccepted', 'expectedImagesChanged']:
        assert value[key] is False, key
    assert value['approvedExceptions'] == []


def phases(value, display=False):
    assert value['accepted'] is False and value['qt'] == '6.8.3'
    assert [row['phase'] for row in value['phases']] == PHASES + (['session-selected'] if display else [])
    rows = {row['phase']: row for row in value['phases']}
    assert all(not row['busy'] and not row['error'] for row in rows.values())
    token = [{'kind': 'token', 'mode': 'filename', 'query': 'avelinoulnacerulean'}]
    raw = [{'kind': 'text', 'text': 'avelinoulnacerulean'}]
    for name in ['filename', 'query-selected', 'query-expand-undo']:
        assert rows[name]['expression'] == token
    for name in ['query-selected', 'query-expand-undo', 'compound-query-undo']:
        assert rows[name]['selectedText'] == '\ufffc'
    for name in ['query-expanded', 'query-expand-redo']:
        assert rows[name]['expression'] == raw
    compound = [{'kind': 'token', 'mode': 'everything', 'query': 'avelinoulnacerulean'},
                {'kind': 'token', 'mode': 'filename', 'query': 'pine'}]
    assert rows['compound-mixed']['expression'] == rows['compound-query-undo']['expression'] == compound
    for name in ['compound-query-expanded', 'compound-query-redo']:
        assert rows[name]['expression'] == [raw[0], compound[1]]
    for name in ['query-expanded', 'compound-query-expanded']:
        assert rows[name]['selectedText'] == 'avelinoulnacerulean'
        assert rows[name]['selectionStart'] == 0 and rows[name]['selectionEnd'] == 19
    for name in ['query-expand-redo', 'compound-query-redo']:
        assert rows[name]['selectedText'] == '' and rows[name]['cursorPosition'] == 19
    for name in ['compound-mixed', 'compound-query-expanded', 'compound-query-undo',
                 'compound-query-redo', 'compound-everything']:
        assert rows[name]['names'] == ['pine-only.txt']


def absent(value):
    for key in ['libraryProjectMounted', 'consumerProjectMounted', 'productBuildMounted']:
        assert value[key] is False


def verify():
    files = json.loads((DIRECTORY / 'files.json').read_text())
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, entry in files.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        value = (DIRECTORY / name).read_bytes()
        assert len(value) == entry['bytes'] and digest(value) == entry['sha256'], name
    records = json.loads((DIRECTORY / 'records.json').read_text())
    used = set()

    def raw(name):
        entry = records[name]; used.add(entry['stored'])
        assert entry['stored'] in files
        value = (DIRECTORY / entry['stored']).read_bytes()
        if entry['stored'].endswith('.gz'):
            value = gzip.decompress(value)
        assert len(value) == entry['bytes'] and digest(value) == entry['sha256'], name
        assert Path(entry['stored']).stem == entry['sha256']
        assert not value.startswith((b'\x7fELF', b'\xcf\xfa\xed\xfe'))
        return value

    record = lambda name: json.loads(raw(name))
    for name in records:
        raw(name)
    assert used == {name for name in files if name.startswith(('blobs/', 'images/'))}
    limits(json.loads((DIRECTORY / 'validation.json').read_text()))
    build = record('fresh-native/inputs.json'); result = record('fresh-native/result.json')
    assert build['reference'] == REFERENCE and len(build['sourceFiles']) == 89
    assert build['archiveSha256'] == '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
    assert build['byteIdenticalToFreshPinnedGitArchive'] is True
    assert build['prebuiltSabellaInputs'] is build['copiedBuildCache'] is False
    assert result['exitCode'] == 0 and result['accepted'] is False
    native = record('native/build.json'); after = record('native/post-run-binding.json')
    assert native['reference'] == REFERENCE and native['libraryObjectSha256'] == NATIVE
    assert native['independentNativeLibraryRebuild'] is True and native['independentMachineAccepted'] is False
    assert native['copiedResourceFilesIdentical'] is True and len(native['resourceFiles']) == 27
    assert after['libraryObjectSha256'] == NATIVE and after['libraryUnchangedAfterLaunch'] is True
    assert after['resourceFiles'] == native['resourceFiles'] and after['all27ResourceFilesUnchangedAfterLaunch'] is True
    close = record('native/closure.json')
    assert close['processAbsent'] is True and close['recordedOwnerResults'] == [] and close['accepted'] is False
    observations = record('native/observations.json')
    assert observations['captureRecords'] == 52 and len(observations['images']) == 21
    assert observations['libraryObjectSha256'] == NATIVE and observations['independentNativeLibraryRebuild'] is True
    projections = record('native/case-projections.json')['projections']
    assert len(projections) == 18
    for projection in projections:
        name = 'native/captured/' + projection['rawCall']
        call = record(name)
        assert digest(raw(name)) == projection['rawCallSha256']
        assert call['sourceByteOffset'] == projection['sourceByteOffset']
        assert call['call']['payload']['namespace'] == 'mcp__cua_repl'
        assert call['call']['payload']['call_id'] == call['output']['payload']['call_id']
        blocks = call['output']['payload']['output']
        text = '\n'.join(block['text'] for block in blocks if block['type'] == 'input_text')
        assert digest(text.encode()) == projection['outputTextSha256']
        images = [block for block in blocks if block['type'] == 'input_image']
        assert len(images) == len(projection['images'])
        for block, image in zip(images, projection['images']):
            url = block['image_url']; url = url['url'] if isinstance(url, dict) else url
            value = base64.b64decode(url.split(',', 1)[1], validate=True)
            assert value == raw('native/captured/' + image['path'])
            assert digest(value) == image['sha256'] and value.startswith(b'\xff\xd8')
        assert projection['excludedFromQueryClaims'] is (projection['case'] == 'calibration')
    cases = {row['case']: row for row in observations['cases']}
    assert cases['query-single']['selected'] == '\ufffc' and cases['query-single']['modeMenuOpened'] is False
    assert cases['query-double']['after'] == cases['query-double']['selected'] == 'pine'
    assert cases['already-spaced-prefix']['after'] == 'oak  pine'
    assert cases['both-already-spaced']['after'] == 'oak  pine  cedar'
    assert cases['suffix-redo-caret-test']['after'] == 'pine Xcedar'
    assert cases['after-token-neighbor']['after'] == '\ufffcpine'
    assert cases['first-with-token-neighbor']['after'] == 'pine\ufffc'

    binding = json.loads((DIRECTORY / 'runtime-binding.json').read_text())
    assert binding['sourceParent'] == PARENT and len(binding['files']) == 578
    base = {}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for name in sorted(binding['files']):
            assert not Path(name).is_absolute() and '..' not in Path(name).parts and '\n' not in name
            process.stdin.write((PARENT + ':' + name + '\n').encode()); process.stdin.flush()
            header = process.stdout.readline().split(); assert len(header) == 3 and header[1] == b'blob'
            base[name] = digest(process.stdout.read(int(header[2])))
            assert process.stdout.read(1) == b'\n'
        process.stdin.close(); assert process.wait() == 0
    for attempt, summary in [(53, b'25 passed, 10 failed, 1 skipped'), (54, b'35 passed, 0 failed, 1 skipped'),
                             (55, b'40 passed, 1 failed, 1 skipped'), (56, b'42 passed, 0 failed, 1 skipped')]:
        inputs = record(f'source{attempt}/inputs.json'); result = record(f'source{attempt}/result.json')
        assert inputs['parent'] == PARENT and result['sourceUnchanged'] is True and result['accepted'] is False
        assert result['exitCode'] == (8 if attempt in [53, 55] else 0)
        for name in base:
            expected = inputs['sourceFiles'][name]
            value = digest(raw(f'source{attempt}/override/' + name)) if expected != base[name] else base[name]
            assert value == expected
        if attempt == 56:
            assert b'100% tests passed, 0 tests failed out of 1' in raw('source56/search-dpr1.log')
        else:
            assert summary in raw(f'source{attempt}/indexed-last-test.log')
    current = record('source56/inputs.json')
    assert {name: current['sourceFiles'][name] for name in binding['files']} == binding['files']
    assert all(digest((ROOT / name).read_bytes()) == value for name, value in binding['files'].items())
    assert b'42 passed, 0 failed, 1 skipped' in raw('source56/pointer-dpr2-v1/last-test.log')
    assert record('source56/pointer-dpr2-v1/result.json')['exitCode'] == 0
    suite = record('source56/validation/ctest/result.json')
    assert suite['exitCode'] == 0 and suite['sourceInputsUnchanged'] is suite['runtimeCorpusUnchanged'] is True
    rows = re.findall(rb'^\s*\d+/57 Test\s+#\d+:\s+(\S+).*?\b(Passed|Failed)\b', raw('source56/validation/ctest/full-remaining-tests.log'), re.M)
    assert len(rows) == 57 and all(status == b'Passed' for name, status in rows)
    prefix = record('source56/installed-prefix.json')
    assert len(prefix) == 158 and prefix['lib/qml/Avelino/libAvelino.so'] == MODULE
    proof = record('source56/install-rpath-transformation.json')
    assert proof['installedModuleSha256'] == proof['normalizedBuiltSha256'] == MODULE
    assert proof['allOtherBytesIdentical'] is proof['zeroPadded'] is True
    assert proof['oldRpath'] == '/opt/qt/lib:' and proof['installedRpath'] == '$ORIGIN'
    consumer = record('source56/validation/consumer/result.json')
    assert consumer['exitCode'] == 0 and consumer['consumerSha256'] == CONSUMER
    assert consumer['installedConsumerSourcesUnchanged'] is consumer['sourceInputsUnchanged'] is consumer['installedModuleUnchanged'] is True
    assert consumer['unavailableReport']['providerUnavailable'] is True
    phases(consumer['availableReport'])
    portable = record('portable/controller/result.json'); absent(portable)
    assert portable['sourceAttempt'] == 56 and portable['moduleSha256'] == MODULE and portable['consumerSha256'] == CONSUMER
    assert portable['exitCode'] == 0 and portable['runtimeFilesUnchanged'] is True and portable['displayProfiles'] == 8
    phases(record('portable/output/available.json'))
    for name in records:
        if name.startswith('portable/output/display/') and re.search(r'-(standard|scaled)\.json$', name):
            phases(record(name), display=True)
    for number in [21, 22]:
        inputs = record(f'reader{number}/controller/inputs.json'); absent(inputs)
        assert inputs['sourceAttempt'] == 56 and inputs['moduleSha256'] == MODULE and inputs['installedPrefixFiles'] == prefix
        result = record(f'reader{number}/controller/result.json')
        assert result['exitCode'] == 0 and result['operatorPhases'] == 26 and result['installedPrefixUnchanged'] is True
        operator = record(f'reader{number}/output/operator-report.json')
        assert operator['status'] == 'passed' and len(operator['phases']) == 26
        for key in ['accepted', 'physicalInput', 'readerNativeComparisonAccepted', 'speechEngineAudioAccepted']:
            assert operator[key] is False
    closed = record('closed/controller/result.json'); absent(closed)
    assert closed['sourceAttempt'] == 56 and closed['consumerSha256'] == CONSUMER and closed['newModuleSha256'] == MODULE
    assert closed['exitCode'] == 0 and closed['byteIdentical'] == closed['frameAndStateIdentical'] == len(closed['closedComparisons']) == 256
    for row in closed['closedComparisons']:
        location = 'closed/output/' + row['context'] + '/'
        a, b = raw(location + 'old-' + row['id'] + '.png'), raw(location + 'new-' + row['id'] + '.png')
        assert a == b and digest(a) == row['oldSha256'] == row['newSha256']
    spec = importlib.util.spec_from_file_location('pointer_inventory_fields', ROOT / 'scripts/verify-modal-parent-focus.py')
    inventory = importlib.util.module_from_spec(spec); spec.loader.exec_module(inventory)
    before = inventory.protected_fields(json.loads(subprocess.check_output(['git', 'show', PARENT + ':docs/parity-inventory.json'], cwd=ROOT)))
    current = inventory.protected_fields(json.loads((ROOT / 'docs/parity-inventory.json').read_text()))
    invariance = json.loads((DIRECTORY / 'inventory-invariance.json').read_text())
    assert invariance['base'] == PARENT and invariance['existingProtectedFields'] == len(before)
    assert invariance['allExistingProtectedFieldsUnchanged'] is True
    assert all(current[name] == value for name, value in before.items())
    print('FileInput query pointer/expansion: native call bindings, retained red attempts, current Qt/consumer/display/reader and256 closed checks verified; native acceptance pending')


if __name__ == '__main__':
    verify()
