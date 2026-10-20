#!/usr/bin/env python3
"""Verify bounded native path-sheet transitions; does not grant mirror acceptance."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/file-input-go-to-20261018'


def path_input(state):
    fields = [line for line in state.splitlines()
              if re.match(r'^\s*\d+ text field', line) and 'PathTextField' in line]
    assert len(fields) == 1, 'Expected one native path field'
    value = re.search(r'Value: (.*?)(?:, ID: PathTextField|$)', fields[0])
    return value[1] if value else ''


def proposals(state, selected_only=False):
    result = []
    selected = False
    for line in state.splitlines():
        if re.match(r'^\s*\d+ row ', line):
            selected = 'row (selected)' in line
        if 'list (disabled) Description: path, ID: ' in line:
            if not selected_only or selected:
                result.append(line.split('Description: path, ID: ', 1)[1])
    return result


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    text = lambda name: (DIRECTORY / 'captures' / (name + '.ax.txt')).read_text()
    report = read('investigation.json')
    assert report['accepted'] is report['physicalInput'] is report['independentBehaviorSourceReplay'] is False
    assert report['reusedExecutable'] is True
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['baseGit'] == 'ad13788a016cad428f8d4a4695e2190f86ee5c9f'
    assert report['expectedImagesChanged'] is False and report['tolerance'] == 'none' and report['approvedExceptions'] == []
    for gate in ['nativeReaderAcceptance', 'physicalDisplayAcceptance', 'strictRasterAcceptance',
                 'completeContextCoverage', 'generalSuggestionOrdering', 'generalRelativeResolution',
                 'inputTiming', 'otherTypeArraysAndPathSelection', 'linuxGoToImplementation']:
        assert report[gate] == 'pending', gate
    assert report['pasteBehavior'] == report['commandAAfterTab'] == 'unproven'
    files = read('files.json')
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*')
                          if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        raw = (DIRECTORY / name).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name

    launch, terminal, trace = read('launch.json'), read('result.json'), read('ui-trace.json')
    assert terminal['exitCode'] == 0 and trace['steps'][-1]['phase'] == 'finished'
    assert trace['pid'] == launch['pid'] and trace['reference'] == report['reference']
    previous = json.loads((ROOT / report['helperProvenance']).read_text())
    assert launch['executableSha256'] == report['helperSha256'] == previous['executableSha256']
    assert report['sourceLibraryObjectSha256'] == json.loads((ROOT /
        'evidence/reference-investigations/file-input-location-policy-20261017/investigation.json').read_text())['sourceLibraryObjectSha256']
    assert launch['command'][2] + '/Navigator Root' == report['fixtureRoot']
    assert all(step['configuration']['types'] == ['public.plain-text'] for step in trace['steps'])
    assert any(step.get('allowedContentTypes') == ['public.plain-text'] for step in trace['steps'])
    assert all(launch['startedAt'] <= step['recordedAt'] <= terminal['finishedAt'] for step in trace['steps'])
    callbacks = trace['steps'][-1]['results']
    assert len(callbacks) == report['successfulCallbacks'] == 1
    assert callbacks[0]['kind'] == 'success' and callbacks[0]['panelVisibleAtCallback'] is True
    assert [unquote(urlsplit(url).path) for url in callbacks[0]['urls']] == [report['fixtureRoot'] + '/Other.png']

    captures = read('captures.json')
    assert len(captures) == 57
    by_phase = {row['phase']: row for row in captures}
    complete = [row for row in captures if row['receiptAvailable']]
    partial = [row for row in captures if not row['receiptAvailable']]
    assert len(complete) == report['completedCaptureReceipts'] == 55
    assert len(partial) == report['partialAXCaptures'] == 2
    assert {row['phase'] for row in partial} == {'edit-menu-paste-availability', 'prefix-tab-completion'}
    for row in captures:
        assert row['filtered'] is True and len(row['sourceSha256']) == 64
        assert 'outline sidebar' not in text(row['phase'])
        if not row['receiptAvailable']:
            assert row['failure'] and row['phase'] in report['diagnostics'][2 if row['phase'].startswith('edit') else 3]
            continue
        receipt = read('captures/' + row['phase'] + '.receipt.json')
        assert receipt['pid'] == trace['pid'] and receipt['axSha256'] == row['sourceSha256']
        assert launch['startedAt'] <= receipt['capturedAt'] == row['capturedAt'] <= terminal['finishedAt']
        assert receipt['ownerResultCount'] == row['ownerResultCount'] == (1 if row['phase'] == 'other-png-owner-accepted' else 0)
    for operation in read('operations.json'):
        before, after = by_phase[operation['before']], by_phase[operation['after']]
        assert before['capturedAt'] <= after['capturedAt'], operation

    fixture = report['fixtureRoot']
    initial = text('prompt-initial')
    cleared = text('close-control-result')
    assert 'GoToWindow' in initial and path_input(initial).endswith('/fixtures/.Hidden')
    assert 'GoToWindow' in cleared and path_input(cleared) == '' and 'text Recents' in cleared
    assert path_input(text('absolute-alpha-proposal')) == '', 'Failed paste must not count as entered Alpha'
    assert path_input(text('absolute-alpha-typed')) == fixture + '/Alpha'
    assert 'Where:, Value: Alpha' in text('absolute-alpha-submitted')
    assert path_input(text('relative-child-proposal')) == 'Child'
    assert proposals(text('relative-child-proposal'), True) == [fixture + '/Alpha/Child']
    assert 'Where:, Value: Child' in text('relative-child-submitted')
    assert path_input(text('relative-parent-initial')) == 'Child'
    assert proposals(text('relative-parent-initial'), True) == [fixture + '/Alpha/Child/Child.txt']
    for phase in ['relative-parent-proposal', 'relative-parent-return']:
        assert path_input(text(phase)) == '..' and proposals(text(phase)) == []
    assert path_input(text('relative-parent-slash-proposal')) == '../'
    assert proposals(text('relative-parent-slash-proposal'), True) == [fixture + '/Alpha/Child']
    assert 'Where:, Value: Child' in text('relative-parent-slash-submitted')
    for phase in ['relative-parent-file-proposal', 'relative-parent-file-return']:
        assert path_input(text(phase)) == '../A.txt' and proposals(text(phase)) == []
    assert path_input(text('after-invalid-retained-input')) == '../'
    assert path_input(text('absolute-missing-return')) == fixture + '/Missing'
    assert proposals(text('absolute-missing-return')) == []
    cancelled = text('absolute-missing-cancel')
    assert 'text field (selected, settable) Value: Child.txt' in cancelled and 'button Open, ID: OKButton' in cancelled
    assert path_input(text('absolute-missing-did-not-save')) == '../'
    clicked = text('recent-alpha-single-click')
    assert path_input(clicked) == '' and proposals(clicked, True) == [fixture + '/Alpha']
    assert 'Where:, Value: Alpha' in text('recent-alpha-pointer-double-click')
    assert path_input(text('after-recent-double-click-initial')) == ''

    prefix = fixture + '/Al'
    proposal = text('absolute-prefix-proposal')
    down = text('absolute-prefix-down')
    assert path_input(proposal) == path_input(down) == prefix
    assert proposals(proposal) == [fixture + '/' + name for name in ['Alpha', 'Alpine', 'Alphabet']]
    assert proposals(proposal, True) == [fixture + '/Alpha']
    assert proposals(down, True) == [fixture + '/Alpine']
    assert 'Where:, Value: Alpine' in text('absolute-prefix-selected-submit')
    assert path_input(text('absolute-prefix-retained')) == prefix
    assert path_input(text('paste-beta-result')) == prefix
    assert path_input(text('tab-trial-initial')) == prefix
    assert path_input(text('tab-trial-result')) == prefix + 'p'
    malformed = path_input(text('root-proposal'))
    assert malformed == fixture + '/Alp' + fixture
    assert path_input(text('root-retry-proposal')) == fixture
    assert 'Where:, Value: Navigator Root' in text('root-retry-submitted')
    ordinary, routed = text('other-png-ordinary-click'), text('other-png-path-submitted')
    assert 'Value: Other.png' in ordinary and 'text field (selected, settable) Value: Other.png' not in ordinary
    assert 'button (disabled) Open, ID: OKButton' in ordinary
    assert path_input(text('other-png-path-proposal')) == fixture + '/Other.png'
    assert 'text field (selected, settable) Value: Other.png' in routed and 'button Open, ID: OKButton' in routed

    assert len(report['images']) == 20 and len(report['omittedImages']) == 9
    for name, row in report['images'].items():
        raw = (DIRECTORY / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['sourceSha256']
        assert all(row[key] is False for key in ['resized', 'cropped', 'masked', 'reencoded', 'artworkVerified'])
        with Image.open(DIRECTORY / name) as image:
            assert image.format == row['format'] == 'JPEG' and list(image.size) == row['pixels']
    for name, row in report['omittedImages'].items():
        assert row['reason'] and not (DIRECTORY / 'captures' / name).exists()
    fixtures = read('fixtures.json')
    assert len(fixtures['files']) == 5 and len(fixtures['directories']) == 8
    for row in fixtures['files'].values():
        raw = row['content'].encode()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
    print('FileInput Go to Folder: 55 complete receipts, 2 partial AX captures, 20 original images; bounded native navigation and one callback; parity pending')


if __name__ == '__main__':
    verify()
