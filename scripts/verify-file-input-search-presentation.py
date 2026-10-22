#!/usr/bin/env python3
"""Audit scoped native token observations and the Linux presentation candidate."""
import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/file-input-search-presentation-20261022'
PARENT = 'c58ac8fe0ffab2b9b482ade87d87a9f4bcea9c28'
MODULE = '6353c64778ede80d0c77c11558a317d16c6087b038d4c77afce89b27bbb34131'
CONSUMER = '519c4a22a50110fd380e33d7ce254361c461c16efe047be4c9155b058747c8e5'
CURRENT_CONSUMER = '36d5647e3662eebdb90be1c3386c05cb88510b73dd46e90a1134776095dd7a82'
NATIVE = '61d1e55c6f9c17c841eded420066c72b5611ec51af8c5a4821306f1751ea6514'
digest = lambda value: hashlib.sha256(value).hexdigest()


def limits(value):
    assert value['sourceParent'] == PARENT and value['sourceAttempt'] == 52
    assert value['moduleSha256'] == MODULE and value['consumerSha256'] == CURRENT_CONSUMER
    assert value['runtimeConsumerSha256'] == CONSUMER
    assert value['indexedPassed'] == 25 and value['indexedExpectedSkips'] == 1
    assert value['runtimeEvidenceAttempt'] == value['fullSuiteSource'] == 50
    assert value['fullSuiteConclusion'] == 'failure' and value['fullSuitePassedGroups'] == 57
    assert value['correctedTestSource'] == 52 and value['ctestGroupsCovered'] == 58
    assert value['fullSuiteRelabeled'] is False
    assert value['displayProfiles'] == 8 and value['readerPhases'] == [26, 26]
    assert value['closedIdentical'] == 256
    for key in ['accepted', 'nativeRasterAccepted', 'nativeGeometryAccepted',
                'nativeReaderAccepted', 'physicalInputAccepted',
                'independentMachineAccepted', 'expectedImagesChanged']:
        assert value[key] is False, key
    assert value['approvedExceptions'] == []


