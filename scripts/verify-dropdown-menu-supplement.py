#!/usr/bin/env python3
"""Verify native label/image replay and preserve popup-placement differences."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/dropdown-menu-supplement-20261017'


def validate_report(report):
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['accepted'] is False and report['status'] == 'source-investigation; differences-retained'
    assert report['sourceFilesUnchanged'] == 89 and report['prebuiltLibraryInputs'] is False
    assert (report['filesCompared'], report['exactFiles'], report['differingFiles']) == (62, 59, 3)
    assert report['expectedImagesChanged'] is False and report['tolerance'] == 'none'
    assert report['approvedExceptions'] == []
    assert report['remainingAcceptance'] == ['independentMachineReplay', 'nativePopupPlacement',
        'physicalPointerKeyboard', 'nativeAccessibilityReaders']
    members = report['sourceOnlyArchive']['members']
    assert {row['path'] for row in members} == {'reference-source.tar', 'inputs.json',
        'behavior/tool/DropdownCommon.swift', 'behavior/tool/BehaviorMain.swift',
        'labels/tool/DropdownCommon.swift', 'labels/tool/CaptureMain.swift', 'labels/fixtures.json',
        'metrics/tool/DropdownCommon.swift', 'metrics/tool/CaptureMain.swift', 'metrics/fixtures.json'}


def verify(directory=DIRECTORY):
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    validate_report(report)
    files = read('files.json')
    assert set(files) == {str(f.relative_to(directory)) for f in directory.rglob('*')
        if f.is_file() and f.name != 'files.json'}
    for name, record in files.items():
        data = (directory / name).read_bytes()
        assert len(data) == record['bytes'] and hashlib.sha256(data).hexdigest() == record['sha256'], name
    replay = read('result.json')
    assert replay['accepted'] is False and replay['prebuiltLibraryInputs'] is False
    assert replay['sourceArchiveSha256'] == report['sourceOnlyArchive']['sha256']
    comparisons = replay['comparisons']
    assert len(comparisons) == 62 and sum(row['identical'] for row in comparisons) == 59
    for row in comparisons:
        kind, name = row['kind'], row['path']
        before = (directory / kind / 'original/output' / name).read_bytes()
        after = (directory / kind / 'replay/output' / name).read_bytes()
        assert (before == after) == row['identical']
        assert hashlib.sha256(before).hexdigest() == row['originalSha256']
        assert hashlib.sha256(after).hexdigest() == row['replaySha256']
        if kind == 'behavior':
            for content in [before, after]:
                steps = json.loads(content)['steps']
                assert not any(step['phase'] == 'fallback-cancel' for step in steps)
                assert next(step for step in steps if step['phase'] == 'after-cancel')['calls'] == ['duplicate']
                assert next(step for step in steps if step['phase'] == 'pointer-target')['target'] == 'Duplicate'
            assert before != after, 'Uncontrolled native placement differences must remain visible'
        else:
            assert before == after
    print('Dropdown native supplement: 59 exact label/image outputs; three popup-placement differences retained; acceptance pending')


if __name__ == '__main__':
    verify()
