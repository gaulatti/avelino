#!/usr/bin/env python3
"""Audit the recorded path-edit lifetime repair without promoting native parity."""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/path-assistive-lifetime-20261024'
PARENT = 'b93899f4a0b4381db0514ed8da230f1c0c837069'
BASE_IMAGE = 'sha256:56eb7ac400248fbadfbb6eaddbce2c3827ac0b2ffc68346137dcbadda41dad1b'
READER_IMAGE = 'sha256:6ec59fc60fae3a41c3802f824c1da5f075d12322d560a78013a20c4f14492ef1'
BASE_MODULE = '71dde323f73677aa94fc0c878edd3376f10c65eb59d13aabcd68983671fc2368'
FIX_MODULE = 'eaa547637c23e24f4267e1404681bba94684144f7f65ce54703e2a7b7fc1af18'
CONSUMER = '4839b21d15db8fa67fdd5d96fb84e32a1d05db8a06d4e2316e6a314ac1adde2f'
GOTO_EXERCISE = '3d98035372523cb8c958961429c1d0663bf62e2325a138a0a3b09d18d43885bf'
DATE_EXERCISE = 'b9fb7bab21c258924ec0d34bbf51aec748b10f012d152723c43b6322c78f8ecd'
DELTA = ['src/Avelino/daterangeinput.cpp', 'src/Avelino/filechooserpathinput.cpp',
         'src/Avelino/assistivetextinput_p.h', 'tests/components/fileinput-ui.cpp',
         'tests/consumer/CMakeLists.txt', 'tests/consumer/fileinputchecks.h', 'tests/consumer/pathinputobserver.h']
OVERRIDES = DELTA[4:]
NOTIFICATIONS = ['selectedTextChanged', 'selectionStartChanged', 'selectionEndChanged', 'cursorPositionChanged',
                 'cursorRectangleChanged', 'textEdited', 'textChanged', 'displayTextChanged', 'contentSizeChanged', 'canUndoChanged']
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


HISTORY = load('path_history_helpers', ROOT / 'scripts/verify-stepper-native-names.py')
PROTECTED = load('path_inventory_helpers', ROOT / 'scripts/verify-modal-parent-focus.py')


class Capsule:
    def __init__(self, directory):
        self.directory = directory
        self.records = json.loads((directory / 'records.json').read_text())

    def raw(self, name):
        row = self.records[name]; path = self.directory / row['stored']
        assert path.resolve().is_relative_to(self.directory.resolve())
        stored = path.read_bytes()
        raw = stored if path.suffix == '.png' else gzip.decompress(stored)
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
        return raw

    def record(self, name):
        return json.loads(self.raw(name))


