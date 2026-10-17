#!/usr/bin/env python3
"""Keep fresh FileInput type observations separate from retained/physical gates."""
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/file-input-types-20261017'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'


def validate_report(report):
    assert report['reference'] == REFERENCE and report['accepted'] is False
    assert report['status'] == 'native type supplement; Linux implementation pending'
    assert report['cases'] == 4 and report['successCallbacks'] == 3 and report['returnedUrls'] == 5
    assert report['controlledAXObservations'] == 16 and report['freshPublicItemSelection'] == 'passed'
    for key in ['retainedTypeUpdateAcceptance', 'nativePanelInputAcceptance',
            'physicalInputAcceptance', 'readerAcceptance', 'freshSourceBehaviorReplay']:
        assert report[key] == 'pending'
    assert report['sourceOnlyArchiveAvailability'] == 'pending independent-machine replay'
    assert report['expectedImagesChanged'] is False
    assert report['tolerance'] == 'none' and report['approvedExceptions'] == []


def verify(directory=DIRECTORY):
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    validate_report(report)
    files = read('files.json')
    assert set(files) == {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        path = PurePosixPath(name)
        assert str(path) == name and not path.is_absolute() and '..' not in path.parts
        file = directory / name
        assert file.stat().st_size == row['bytes'] and hashlib.sha256(file.read_bytes()).hexdigest() == row['sha256'], name
    inputs = read('inputs.json')
    assert inputs['sourceArchiveSha256'] == 'ab7ff095cdcd10ff6816b09997ccdce5bed57e689d5077b079b9cc961e166bea'
    assert inputs['sourceBuildResult']['sourceFilesUnchanged'] == 89
    assert inputs['sourceBuildResult']['exitCode'] == read('build-command.json')['exitCode'] == 0
    cases = {
        'types-item': (['public.item'], ['public.item'], False, ['one.txt']),
        'types-mixed': (['public.plain-text', 'public.image'], ['public.plain-text', 'public.image'], False, ['one.txt', 'photo.png']),
        'types-file-and-folder': (['public.folder', 'public.plain-text'], ['public.folder', 'public.plain-text'], True, ['folder/', 'one.txt']),
        'types-custom': (['org.avelino.fixture'], [], False, []),
    }
    root = 'file:///Users/gaulatti/.codex/tmp/avelino-file-input-fixtures-20261017-v1/'
    for case, (types, panelTypes, directories, names) in cases.items():
        fixture = read(case + '/fixture.json')
        assert fixture['types'] == types
        assert read(case + '/result.json') == dict(exitCode=0, accepted=False)
        assert read(case + '/command.json')['exitCode'] == 0
        trace = read(case + '/output/ui-trace.json')
        assert trace['reference'] == REFERENCE and trace['accepted'] is False
        assert trace['steps'][0]['phase'] == 'initial' and trace['steps'][-1]['phase'] == 'finished'
        assert all(step['configuration']['types'] == types for step in trace['steps'])
        panels = [step for step in trace['steps'] if step['phase'] == 'panel-ready']
        assert panels
        for panel in panels:
            assert panel['allowedContentTypes'] == panelTypes
            assert panel['canChooseFiles'] is True and panel['canChooseDirectories'] is directories
            assert panel['allowsMultipleSelection'] is True
        result = trace['steps'][-1]['results']
        assert result == ([dict(kind='success', ordinal=0, panelVisibleAtCallback=True,
            urls=[root + name for name in names])] if names else [])
    ax = read('cua-observations.json')
    assert ax['fileInputInitialCuaVersion'] == 1 and len(ax['observations']) == 16
    states = {(row['type'], row['phase']): row['state'] for row in ax['observations']}
    assert 'button Open' in states['public.item', 'fresh-one-selected']
    assert '(disabled) Open' in states['custom', 'text-click']
    retained = json.loads((ROOT / report['priorRetainedFailure']).read_text())
    state = next(row['state'] for row in retained['observations'] if row['phase'] == 'item-filter-file-click')
    assert '(disabled) Open' in state
    print('FileInput types: fresh item, text/image and directory/text selections; custom exclusion; retained gates pending')


if __name__ == '__main__':
    verify()
