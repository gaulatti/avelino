#!/usr/bin/env python3
"""Audit navigation-only native path history separately from Recent Places."""
import hashlib
import json
from pathlib import Path
import re

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/file-input-go-to-history-20261018'


def path_input(state):
    fields = [line for line in state.splitlines()
              if re.match(r'^\s*\d+ text field', line) and 'PathTextField' in line]
    assert len(fields) == 1
    value = re.search(r'Value: (.*?)(?:, ID: PathTextField|$)', fields[0])
    return value[1] if value else ''


def paths(state):
    return re.findall(r'Description: path, ID: (.+)', state)


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    text = lambda run, phase: (DIRECTORY / run / (phase + '.ax.txt')).read_text()
    report = read('investigation.json')
    assert report['accepted'] is report['physicalInput'] is report['independentBehaviorSourceReplay'] is False
    assert report['reusedExecutable'] is True
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['baseGit'] == '0d88506df0ddf14b12eb39c5ebfde12dc867f2ac'
    assert report['expectedImagesChanged'] is False and report['tolerance'] == 'none' and report['approvedExceptions'] == []
    for gate in ['physicalDisplayAcceptance', 'nativeReaderAcceptance', 'strictRasterAcceptance',
                 'completeContextCoverage', 'generalHistoryCapacity', 'generalSuggestionRanking',
                 'unavailableTargetBehavior', 'generalRelativeResolution', 'inputTiming', 'linuxGoToImplementation']:
        assert report[gate] == 'pending', gate
    files = read('files.json')
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*')
                          if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        raw = (DIRECTORY / name).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
    captures = read('captures.json')
    assert len(captures) == 76
    previous = json.loads((ROOT / report['helperProvenance']).read_text())
    pids = set()
    for run, count in [('run-a', 61), ('run-b', 7), ('run-c', 8)]:
        launch, terminal, trace = read(run + '/launch.json'), read(run + '/result.json'), read(run + '/ui-trace.json')
        consumer = report['consumers'][run]
        pids.add(launch['pid'])
        assert terminal['exitCode'] == 0 and trace['steps'][-1]['phase'] == 'finished'
        assert consumer['pid'] == trace['pid'] == launch['pid']
        assert consumer['executableSha256'] == launch['executableSha256'] == previous['executableSha256']
        assert trace['reference'] == report['reference']
        assert all(step['results'] == [] for step in trace['steps'])
        assert all(step['configuration']['types'] == ['public.plain-text'] for step in trace['steps'])
        assert all(launch['startedAt'] <= step['recordedAt'] <= terminal['finishedAt'] for step in trace['steps'])
        group = [row for row in captures if row['run'] == run]
        assert len(group) == consumer['completedCaptures'] == count
        for row in group:
            assert row['filtered'] is True and len(row['sourceSha256']) == 64
            assert 'outline sidebar' not in text(run, row['phase'])
            receipt = read(run + '/' + row['phase'] + '.receipt.json')
            assert receipt['pid'] == trace['pid'] and receipt['axSha256'] == row['sourceSha256']
            assert receipt['ownerResultCount'] == row['ownerResultCount'] == 0
            assert launch['startedAt'] <= receipt['capturedAt'] == row['capturedAt'] <= terminal['finishedAt']
    assert len(pids) == 3 and report['successfulCallbacks'] == 0
    assert report['consumers']['run-a']['bundleIdentifier'] == report['consumers']['run-c']['bundleIdentifier'] == 'org.avelino.FileInputLocationProbe'
    assert report['consumers']['run-b']['bundleIdentifier'] == read('run-b/launch.json')['bundleIdentifier'] == 'org.avelino.FileInputLocationSecondProbe'

    fixture = report['fixtureRoot']
    assert path_input(text('run-a', 'initial-prompt')).endswith('/Navigator Root/Other.png')
    expected = [f'History-{i:02}' for i in range(1, 13)]
    assert report['navigatedFolders'] == expected
    for number, folder in enumerate(expected, 1):
        phase = 'history-' + str(number).zfill(2)
        initial = text('run-a', phase + '-initial')
        if number > 1:
            assert path_input(initial) == fixture + '/' + expected[number - 2]
        assert path_input(text('run-a', phase + '-cleared')) == ''
        proposal = text('run-a', phase + '-proposal')
        assert path_input(proposal) == fixture + '/' + folder
        assert paths(proposal)[0] == fixture + '/' + folder
        navigated = text('run-a', phase + '-result')
        assert 'GoToWindow' not in navigated and 'Where:, Value: ' + folder in navigated
        times = {row['phase']: row['capturedAt'] for row in captures if row['run'] == 'run-a'}
        assert times[phase + '-initial'] <= times[phase + '-cleared'] <= times[phase + '-proposal'] <= times[phase + '-result']
    latest = [f'History-{i:02}' for i in range(12, 7, -1)]
    assert report['emptyFieldRecents'] == latest
    empty = text('run-a', 'after-twelve-empty-recents')
    assert path_input(empty) == '' and 'text Recents' in empty
    assert paths(empty) == [fixture + '/' + folder for folder in latest]
    query = text('run-a', 'after-twelve-history-query')
    assert path_input(query) == 'History-' and paths(query) == paths(empty)
    oldest = text('run-a', 'after-twelve-oldest-query')
    assert path_input(oldest) == 'History-01'
    assert paths(oldest) == [fixture + '/' + name for name in ['History-12', 'History-11', 'History-09', 'History-08', 'History-10']]
    assert 'text Recents' in oldest
    old_file = text('run-a', 'old-path-query')
    assert path_input(old_file) == 'Other.png' and paths(old_file) == []
    assert path_input(text('run-a', 'cancelled-query-not-retained')) == fixture + '/History-12'
    where = text('run-a', 'where-after-navigation-only')
    assert 'Where:, Value: History-12' in where and 'Recent Places' in where
    recent = where.split('Recent Places', 1)[1]
    assert 'History-' not in recent and 'Navigator Root, ID: retargetFromMenuItem:' in recent
    assert path_input(text('run-b', 'initial-prompt')) == fixture + '/History-12'
    second = text('run-b', 'initial-empty-recents')
    assert path_input(second) == '' and paths(second) == paths(empty)
    selected = text('run-b', 'promote-ten-selected')
    assert 'row (selected)' in selected and path_input(selected) == ''
    assert 'Where:, Value: History-10' in text('run-b', 'promote-ten-result')
    promoted = ['History-10', 'History-12', 'History-11', 'History-09', 'History-08']
    assert report['afterPromotion'] == promoted
    state = text('run-b', 'promoted-recents')
    assert path_input(state) == '' and paths(state) == [fixture + '/' + folder for folder in promoted]
    assert len(set(paths(state))) == 5
    first_again = text('run-c', 'initial-promoted-recents')
    assert path_input(first_again) == '' and paths(first_again) == paths(state)
    assert 'History Root, ID: retargetFromMenuItem:' in text('run-c', 'ordinary-ancestor-menu')
    assert 'Where:, Value: History Root' in text('run-c', 'ordinary-parent-result')
    assert 'Where:, Value: History-01' in text('run-c', 'ordinary-child-result')
    ordinary = text('run-c', 'after-ordinary-navigation-recents')
    assert path_input(ordinary) == '' and paths(ordinary) == paths(state)

    earlier_path = ROOT / report['sourceOfEarlierTwelveRows']
    earlier = earlier_path.read_text()
    assert report['earlierTwelveRowsHeading'] == 'Go to:'
    assert 'text Go to:' in earlier and 'text Recents' not in earlier and len(paths(earlier)) == 12
    earlier_files = json.loads((earlier_path.parent.parent / 'files.json').read_text())
    earlier_name = str(earlier_path.relative_to(earlier_path.parent.parent))
    assert hashlib.sha256(earlier_path.read_bytes()).hexdigest() == earlier_files[earlier_name]['sha256']
    assert len(report['images']) == 10
    for name, row in report['images'].items():
        assert hashlib.sha256((DIRECTORY / name).read_bytes()).hexdigest() == row['sourceSha256']
        assert all(row[key] is False for key in ['resized', 'cropped', 'masked', 'reencoded', 'artworkVerified'])
        with Image.open(DIRECTORY / name) as image:
            assert image.format == row['format'] == 'JPEG' and list(image.size) == row['pixels']
    assert {tuple(row['pixels']) for row in report['images'].values()} == {(920, 690), (920, 430), (920, 494)}
    fixtures = read('fixtures.json')
    assert len(fixtures['files']) == 12 and len(fixtures['directories']) == 13
    for row in fixtures['files'].values():
        raw = row['content'].encode()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
    print('FileInput Go to Folder history: 76 complete captures, 3 terminal processes, 2 consumer identities; 5 observed recent paths, navigation-only promotion, zero callbacks; parity pending')


if __name__ == '__main__':
    verify()
