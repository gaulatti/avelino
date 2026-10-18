#!/usr/bin/env python3
"""Audit scoped native recent/path observations without accepting mirror parity."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/file-input-location-policy-20261017'


def path_input(state):
    fields = [line for line in state.splitlines()
              if re.match(r'^\s*\d+ text field', line) and re.search(r'ID: PathTextField(?:,|$)', line)]
    assert len(fields) == 1, 'Expected the native path-entry field'
    value = re.search(r'Value: (.*?)(?:, ID: PathTextField|$)', fields[0])
    assert value is not None, 'Expected the native path-entry value'
    return value[1]


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    text = lambda group, phase: (DIRECTORY / group / (phase + '.ax.txt')).read_text()
    relative = lambda result: [unquote(urlsplit(url).path).split('/fixtures/', 1)[1] for url in result['urls']]
    def recent(state):
        assert 'Recent Places' in state, 'Expected the captured Recent Places menu'
        return re.findall(r'(Mixed Root|Recent Child|Recent-\d\d), ID: retargetFromMenuItem:', state.split('Recent Places', 1)[1])
    report = read('investigation.json')
    assert report['accepted'] is report['physicalInput'] is report['independentBehaviorSourceReplay'] is False
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['baseGit'] == '2cdefcb79b8434e188191043f76791dd35fe338d'
    assert report['expectedImagesChanged'] is False and report['approvedExceptions'] == [] and report['tolerance'] == 'none'
    for gate in ['physicalDisplayAcceptance', 'nativeReaderAcceptance', 'strictRasterAcceptance', 'completeContextCoverage']:
        assert report[gate] == 'pending', gate
    assert report['linuxImplementation'] == 'in-progress'
    files = read('files.json')
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        raw = (DIRECTORY / name).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
    assert read('helper-build-command.json')['exitCode'] == 0
    assert read('helper-inputs.json')['executableSha256'] == report['helperSha256']
    assert len(report['sourceLibraryObjectSha256']) == 64
    assert read('run-a/result.json')['exitCode'] == -5
    assert 'unable to find bundle named Sabella_Sabella' in (DIRECTORY / 'run-a/helper.log').read_text()
    traces = {}
    for group in ['run-a2', 'run-b', 'run-c']:
        assert read(group + '/result.json')['exitCode'] == 0
        assert read(group + '/launch.json')['executableSha256'] == report['helperSha256']
        trace = read(group + '/ui-trace.json'); traces[group] = trace
        assert trace['reference'] == report['reference'] and trace['steps'][-1]['phase'] == 'finished'
        assert all('recordedAt' in step for step in trace['steps'])
        launch, result = read(group + '/launch.json'), read(group + '/result.json')
        for snapshot in read(group + '/snapshots.json'):
            assert snapshot['pid'] == trace['pid']
            assert launch['startedAt'] <= snapshot['capturedAt'] <= result['finishedAt']
            assert (DIRECTORY / group / (snapshot['phase'] + '.ax.txt')).is_file()
    assert len({trace['pid'] for trace in traces.values()}) == 3
    assert read('run-b/launch.json')['bundleIdentifier'] == 'org.avelino.FileInputLocationSecondProbe'
    for group, count in [('run-a2', 13), ('run-b', 2), ('run-c', 1)]:
        callbacks = traces[group]['steps'][-1]['results']; assert len(callbacks) == count
        for callback in callbacks:
            assert callback['kind'] == 'success' and callback['panelVisibleAtCallback'] is True
            assert all('/avelino-file-input-location-harness-20261017-v1/fixtures/' in url for url in callback['urls'])
    observed = report['observations']
    a = traces['run-a2']['steps'][-1]['results']
    assert relative(a[0]) == observed['crossDirectoryCallbackOrder'] == ['Mixed Root/Recent Child/Child.txt', 'Mixed Root/Root.txt']
    assert recent(text('run-a2', 'mixed-recent-menu'))[0] == observed['currentFolderRecordedForCrossDirectorySelection'] == 'Mixed Root'
    assert 'Recent Child' not in recent(text('run-a2', 'mixed-recent-menu'))
    expected = [f'Recent-{i:02}' for i in range(12, 2, -1)]
    assert observed['recentLimitObserved'] == len(expected) == 10
    assert recent(text('run-a2', 'capacity-recent-menu')) == observed['recentAfterCapacity'] == expected
    assert recent(text('run-b', 'initial-recent-menu')) == observed['secondConsumerInitialRecent'] == expected
    assert [relative(row) for row in a[1:]] == [[f'Recent-{i:02}/Mark.txt'] for i in range(1, 13)]
    b = traces['run-b']['steps'][-1]['results']
    assert relative(b[0]) == observed['selectedDirectoryResult'] == ['Mixed Root/Recent Child/']
    assert relative(b[1]) == observed['currentDirectoryResult'] == ['Mixed Root/']
    assert recent(text('run-b', 'directory-recent-menu'))[0] == observed['currentFolderRecordedForSelectedDirectory'] == 'Mixed Root'
    empty = text('run-b', 'directory-no-selection')
    assert 'text field (selected' not in empty and 'button Open, ID: OKButton' in empty
    missing = text('run-a2', 'missing-path-result')
    assert 'GoToWindow' in missing and '/fixtures/missing' in missing
    cancelled = text('run-a2', 'missing-path-cancel')
    assert 'text field (selected, settable) Value: Mark.txt' in cancelled
    after_missing = text('run-a2', 'existing-file-path-prompt')
    assert path_input(after_missing).endswith('/fixtures/Recent-12') and '/fixtures/missing' not in after_missing
    assert observed['cancelledInvalidPathDoesNotReplaceRememberedInput'] is True
    file_result = text('run-a2', 'existing-file-path-result')
    assert 'GoToWindow' not in file_result and 'text field (selected, settable) Value: Root.txt' in file_result
    same = text('run-a2', 'same-folder-path-result')
    assert 'text field (selected, settable) Value: Root.txt' in same
    assert path_input(text('run-a2', 'same-folder-path-prompt')).endswith('/Mixed Root/Root.txt')
    assert path_input(text('run-b', 'directory-root-prompt')).endswith('/fixtures/Mixed Root')
    c = traces['run-c']['steps'][-1]['results']
    assert relative(c[0]) == observed['pathSelectedNonmatchingFileResult'] == ['Mixed Root/Blocked.png']
    stable = text('run-c', 'blocked-file-stable'); pointer = text('run-c', 'blocked-pointer-selected')
    assert 'text field (selected, settable) Value: Blocked.png' in stable and 'button Open, ID: OKButton' in stable
    assert 'text field (selected, settable) Value: Blocked.png' not in pointer and 'button (disabled) Open' in pointer
    assert any(step.get('allowedContentTypes') == ['public.plain-text'] for step in traces['run-c']['steps'])
    assert 'Where:, Value: .Hidden' in text('run-c', 'hidden-folder-result')
    assert path_input(text('run-c', 'relative-parent-typed')) == '../Recent-12'
    assert 'Where:, Value: Recent Child' in text('run-c', 'relative-parent-result')
    assert path_input(text('run-c', 'hidden-folder-prompt')) == '../Recent-12'
    assert observed['inputTiming'] == observed['otherTypeArraysAndPathSelection'] == observed['generalCrossDirectoryResultOrder'] == 'pending'
    assert report['successfulCallbacks'] == 16
    assert len(report['images']) == 1
    for name, row in report['images'].items():
        assert hashlib.sha256((DIRECTORY / name).read_bytes()).hexdigest() == row['sourceSha256']
        assert row['resized'] is row['cropped'] is row['masked'] is row['artworkVerified'] is False
        with Image.open(DIRECTORY / name) as image:
            assert image.format == 'JPEG' and list(image.size) == row['pixels'] == [1760, 896]
    for row in report['accessibility']:
        assert row['filtered'] is True and len(row['sourceSha256']) == 64
    print('FileInput native policy: shared ten-folder pool, accepted visible locations and sixteen callbacks; scoped path observations, strict parity pending')


if __name__ == '__main__':
    verify()
