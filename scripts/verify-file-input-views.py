#!/usr/bin/env python3
"""Audit measured native chooser views without accepting a Linux implementation."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/file-input-views-20261017'


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    text = lambda name: (DIRECTORY / 'observations' / (name + '.ax.txt')).read_text()
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    report = read('investigation.json')
    assert report['accepted'] is report['physicalInput'] is report['independentBehaviorSourceReplay'] is False
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['expectedImagesChanged'] is False and report['approvedExceptions'] == [] and report['tolerance'] == 'none'
    for gate in ['physicalDisplayAcceptance', 'nativeReaderAcceptance', 'strictRasterAcceptance', 'completeContextCoverage', 'linuxImplementation']:
        assert report[gate] == 'pending', gate
    files = read('files.json')
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        raw = (DIRECTORY / name).read_bytes()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
    assert read('launch.json')['executableSha256'] == report['helperSha256'] == '8e3db8c9c0089e3365def776393f3b0b5ddeccbf8835aea9079e94022d907b70'
    assert read('result.json')['exitCode'] == 0
    fixtures = read('fixtures.json')['files']
    assert set(fixtures) == {'Alpha.txt', 'Bravo.txt', 'Charlie.txt', 'blocked.png', 'Folder/Child.txt'}
    for row in fixtures.values():
        raw = row['content'].encode()
        assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
    assert len(report['images']) == 5
    for name, row in report['images'].items():
        path = DIRECTORY / name
        assert sha(path.read_bytes()) == row['sourceSha256']
        assert row['resized'] is row['cropped'] is row['masked'] is row['artworkVerified'] is False
        with Image.open(path) as image:
            assert image.format == 'JPEG' and list(image.size) == row['pixels'] == [1760, 896]

    observed = report['observations']
    listing = text('list-name-ascending')
    names = re.findall(r'/fixtures/([^,\n]+), Value:', listing)
    assert names == ['Alpha.txt', 'blocked.png', 'Bravo.txt', 'Charlie.txt', 'Folder/']
    assert observed['listNameAscending'] == [name.rstrip('/') for name in names]
    assert 'Name, Value: AXAscendingSortDirection' in listing
    assert observed['listMetadataColumns'] == ['Name', 'Size', 'Kind', 'Date Added']
    for column in observed['listMetadataColumns']:
        assert 'button Description: ' + column in listing
    assert 'text 50 bytes' in listing and 'text Plain Text' in listing and 'text PNG image' in listing
    for phase, expected in [('list-two-selected', ['Alpha.txt', 'Bravo.txt']),
                            ('list-parent-and-child-selected', ['Alpha.txt', 'Folder/Child.txt']),
                            ('list-collapse-child-selection', ['Alpha.txt']),
                            ('list-collapse-only-child', [])]:
        actual = re.findall(r'text field \(selected[^\n]+/fixtures/([^,\n]+), Value:', text(phase))
        assert actual == expected, (phase, actual)
    expanded = text('list-folder-right-expands')
    assert 'row (selected, expanded) Secondary Actions: Collapse' in expanded
    assert '/fixtures/Folder/Child.txt' in expanded and 'Where:, Value: fixtures' in expanded
    for phase, expected in [('icons-two-retained', ['Alpha.txt', 'Bravo.txt']),
                            ('icons-after-cross-level-settled', ['Alpha.txt']),
                            ('icons-file-and-folder', ['Alpha.txt']),
                            ('icons-after-only-child', [])]:
        actual = re.findall(r'image \(selected\) ([^,\n]+)', text(phase))
        assert actual == expected, (phase, actual)
    assert 'button (disabled) Open' in text('icons-after-only-child')
    assert 'Where:, Value: fixtures' in text('icons-folder-single')
    assert 'image (selected) Folder, 1 item' in text('icons-folder-single')
    assert 'button Open, ID: OKButton' in text('icons-folder-single')
    assert 'Where:, Value: Folder' in text('icons-folder-open-navigates')
    assert 'button (disabled) Open' in text('icons-folder-open-navigates')
    retained = text('columns-after-icons-settled')
    assert 'Description: column view' in retained
    assert re.findall(r'text field \(selected[^\n]+/fixtures/([^,\n]+), Value:', retained) == ['Alpha.txt']
    reopened = text('reopened-mode')
    assert 'Description: List,' in reopened and '/fixtures/Folder/Child.txt' in reopened
    assert 'button (disabled) back' in reopened and 'button (disabled) Open' in reopened

    trace = read('observations/ui-trace.json')
    assert trace['accepted'] is False and trace['reference'] == report['reference']
    assert trace['steps'][-1]['phase'] == 'finished'
    callbacks = trace['steps'][-1]['results']
    assert len(callbacks) == 4
    relative = lambda row: [unquote(urlsplit(url).path).split('/fixtures/', 1)[1] for url in row['urls']]
    assert all(row['kind'] == 'success' and row['panelVisibleAtCallback'] is True for row in callbacks)
    assert relative(callbacks[0]) == observed['crossLevelListResultOrder'] == ['Folder/Child.txt', 'Alpha.txt']
    assert relative(callbacks[1]) == relative(callbacks[2]) == observed['columnReverseClicksResultOrder'] == ['Alpha.txt', 'Bravo.txt']
    assert relative(callbacks[3]) == ['Alpha.txt']
    assert observed['generalCrossDirectoryResultOrdering'] == observed['inputTiming'] == 'pending'
    print('FileInput views: native hierarchy, view selection retention/pruning and four callbacks; Linux and strict parity pending')


if __name__ == '__main__':
    verify()
