#!/usr/bin/env python3
"""Audit only the verified empty-field native Close transition."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/file-input-go-to-empty-close-20261018'


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    report, launch, terminal, trace = [read(name) for name in ['investigation.json', 'launch.json', 'result.json', 'ui-trace.json']]
    assert report['accepted'] is report['physicalInput'] is report['independentBehaviorSourceReplay'] is False
    assert report['reference'] == trace['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['baseGit'] == '78708f69205379cc858f596a913bb32063c16b9e'
    assert report['expectedImagesChanged'] is False and report['tolerance'] == 'none' and report['approvedExceptions'] == []
    assert report['reusedExecutable'] is True and report['helperSha256'] == launch['executableSha256']
    prior = json.loads((ROOT / 'evidence/reference-investigations/file-input-location-policy-20261017/helper-inputs.json').read_text())
    assert report['helperSha256'] == prior['executableSha256']
    for gate in ['strictRasterAcceptance', 'nativeReaderAcceptance', 'completeContextCoverage']:
        assert report[gate] == 'pending'
    assert terminal['exitCode'] == 0 and trace['steps'][-1]['phase'] == 'finished'
    assert all(step['results'] == [] for step in trace['steps'])
    files = read('files.json')
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        raw = (DIRECTORY / name).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
    captures = read('captures.json')
    assert len(captures) == 17 and len(report['excludedSetupImages']) == 4
    for row in captures:
        assert row['filtered'] is True and len(row['sourceSha256']) == 64
        receipt = read(row['phase'] + '.receipt.json')
        assert receipt['pid'] == launch['pid'] == trace['pid'] and receipt['ownerResultCount'] == 0
        assert receipt['axSha256'] == row['sourceSha256']
        assert launch['startedAt'] <= receipt['capturedAt'] <= terminal['finishedAt']
        assert 'outline sidebar' not in (DIRECTORY / (row['phase'] + '.ax.txt')).read_text()
    before = (DIRECTORY / 'root-initial.ax.txt').read_text()
    after = (DIRECTORY / 'root-cleared.ax.txt').read_text()
    fields = [line for line in before.splitlines() if re.match(r'^\s*\d+ text field', line) and 'PathTextField' in line]
    assert len(fields) == 1 and 'Value:' not in fields[0]
    assert 'GoToWindow' in before and 'CloseButton' in before
    assert 'GoToWindow' not in after and 'ID: open-panel' in after
    assert read('root-initial.receipt.json')['capturedAt'] <= read('root-cleared.receipt.json')['capturedAt']
    assert report['observations'] == {'emptyCloseDismisses': True, 'relativeResolution': 'unproven', 'retryReturnTarget': 'unproven'}
    assert len(report['diagnostics']) == 3
    assert not list(DIRECTORY.glob('*.jpg')), 'Excluded setup images cannot be treated as accepted target captures'
    print('FileInput native Close: empty field dismisses only the nested sheet; failed relative/retry setup retained without a resolution claim')


if __name__ == '__main__':
    verify()