def manifest(directory):
    files = json.loads((directory / 'files.json').read_text())
    assert set(files) == {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        raw = (directory / name).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
    capsule = Capsule(directory)
    for name in capsule.records:
        raw = capsule.raw(name)
        assert not raw.startswith((b'\x7fELF', b'\xcf\xfa\xed\xfe'))
        if raw.startswith(b'\x89PNG\r\n\x1a\n'):
            with Image.open(io.BytesIO(raw)) as image: image.load()
    return capsule


def limits(value):
    assert value['sourceParent'] == PARENT
    for key, expected in [('librarySourceAttempt', 4), ('baselineSourceAttempt', 3), ('consumerSourceAttempt', 2),
                          ('baselineCrashes', 10), ('baselineStaleCallbackFailures', 4), ('fileInputQtChecksEachDpr', 38),
                          ('dateRangeQtChecksEachDpr', 48), ('consumerProfiles', 4), ('consumerPathLifetimeChecksEach', 10),
                          ('consumerPathCallbackChecksEach', 4), ('consumerDateAssistiveEditsEach', 6),
                          ('gotoReaderPhasesEach', 21), ('dateReaderPhasesEach', 12), ('readerProfilesEach', 2),
                          ('runtimeInputFiles', 581), ('libraryRuntimeInputFiles', 580), ('installedFiles', 158),
                          ('priorProtectedFields', 31532), ('afterProtectedFields', 31534),
                          ('desktopCandidates', 78), ('desktopEntries', 80), ('acceptedDesktopEntries', 0), ('televisionPending', 46)]:
        assert value[key] == expected, key
    assert value['dprs'] == [1, 2]
    assert value['compiledBaselineModule'] == BASE_MODULE and value['compiledFixedModule'] == FIX_MODULE
    assert value['consumerBinary'] == CONSUMER and value['baseImage'] == BASE_IMAGE and value['readerImage'] == READER_IMAGE
    for key in ['accepted', 'nativeReaderAccepted', 'nativeRasterAccepted', 'physicalInputAccepted',
                'physicalListeningAccepted', 'independentMachineAccepted', 'fullQt58Rerun',
                'historicalImagesRestored', 'expectedImagesChanged', 'nativePixelsCompared']:
        assert value[key] is False, key
    assert value['approvedExceptions'] == []


def crash(log, code):
    assert code == 139 and 'Received signal 11 (SIGSEGV)' in log
    assert 'assistivePathSelectionAllowsSynchronousDestruction' in log


def qt_log(log, group, count):
    assert f'Totals: {count} passed, 0 failed, 0 skipped, 0 blacklisted' in log
    assert f'Finished testing of {group}' in log


def helper_move(before, after, header):
    start = before.index('struct DateInputState {'); end = before.index('class DateInputAccessible final', start)
    original = before[start:end]
    expected_header = '#pragma once\n#include <QtQuick/private/qquicktextinput_p_p.h>\n#include <QPointer>\n#include <QSignalBlocker>\n\nstatic_assert(QT_VERSION==QT_VERSION_CHECK(6,8,3),"Revalidate assistive text-input notifications and Qt Undo cursor before upgrading Qt");\nnamespace AvelinoPrivate {\n'
    expected_header += original.replace('DateInputState', 'AssistiveTextInputState').replace('DateRangeInput *input', 'QQuickTextInput *input').replace('QPointer<DateRangeInput>', 'QPointer<QQuickTextInput>') + '}\n'
    expected_after = before[:start] + before[end:]
    expected_after = expected_after.replace('#include "daterangeinput.h"', '#include "daterangeinput.h"\n#include "assistivetextinput_p.h"').replace('#include <QSignalBlocker>\n', '')
    expected_after = expected_after.replace('finishAssistiveOperation(input,', 'AvelinoPrivate::finishAssistiveOperation(input,')
    assert header == expected_header and after == expected_after


def binding(capsule, value):
    assert value['sourceParent'] == PARENT and value['librarySourceAttempt'] == 4 and value['baselineSourceAttempt'] == 3
    assert value['runtimeDeltaPaths'] == DELTA and value['consumerOverridePaths'] == OVERRIDES
    files = value['files']; library = value['libraryFiles']
    assert len(files) == 581 and len(library) == 580 and value['accepted'] is False
    assert set(files) - set(library) == {'tests/consumer/pathinputobserver.h'}
    prior = HISTORY.git_files(PARENT, sorted(set(files) - {'src/Avelino/assistivetextinput_p.h', 'tests/consumer/pathinputobserver.h'}))
    reconstructed = {name: sha(raw) for name, raw in prior.items()}
    for name in DELTA:
        prefix = 'consumer2/implementation/' if name in OVERRIDES else 'source4/implementation/'
        reconstructed[name] = sha(capsule.raw(prefix + name))
    assert reconstructed == files
    source3 = capsule.record('source3/controller/inputs.json'); source4 = capsule.record('source4/controller/inputs.json')
    assert source3['parent'] == source4['parent'] == PARENT
    assert source3['imageId'] == source4['imageId'] == BASE_IMAGE
    assert source3['dockerContext'] == source4['dockerContext'] == 'colima-avelino-path-20261024'
    assert {name: source4['sourceFiles'][name] for name in library} == library
    assert {name: digest for name, digest in files.items() if name not in OVERRIDES} == {name: digest for name, digest in library.items() if name not in OVERRIDES}
    changed = {name for name in set(source3['sourceFiles']) | set(source4['sourceFiles']) if source3['sourceFiles'].get(name) != source4['sourceFiles'].get(name)}
    assert changed == {'docs/date-range-picker.md', 'docs/file-input-linux.md', *DELTA[:3]}
    assert all(source3['sourceFiles'][name] == sha(raw) for name, raw in prior.items() if name != DELTA[3])
    for name in DELTA[:2]: assert sha(capsule.raw('source3/implementation/' + name)) == source3['sourceFiles'][name]
    assert source3['sourceFiles'][DELTA[3]] == sha(capsule.raw('source3/implementation/' + DELTA[3])) == files[DELTA[3]]
    consumer = capsule.record('consumer2/controller/inputs.json')
    assert consumer['changedFilesFromFreshConsumer1'] == ['CMakeLists.txt', 'fileinputchecks.h', 'pathinputobserver.h']
    assert consumer['incrementalIndependentBuild'] is True and consumer['freshEmptyBuildDirectory'] is False and consumer['libraryProjectMounted'] is False
    for name, digest in consumer['consumerFiles'].items():
        key = 'tests/consumer/' + name
        if key in files: assert files[key] == digest


def candidate(current, executed):
    assert current == executed, 'Current runtime differs from the executed candidate'


def inventory_snapshot(value):
    assert value['sourceParent'] == PARENT and value['priorProtectedFields'] == 31532 and value['afterProtectedFields'] == 31534
    assert value['accepted'] is False
    raw = subprocess.check_output(['git', 'cat-file', 'blob', value['candidateBlob']], cwd=ROOT)
    assert sha(raw) == value['candidateSha256']
    before = json.loads(HISTORY.git_files(PARENT, ['docs/parity-inventory.json'])['docs/parity-inventory.json'])
    after = json.loads(raw); old = PROTECTED.protected_fields(before); new = PROTECTED.protected_fields(after)
    assert len(old) == 31532 and len(new) == 31534 and all(new[name] == item for name, item in old.items())
    assert after['desktop']['acceptance'] == before['desktop']['acceptance'] and after['television'] == before['television']
    for old_entry, new_entry in zip(before['desktop']['entries'], after['desktop']['entries']):
        assert old_entry['id'] == new_entry['id'] and old_entry['status'] == new_entry['status']
        assert new_entry['cases'][:len(old_entry['cases'])] == old_entry['cases']
    assert sum(e['status'] == 'verification-pending' for e in after['desktop']['entries']) == 78
    return after


def package_inputs(value, installed):
    assert value['installedFiles'] == installed
    assert value['sourceProjectsMounted'] is value['productBuildMounted'] is value['consumerBuildMounted'] is False


def consumer_report(value, fixture, dpr):
    assert value['fixture'] == fixture and value['structuralChecks'] == 'passed' and value['accepted'] is False
    assert value['platform'] == 'xcb' and value['graphicsApi'] == 1 and value['dpr'] == dpr
    assert value['appearance'] == ('light' if dpr == 1 else 'dark') and value['textScale'] == (1 if dpr == 1 else 1.5)
    if fixture == 'file-input':
        lifetime = value['assistiveLifetime']; callbacks = value['assistiveSelectionCallbacks']
        assert [x['notification'] for x in lifetime] == ['2' + x + '()' for x in NOTIFICATIONS]
        assert all(x['calls'] == x['destroyed'] == 1 and x['lastText'] == ('/tmp/Alpha' if i < 5 else 'Xtmp/Alpha') for i, x in enumerate(lifetime))
        assert {x['property'] for x in callbacks} == {'enabled', 'readOnly', 'text', 'cursorPosition'} and len(callbacks) == 4
        assert all(x['calls'] == 1 and x['editNotifications'] == 0 for x in callbacks)
        assert value['assistiveEditing']['ownerResults'] == 0
        assert value['assistiveEditing']['replacement'] == value['assistiveEditing']['redo'] == value['assistiveEditing']['insertDelete']
        assert {'go-to-assistive-edit-undo-redo', 'go-to-assistive-callback-vetoes'} <= {x['phase'] for x in value['actions']}
        assert len(value['actions']) == 32 and value['images'] == 49 and value['closedImages'] == 32
        assert value['nativeCompleteFramesMatch'] == 29 and value['nativeContractStatesMatch'] == 32 and value['nativeFrameComparisonStatus'] == 'failed'
        assert value['nativeRasterAcceptance'] == value['readerAcceptance'] == value['physicalInputAcceptance'] == 'pending'
    else:
        assert len(value['assistiveInput']) == 6 and value['strictObservationsMatch'] is False
        assert {(x['endpoint'], x['owner']) for x in value['assistiveInput']} == {(endpoint, owner) for endpoint in ['start', 'end'] for owner in ['echo', 'ignore', 'delay']}
        assert value['visualAcceptance'] == value['readerPhysicalAcceptance'] == 'pending'


def capture_result(value, module):
    assert value['exitCode'] == value['captureExitCode'] == 0 and value['acknowledgedAfterActualSessionCapture'] is True
    assert value['consumerSha256'] == CONSUMER and value['installedLibrarySha256'] == module
    for key in ['sourceProjectsMounted', 'productBuildMounted', 'consumerBuildMounted', 'physicalInput', 'accepted']:
        assert value[key] is False


def capture_image(raw):
    with Image.open(io.BytesIO(raw)) as image:
        image.load(); assert image.size == (2560, 1920) and image.format == 'PNG'
        assert any(low != high for low, high in image.convert('RGB').getextrema())


def reader_report(value, kind, profile, session):
    assert value['status'] == 'passed' and value['accepted'] is False
    assert len(value['phases']) == (21 if kind == 'goto' else 12)
    assert session['exitCode'] == 0 and session['profile'] == profile
    if kind == 'goto':
        assert value['profile'] == profile
        assert value['directAssistiveTextEdit'] == value['nativeKeyFlow'] == 'passed'
        assert value['physicalInput'] is value['physicalListening'] is False
        assert value['nativeAccessibilityAcceptance'] == value['nativeReaderComparison'] == 'pending'
        assert {'go-to-editable-text-prefix', 'go-to-editable-text-insert-delete', 'go-to-editable-text-native-undo-redo',
                'go-to-editable-text-navigates-without-owner', 'go-to-editable-text-unicode-proposal',
                'go-to-editable-text-missing-stays-modal', 'go-to-final-cancel-restores-caller'} <= {x['phase'] for x in value['phases']}


def verify(directory=DIRECTORY, current=False):
    capsule = manifest(directory)
    limits(json.loads((directory / 'validation.json').read_text()))
    executed = json.loads((directory / 'runtime-binding.json').read_text()); binding(capsule, executed)
    inventory_snapshot(json.loads((directory / 'inventory-binding.json').read_text()))
    if current: candidate({name: sha((ROOT / name).read_bytes()) for name in executed['files']}, executed['files'])
    first = capsule.record('source1/controller/result.json'); assert first['exitCode'] == 125
    assert 'No such image' in capsule.raw('source1/controller/configure.log').decode()
    failed = capsule.record('source2/controller/qualification.json')
    assert failed['controllerExitCode'] == 1 and failed['applicationExecuted'] is failed['applicationCrashReproduced'] is False
    assert failed['configureExitCode'] == 0 and failed['sourceUnchanged'] is True and failed['resultJsonAbsent'] is True
    assert 'no space left on device' in capsule.raw('source2/controller/build.log').decode().lower()
    before = capsule.record('source3/controller/result.json'); assert before['applicationExecuted'] and before['sourceUnchanged']
    crash(capsule.raw('source3/controller/path-assistive-destruction.log').decode(), before['exitCode'])
    matrix = capsule.record('baseline-matrix/result.json'); assert matrix['recordingComplete'] and matrix['compiledBinariesUnchanged']
    assert capsule.record('baseline-matrix/inputs.json')['binaryHashes']['src/Avelino/libAvelino.so'] == BASE_MODULE
    for name in NOTIFICATIONS[1:]: crash(capsule.raw('baseline-matrix/' + name + '.log').decode(), matrix['applicationExitCodes'][name])
    assert matrix['applicationExitCodes']['stale-callbacks'] == 4
    assert '2 passed, 4 failed, 0 skipped' in capsule.raw('baseline-matrix/stale-callbacks.log').decode()
    for name in ['qt-history', 'qt-validation', 'actual-owner-removal']: assert matrix['applicationExitCodes'][name] == 0
    after = capsule.record('source4/controller/result.json'); assert after['exitCode'] == 0 and after['sourceUnchanged']
    qt_log(capsule.raw('source4/controller/path-assistive-destruction.log').decode(), 'FileInputUiTests', 12)
    for n in [3, 4]:
        commands = capsule.record(f'source{n}/controller/commands.json')
        assert [x['name'] for x in commands] == ['configure', 'build', 'path-assistive-destruction']
        assert [x['exitCode'] for x in commands] == [0, 0, 139 if n == 3 else 0]
        assert all(BASE_IMAGE in x['command'] and not any('CMAKE_CXX_FLAGS' in part for part in x['command']) for x in commands)
    helper_move(capsule.raw('source3/implementation/src/Avelino/daterangeinput.cpp').decode(),
                capsule.raw('source4/implementation/src/Avelino/daterangeinput.cpp').decode(),
                capsule.raw('source4/implementation/src/Avelino/assistivetextinput_p.h').decode())
    validation = capsule.record('validation/result.json')
    assert capsule.record('validation/inputs.json')['librarySha256'] == FIX_MODULE
    assert validation['exitCode'] == 0 and validation['completedStages'] == validation['expectedStages'] == 5
    assert validation['sourceUnchanged'] and validation['libraryUnchanged'] and validation['fullQtSuiteExecuted'] is False
    for dpr in [1, 2]:
        qt_log(capsule.raw(f'validation/file-input-ui-dpr{dpr}.log').decode(), 'FileInputUiTests', 38)
        qt_log(capsule.raw(f'validation/date-range-ui-dpr{dpr}.log').decode(), 'DateRangeUiTests', 48)
    package = capsule.record('package1/controller/result.json'); installed = package['installedFiles']
    assert package['exitCode'] == 0 and package['completedStages'] == package['expectedStages'] == 4 and len(installed) == 158
    assert capsule.record('package1/controller/inputs.json')['freshConsumerBuild'] is True
    built = capsule.record('consumer2/controller/result.json')
    assert built['exitCode'] == 0 and built['consumerSha256'] == CONSUMER and built['installedPrefixUnchanged'] and built['consumerSourcesUnchanged']
    runtime = capsule.record('consumer-runtime/controller/inputs.json'); package_inputs(runtime, installed)
    assert runtime['consumerSha256'] == CONSUMER and runtime['imageId'] == BASE_IMAGE
    result = capsule.record('consumer-runtime/controller/result.json')
    assert result['exitCode'] == 0 and result['profilesPassed'] == result['expectedProfiles'] == 4 and result['consumerUnchanged'] and result['installedPrefixUnchanged']
    for fixture in ['file-input', 'date-range']:
        for dpr in [1, 2]:
            prefix = f'consumer-runtime/output/{fixture}-dpr{dpr}/'
            consumer_report(capsule.record(prefix + 'report.json'), fixture, dpr)
            capture_result(capsule.record(prefix + 'capture-result.json'), installed['lib/qml/Avelino/libAvelino.so'])
            capture_image(capsule.raw(prefix + 'full-session.png'))
            assert '/package/install/lib/qml/Avelino/libAvelino.so' in capsule.raw(prefix + 'loaded-library-maps.txt').decode()
    image = capsule.record('reader-image/result.json')
    assert image['exitCode'] == 0 and image['imageId'] == READER_IMAGE and image['qtVersion'] == '6.8.3'
    assert image['qtLibrariesUnchanged'] is True and image['historicalReaderImageRestored'] is False
    qt_lines = capsule.raw('reader-image/qt-libraries-sha256.txt').decode().splitlines(); assert len(qt_lines) == 5
    original = capsule.raw('reader-origins/goto-exercise.py').decode()
    assert sha(original.encode()) == GOTO_EXERCISE
    assert capsule.raw('reader-harness/goto/exercise.py').decode() == original.replace("p = Path('/probe')", "p = Path('/tmp/avelino-reader')")
    original_date = capsule.raw('reader-origins/date6/exercise.py')
    assert sha(original_date) == DATE_EXERCISE and capsule.raw('reader-harness/date/exercise.py') == original_date
    for kind in ['goto', 'date']:
        for number in [1, 2]:
            prefix = f'readers/{kind}{number}/'; inputs = capsule.record(prefix + 'controller/inputs.json')
            assert inputs['installedFiles'] == installed and inputs['imageId'] == READER_IMAGE
            assert inputs['sourceProjectsMounted'] is inputs['productBuildMounted'] is inputs['consumerBuildMounted'] is False
            profile = {'accepted': False, 'backend': 'software' if number == 1 else 'opengl', 'protocol': 'xcb' if number == 1 else 'wayland', 'scaled': number == 2}
            assert inputs['profile'] == profile
            result = capsule.record(prefix + 'controller/result.json')
            assert result['exitCode'] == 0 and result['installedPrefixUnchanged'] and result['probeInputsUnchanged']
            operator_path = 'operator-controls-v1/result.json' if kind == 'goto' else 'operator-report.json'
            reader_report(capsule.record(prefix + 'output/' + operator_path), kind, profile, capsule.record(prefix + 'output/session-result.json'))
            environment = capsule.record(prefix + 'output/session-env.json')
            assert environment['QT_QPA_PLATFORM'] == profile['protocol'] and environment['QT_SCALE_FACTOR'] == str(number)
            if number == 1: assert environment['QT_QUICK_BACKEND'] == 'software'
            else: assert environment['QSG_RHI_BACKEND'] == 'opengl' and environment['WAYLAND_DISPLAY']
            log = capsule.raw(prefix + 'output/orca-debug.log').decode()
            assert 'SPEECH OUTPUT:' in log and 'SPEECH DISPATCHER: Speaking' in log
            assert '/package/install/lib/qml/Avelino/libAvelino.so' in capsule.raw(prefix + 'output/loaded-library-maps.txt').decode()
            for name, digest in inputs['probeFiles'].items(): assert sha(capsule.raw(prefix + 'output/' + name)) == digest
    environment = capsule.record('environment/postrestart-v2/result.json')
    assert environment['exitCode'] == 0 and environment['imageId'] == BASE_IMAGE and environment['oldImageRestored'] is False
    assert capsule.raw('environment/postrestart-v2/qt-version.log').strip() == b'6.8.3'
    recipe = capsule.record('environment/inputs.json')['files']
    originals = HISTORY.git_files(PARENT, sorted(recipe))
    assert len(recipe) == 14 and all(sha(originals[name]) == digest == sha(capsule.raw('environment/context/' + name)) for name, digest in recipe.items())
    print('Path assistive lifetime: ten crashes/four stale negatives,172 scoped Qt checks, four independent consumer profiles and four actual reader sessions verified; complete native parity pending')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--directory', type=Path, default=DIRECTORY); parser.add_argument('--current', action='store_true')
    arguments = parser.parse_args(); verify(arguments.directory, arguments.current)