def captions(phase):
    expected = [part for part in phase['expression'] if part['kind'] == 'token']
    view = phase['tokenPresentation']
    assert view['glyphVisible'] is True and view['viewportX'] >= view['glyphRight']
    assert len(view['cells']) == len(expected)
    for index, (cell, part) in enumerate(zip(view['cells'], expected)):
        filename = part['mode'] == 'filename'
        assert cell['mode'] == ('NAME' if filename else 'ANY')
        assert cell['query'] == part['query']
        assert cell['accessibleName'] == ('Filename: ' if filename else 'Everything: ') + part['query']
        assert cell['height'] == 15 and cell['width'] > 0
        if index:
            previous = view['cells'][index - 1]
            assert cell['x'] > previous['x'] + previous['width']


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

    for version in [2, 3]:
        build = record(f'native{version}/build.json')
        assert build['libraryObjectSha256'] == NATIVE and build['libraryUnchanged'] is True
        assert build['independentNativeLibraryRebuild'] is False and build['accepted'] is False
        assert build['copiedResourceFilesIdentical'] is True and len(build['resourceFiles']) == 27
        after = record(f'native{version}/post-run-binding.json')
        assert after['libraryObjectSha256'] == NATIVE and after['libraryUnchangedAfterLaunch'] is True
        assert after['resourceFiles'] == build['resourceFiles'] and after['all27ResourceFilesUnchangedAfterLaunch'] is True
        close = record(f'native{version}/closure.json')
        assert close['processAbsent'] is True and close['recordedOwnerResults'] == []
    observations = record('native3/observations.json')
    assert observations['captureRecords'] == 16 and observations['libraryObjectSha256'] == NATIVE
    assert observations['independentNativeLibraryRebuild'] is False
    for key in ['accepted', 'rasterAccepted', 'readerAccepted', 'physicalInputAccepted']:
        assert observations[key] is False
    for number in [7, 9, 11, 12]:
        call = record(f'native3/call-{number:02}.json')
        blocks = call['output']['payload']['output']
        images = [part for part in blocks if part.get('type') == 'input_image']
        assert len(images) == 1
        url = images[0]['image_url']; url = url['url'] if isinstance(url, dict) else url
        image = base64.b64decode(url.split(',', 1)[1], validate=True)
        assert image == raw(f'native3/call-{number:02}.jpg') and image.startswith(b'\xff\xd8')
    final_ax = raw('native3/call-14.json')
    for marker in [b'Everything: pine', b'Filename: pine', b'Value: 1']:
        assert marker in final_ax
    assert b'Choose file' in raw('native3/call-15.json')
    failure = record('native1/launch-failure.json')
    assert failure['exception']['signal'] == 'SIGTRAP' and failure['processAbsentVerified'] is True

    bindings = json.loads((DIRECTORY / 'runtime-binding.json').read_text())
    assert bindings['sourceParent'] == PARENT
    assert len(bindings['files']) == 578
    assert set(bindings['changesFromParent']) == {'src/Avelino/FileChooserSearchInput.qml',
        'src/Avelino/filechoosersearchtext.cpp', 'tests/components/filesearch.cpp', 'tests/consumer/filesearchchecks.h'}
    base = {}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        for name in sorted(bindings['files']):
            assert not Path(name).is_absolute() and '..' not in Path(name).parts and '\n' not in name
            process.stdin.write((PARENT + ':' + name + '\n').encode()); process.stdin.flush()
            header = process.stdout.readline().split()
            assert len(header) == 3 and header[1] == b'blob', name
            base[name] = digest(process.stdout.read(int(header[2])))
            assert process.stdout.read(1) == b'\n'
        process.stdin.close(); assert process.wait() == 0
    for number in [48, 49, 50, 51, 52]:
        inputs = record(f'source{number}/inputs.json')
        assert inputs['parent'] == PARENT
        for name in base:
            expected = inputs['sourceFiles'][name]
            actual = digest(raw(f'source{number}/override/' + name)) if base[name] != expected else base[name]
            assert actual == expected, (number, name)
        result = record(f'source{number}/result.json')
        assert result['sourceUnchanged'] is True and result['accepted'] is False
        log = raw(f'source{number}/indexed-last-test.log')
        if number == 48:
            assert result['exitCode'] == 8
            assert b'23 passed, 2 failed, 1 skipped' in log
            assert b'Filename: pine' in log and log.count(b'FAIL!') == 2
        else:
            assert result['exitCode'] == 0 and b'25 passed, 0 failed, 1 skipped' in log
    current = record('source52/inputs.json')
    for name, expected in bindings['files'].items():
        assert current['sourceFiles'][name] == expected == digest((ROOT / name).read_bytes()), name
    proof = record('source50/install-rpath-transformation.json')
    assert proof['sourceAttempt'] == 50 and proof['installedModuleSha256'] == MODULE
    assert proof['normalizedBuiltSha256'] == MODULE and proof['allOtherBytesIdentical'] is True
    assert proof['oldRpath'] == '/opt/qt/lib:' and proof['installedRpath'] == '$ORIGIN' and proof['zeroPadded'] is True
    prefix = record('source50/installed-prefix.json')
    assert len(prefix) == 158 and prefix['lib/qml/Avelino/libAvelino.so'] == MODULE
    previous = record('previous/source47-prefix.json')
    assert set(previous) == set(prefix)
    assert {name for name in prefix if previous[name] != prefix[name]} == {
        'lib/qml/Avelino/FileChooserSearchInput.qml', 'lib/qml/Avelino/libAvelino.so'}
    suite = record('source50/validation/ctest/result.json')
    assert suite['exitCode'] == 8 and suite['sourceInputsUnchanged'] is suite['runtimeCorpusUnchanged'] is True
    suite_log = raw('source50/validation/ctest/full-remaining-tests.log')
    rows = re.findall(rb'^\s*\d+/57 Test\s+#\d+:\s+(\S+).*?\b(Passed|Failed)\b', suite_log, re.M)
    assert len(rows) == 57 and [name for name, result in rows if result == b'Failed'] == [b'file-input-indexed-search-dpr2']
    assert sum(result == b'Passed' for name, result in rows) == 56
    diagnostic = raw('source51/dpr2-diagnostic-v1/run.log')
    geometry = [json.loads(value) for value in re.findall(rb'TOKEN_PRESENTATION_VIEWPORT (\{[^\n]+\})', diagnostic)]
    assert len(geometry) == 2 and all(row['dpr'] == 2 and row['contentX'] == 0
        and row['contentWidth'] == 260 and row['viewportWidth'] == 309 and row['hostWidth'] == 360 for row in geometry)
    assert record('source51/dpr2-diagnostic-v1/result.json')['exitCode'] == 8
    assert record('source52/dpr2-verification-v1/result.json')['exitCode'] == 0
    assert b'25 passed, 0 failed, 1 skipped' in raw('source52/dpr2-corrected-last-test.log')
    repair = json.loads((DIRECTORY / 'test-only-repair-binding.json').read_text())
    assert repair['runtimeEvidenceAttempt'] == 50 and repair['currentTestSourceAttempt'] == 52
    assert repair['runtimeInputDifferences'] == ['tests/components/filesearch.cpp']
    assert repair['binaryDifferences'] == ['tests/components/AvelinoFileSearchTests']
    assert repair['allOtherTestExecutablesAndBuiltModuleIdentical'] is repair['installedPrefixFilesIdentical'] is True
    assert repair['installedPrefixFileCount'] == 158 and repair['installedModuleSha256'] == MODULE
    assert repair['fullSuiteSource50Conclusion'] == 'failure' and repair['fullSuiteRelabeled'] is False
    assert set(repair['oldBinaryHashes']) == set(repair['currentBinaryHashes'])
    assert [name for name in repair['oldBinaryHashes'] if repair['oldBinaryHashes'][name] != repair['currentBinaryHashes'][name]] == repair['binaryDifferences']
    fifty = record('source50/inputs.json')
    assert [name for name in bindings['files'] if fifty['sourceFiles'][name] != current['sourceFiles'][name]] == ['tests/components/filesearch.cpp']
    assert record('source52/installed-prefix.json') == prefix
    consumer = record('source50/validation/consumer/result.json')
    assert consumer['exitCode'] == 0 and consumer['consumerSha256'] == CONSUMER
    assert consumer['installedConsumerSourcesUnchanged'] is consumer['sourceInputsUnchanged'] is consumer['installedModuleUnchanged'] is True
    report = consumer['availableReport']; assert len(report['phases']) == 14
    for name in ['filename', 'compound-mixed', 'compound-everything']:
        captions(next(phase for phase in report['phases'] if phase['phase'] == name))
    assert consumer['unavailableReport']['providerUnavailable'] is True
    rebuilt = record('source52/validation/consumer/result.json')
    assert rebuilt['exitCode'] == 0 and rebuilt['consumerSha256'] == CURRENT_CONSUMER
    assert rebuilt['moduleHashes'] == consumer['moduleHashes']
    assert rebuilt['installedConsumerSourcesUnchanged'] is rebuilt['sourceInputsUnchanged'] is True
    assert len(rebuilt['availableReport']['phases']) == 14
    for phase in ['filename', 'compound-mixed', 'compound-everything']:
        captions(next(row for row in rebuilt['availableReport']['phases'] if row['phase'] == phase))
    rebuild = json.loads((DIRECTORY / 'consumer-rebuild-binding.json').read_text())
    assert rebuild['previousAttempt'] == 50 and rebuild['currentAttempt'] == 52
    assert rebuild['previousConsumerSha256'] == CONSUMER and rebuild['currentConsumerSha256'] == CURRENT_CONSUMER
    assert rebuild['sourceFilesIdentical'] is rebuild['allOtherBytesIdentical'] is True
    assert rebuild['binaryFilesModified'] is False and rebuild['byteDifferences'] == 23
    assert rebuild['buildId']['section'] == '.note.gnu.build-id' and rebuild['buildId']['bytes'] == 20
    timestamp = rebuild['resourceTimestamp']
    assert timestamp['resource'] == ':/qt/qml/InstalledConsumer/qmldir' and timestamp['bytes'] == 8
    old = ','.join(hex(c) for c in bytes.fromhex(timestamp['old'])) + ','
    new = ','.join(hex(c) for c in bytes.fromhex(timestamp['new'])) + ','
    assert raw('collection/consumer50-qrc-qmldir.cpp').decode().replace(old, new) == raw('collection/consumer52-qrc-qmldir.cpp').decode()

    portable = record('portable/controller/result.json'); absent(portable)
    assert portable['sourceAttempt'] == 50 and portable['exitCode'] == 0
    assert portable['moduleSha256'] == MODULE and portable['consumerSha256'] == CONSUMER
    assert portable['runtimeFilesUnchanged'] is True and portable['displayProfiles'] == 8
    inputs = record('portable/controller/inputs.json'); absent(inputs)
    assert inputs['runtimeFiles']['consumer-build/InstalledConsumer'] == CONSUMER
    assert {name[8:]: value for name, value in inputs['runtimeFiles'].items() if name.startswith('install/')} == prefix
    profiles = [name for name in records if name.startswith('portable/output/display/') and name.endswith(('-standard.json', '-scaled.json'))]
    assert len(profiles) == 8
    for name in profiles:
        value = record(name); assert len(value['phases']) == 15 and value['accepted'] is False
        for phase in ['filename', 'compound-mixed', 'compound-everything']:
            captions(next(row for row in value['phases'] if row['phase'] == phase))
        session = value['displaySession']
        assert session['physicalDisplay'] is session['hardwareAcceleration'] is session['physicalInput'] is False
        for key in ['sessionCapture', 'finalWindowCapture']:
            png = raw('portable/output/display/' + session[key])
            assert digest(png) == session[key + 'Sha256']
            dimensions = struct.unpack('>II', png[16:24])
            assert dimensions == ((2560, 1920) if key == 'sessionCapture' else (880 * value['dpr'], 448 * value['dpr']))
    for number in [19, 20]:
        inputs = record(f'reader{number}/controller/inputs.json'); absent(inputs)
        assert inputs['sourceAttempt'] == 50 and inputs['moduleSha256'] == MODULE and inputs['installedPrefixFiles'] == prefix
        result = record(f'reader{number}/controller/result.json')
        assert result['exitCode'] == 0 and result['operatorPhases'] == 26 and result['installedPrefixUnchanged'] is True
        operator = record(f'reader{number}/output/operator-report.json')
        assert operator['status'] == 'passed' and len(operator['phases']) == 26
        for key in ['accepted', 'physicalInput', 'readerNativeComparisonAccepted', 'speechEngineAudioAccepted']:
            assert operator[key] is False
        speech = raw(f'reader{number}/output/orca-debug.log')
        for phase_name, target in [('focused-result-speech', b'pine-only.txt'), ('keyboard-result-speech', b'avelinoulnacerulean-name.txt')]:
            phase = next(row for row in operator['phases'] if row['phase'] == phase_name)
            window = speech[phase['observations']['speechOffset']:phase['readerLogBytes']]
            for marker in [b'SPEECH OUTPUT:', b'SPEECH DISPATCHER: Speaking']:
                assert any(marker in line and target in line for line in window.splitlines())
    closed = record('closed/controller/result.json'); absent(closed)
    assert closed['sourceAttempt'] == 50 and closed['consumerSha256'] == CONSUMER and closed['newModuleSha256'] == MODULE
    assert closed['exitCode'] == 0 and closed['byteIdentical'] == closed['frameAndStateIdentical'] == len(closed['closedComparisons']) == 256
    for row in closed['closedComparisons']:
        location = 'closed/output/' + row['context'] + '/'
        a, b = raw(location + 'old-' + row['id'] + '.png'), raw(location + 'new-' + row['id'] + '.png')
        assert a == b and digest(a) == row['oldSha256'] == row['newSha256']
    spec = importlib.util.spec_from_file_location('presentation_inventory_fields', ROOT / 'scripts/verify-modal-parent-focus.py')
    inventory = importlib.util.module_from_spec(spec); spec.loader.exec_module(inventory)
    before = inventory.protected_fields(json.loads(subprocess.check_output(['git', 'show', PARENT + ':docs/parity-inventory.json'], cwd=ROOT)))
    frozen = inventory.protected_fields(record('candidate/docs/parity-inventory.json'))
    current = inventory.protected_fields(json.loads((ROOT / 'docs/parity-inventory.json').read_text()))
    invariance = json.loads((DIRECTORY / 'inventory-invariance.json').read_text())
    assert invariance['base'] == PARENT and invariance['existingProtectedFields'] == len(before) == 31503
    assert invariance['allExistingProtectedFieldsUnchanged'] is True
    assert all(frozen[name] == current[name] == value for name, value in before.items())
    print('FileInput token presentation: native JPEG/AX observations, retained full-suite failure, corrected DPR1/2 tests, unchanged runtime displays/readers and256 closed pairs verified; native acceptance pending')


if __name__ == '__main__':
    verify()
