#!/usr/bin/env python3
"""Preserve and verify the graphical whole-second interpretation correction."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/date-range-interpretation-20261018'


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    files = read('files.json')
    assert set(files) == {str(path.relative_to(DIRECTORY)) for path in DIRECTORY.rglob('*')
        if path.is_file() and path != DIRECTORY / 'files.json'}
    for name, row in files.items():
        path = DIRECTORY / name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name
    receipt = read('correction.json')
    assert receipt['accepted'] is receipt['referenceImagesChanged'] is receipt['rawObservationsChanged'] is False
    before = read('before/input/files.json')
    source = ROOT / 'evidence/reference-investigations/date-range-input-20261018'
    after = json.loads((source / 'files.json').read_text())
    assert before.keys() == after.keys()
    changed = {name for name in before if before[name] != after[name]}
    assert changed == {'README.md', 'cases.json', 'cua-annotations.json'}
    for name in changed:
        assert digest(DIRECTORY / 'before/input' / name) == before[name]['sha256']
        assert digest(source / name) == after[name]['sha256']
    for name in before.keys() - changed:
        assert digest(source / name) == before[name]['sha256']
    assert receipt['changedInterpretiveMembers'] == sorted(changed)
    journal = json.loads((source / 'output/journal.json').read_text())
    cases = json.loads((source / 'cases.json').read_text())
    states = {name: journal['records'][cases[name]['observationOrdinal']]['state']
        for name in ['graphical-keyboard-preview', 'graphical-space-commit']}
    preview = states['graphical-keyboard-preview']
    assert preview['model']['start'] == 1710259200.625
    native = preview['nativeControls']['datePickers'][0]['date']
    assert native == 1710345600
    assert datetime.fromtimestamp(native, timezone.utc).isoformat() == '2024-03-13T16:00:00+00:00'
    assert native % 86400 == 57600 and preview['model']['start'] % 86400 == 57600.625
    assert states['graphical-space-commit']['model']['start'] == native
    assert 1710288000 != native
    assert '1710288000' in (DIRECTORY / 'first-linux-regression.log').read_text()
    assert '1710345600' in (DIRECTORY / 'first-linux-regression.log').read_text()
    followup = read('nonzero-time/output/journal.json')
    annotations = read('nonzero-time/annotations.json')
    assert len(annotations) == 2
    first, second = [followup['records'][row['ordinal']]['state'] for row in annotations]
    assert first['model']['start'] == 1709990861.625
    assert first['nativeControls']['datePickers'][0]['date'] == 1710077261
    assert second['model']['start'] == 1710077261
    assert datetime.fromtimestamp(1710077261, timezone.utc).isoformat() == '2024-03-10T13:27:41+00:00'
    assert read('nonzero-time/termination.json')['processAbsent'] is True
    print('DateRange interpretation corrected: graphical keyboard preview retains 16:00:00, discards fractional seconds; every native raw observation and image is unchanged')


if __name__ == '__main__':
    verify()
