#!/usr/bin/env python3
"""Audit native location observations while preserving unresolved parity gates."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/file-input-location-20261017'


def selected_files(state):
    paths = []
    for line in state.splitlines():
        if 'text field (selected' not in line or 'URL: file:' not in line:
            continue
        relative = unquote(line.split('/fixtures/', 1)[1].split(',', 1)[0])
        if not relative.endswith('/'):
            paths.append(relative)
    return paths


def recent_names(state):
    recent = state.split('Recent Places', 1)[1]
    return re.findall(r'(?:\(selected\) )?(Menu Parent|Leaf), ID: retargetFromMenuItem:', recent)


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    text = lambda group, phase: (DIRECTORY / group / (phase + '.ax.txt')).read_text()
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    report = read('investigation.json')
    assert report['accepted'] is report['physicalInput'] is report['independentBehaviorSourceReplay'] is False
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['baseGit'] == '3db5e8ea5318f3c5a694c984a43d01e0cfe211ac'
    assert report['expectedImagesChanged'] is False and report['approvedExceptions'] == [] and report['tolerance'] == 'none'
    for gate in ['physicalDisplayAcceptance', 'nativeReaderAcceptance', 'strictRasterAcceptance', 'completeContextCoverage', 'linuxImplementation']:
        assert report[gate] == 'pending', gate
    assert report['menuArtworkVerified'] is False
    files = read('files.json')
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        raw = (DIRECTORY / name).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
    for group in ['root-too-narrow', 'corrected', 'fresh-process']:
        assert read(group + '/result.json')['exitCode'] == 0
        assert read(group + '/launch.json')['executableSha256'] == report['helperSha256'] == '8e3db8c9c0089e3365def776393f3b0b5ddeccbf8835aea9079e94022d907b70'
        trace = read(group + '/ui-trace.json')
        assert trace['reference'] == report['reference'] and trace['accepted'] is False
        assert trace['steps'][-1]['phase'] == 'finished'
    assert read('fresh-process/launch.json')['freshProcess'] is True
    assert read('corrected/ui-trace.json')['pid'] != read('fresh-process/ui-trace.json')['pid']
    first = read('root-too-narrow/ui-trace.json')['steps'][-1]['results']
    assert len(first) == 1 and first[0]['urls'] == ['<outside-controlled-fixtures>']
    assert read('root-too-narrow/limitation.json')['callbackUrlRedacted'] is True

    fixtures = read('fixtures.json')['files']
    assert set(fixtures) == {'Menu Parent/Parent.txt', 'Menu Parent/Leaf/First.txt', 'Menu Parent/Leaf/Second.txt', 'Alternate/Leaf/Other.txt'}
    for row in fixtures.values():
        raw = row['content'].encode()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    assert len(report['images']) == 5
    for name, row in report['images'].items():
        raw = (DIRECTORY / name).read_bytes()
        assert sha(raw) == row['sourceSha256']
        assert row['resized'] is row['cropped'] is row['masked'] is row['artworkVerified'] is False
        with Image.open(DIRECTORY / name) as image:
            assert image.format == 'JPEG' and list(image.size) == row['pixels']
    for row in report['accessibility']:
        assert row['filtered'] is True and len(row['sourceSha256']) == 64
        assert row['sourcePath'].startswith('/Users/gaulatti/.codex/tmp/avelino-file-input-location-20261017-v')
        state = (DIRECTORY / row['path']).read_text()
        assert all('/avelino-file-input-location-20261017-v2/fixtures/' in line for line in state.splitlines() if 'URL:' in line)

    observed = report['observations']
    menu = text('corrected', 'leaf-location-menu')
    ancestor = menu.split('Recent Places', 1)[0]
    assert re.findall(r'\d+ (Leaf|Menu Parent|fixtures), ID: retargetFromMenuItem:', ancestor) == observed['ancestorOrder']
    assert recent_names(menu) == []
    assert selected_files(text('corrected', 'leaf-selected')) == ['Menu Parent/Leaf/First.txt']
    current = text('corrected', 'current-item-keeps-selection-settled')
    assert selected_files(current) == ['Menu Parent/Parent.txt']
    assert 'button (disabled) back' in current and 'button (disabled) forward' in current
    assert 'menu Secondary Actions:' not in current
    for phase, folder in [('ancestor-back', 'Leaf'), ('ancestor-forward', 'Menu Parent'), ('recent-parent-navigation', 'Menu Parent'), ('recent-navigation-back', 'Leaf')]:
        state = text('corrected', phase)
        assert 'Where:, Value: ' + folder in state and 'button (disabled) Open' in state
        assert selected_files(state) == [], phase
    assert 'button back' in text('corrected', 'ancestor-forward')
    reopened = text('corrected', 'alternate-reopened-after-cancel')
    assert 'Where:, Value: Leaf' in reopened and '/fixtures/Alternate/Leaf/Other.txt' in reopened
    assert 'button (disabled) back' in reopened and selected_files(reopened) == []
    assert recent_names(text('corrected', 'after-success-menu')) == ['Menu Parent']
    assert recent_names(text('corrected', 'recent-after-cancel')) == ['Menu Parent']
    assert recent_names(text('corrected', 'two-successful-recents')) == observed['recentOrderAfterTwoSuccesses'] == ['Leaf', 'Menu Parent']
    assert recent_names(text('corrected', 'recents-after-browsing-older')) == observed['recentOrderAfterBrowsingOlder'] == ['Leaf', 'Menu Parent']
    assert recent_names(text('corrected', 'recents-after-reaccept')) == observed['recentOrderAfterReaccept'] == ['Menu Parent', 'Leaf']
    assert 'Where:, Value: Menu Parent' in text('corrected', 'nested-menu-escape')
    assert 'menu Secondary Actions:' not in text('corrected', 'nested-menu-escape')
    callbacks = read('corrected/ui-trace.json')['steps'][-1]['results']
    assert len(callbacks) == 3
    actual = []
    for row in callbacks:
        assert row['kind'] == 'success' and row['panelVisibleAtCallback'] is True and len(row['urls']) == 1
        path = unquote(urlsplit(row['urls'][0]).path)
        assert '/avelino-file-input-location-20261017-v2/fixtures/' in path
        actual.append(path.split('/fixtures/', 1)[1])
    assert actual == observed['successfulCallbackFiles'] == ['Menu Parent/Parent.txt', 'Menu Parent/Leaf/First.txt', 'Menu Parent/Parent.txt']

    assert recent_names(text('fresh-process', 'fresh-process-recents')) == observed['freshProcessRecentOrder'] == ['Menu Parent', 'Leaf']
    persisted = text('fresh-process', 'persisted-recent-leaf-selected-settled')
    assert 'Where:, Value: Leaf' in persisted and '/fixtures/Menu%20Parent/Leaf/First.txt' in persisted
    assert selected_files(persisted) == []
    initial = text('fresh-process', 'go-to-folder-initial')
    assert 'GoToWindow' in initial and 'ID: PathTextField' in initial
    missing = text('fresh-process', 'go-to-folder-missing')
    assert '/fixtures/missing' in missing and 'ID: PathTextField' in missing
    assert selected_files(text('fresh-process', 'go-to-folder-cancel-preserves-selection')) == ['Menu Parent/Leaf/First.txt']
    assert selected_files(text('fresh-process', 'after-file-path-prompt-cancel')) == ['Menu Parent/Parent.txt']
    assert read('fresh-process/ui-trace.json')['steps'][-1]['results'] == observed['freshProcessOwnerResults'] == []
    assert observed['generalRecentCapacityAndCrossApplicationScope'] == observed['inputTiming'] == 'pending'
    assert observed['recentUpdatesAcrossDirectoriesAndDirectorySelections'] == 'pending'
    assert report['pathInputLimitations'] and report['snapshotTransport'] and report['rootTooNarrowAttempt']
    print('FileInput locations: native ancestors, current-folder selection, recent ordering and process persistence; path and strict parity gates pending')


if __name__ == '__main__':
    verify()
