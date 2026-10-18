#!/usr/bin/env python3
"""Verify scoped native input observations; Linux mirror acceptance stays pending."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/date-range-input-20261018'


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    files = read('files.json')
    assert set(files) == {str(path.relative_to(DIRECTORY)) for path in DIRECTORY.rglob('*')
        if path.is_file() and path.name != 'files.json'}
    for name, row in files.items():
        path = DIRECTORY / name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name
    report = read('investigation.json')
    assert report['accepted'] is report['physicalInput'] is report['physicalDisplay'] is False
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['expectedImagesChanged'] is False and report['tolerance'] == 'none' and report['approvedExceptions'] == []
    assert report['desktopCandidateCoverage'] == [76, 80] and report['acceptedDesktopEntries'] == 0
    assert report['readerAcceptance'] == report['linuxImplementation'] == report['independentMachine'] == 'pending'
    journal = read('output/journal.json')
    records, events = journal['records'], journal['inputEvents']
    assert journal['accepted'] is False and journal['reference'] == report['reference']
    assert len(records) == report['records'] == report['rootImages'] == 116
    assert len(events) == report['events'] == 82
    assert {kind: sum(event['type'] == kind for event in events) for kind in [1, 2, 10, 11]} == {1: 15, 2: 15, 10: 26, 11: 26}
    assert [event['characters'] for event in events if event['type'] == 10 and event['characters'].isdigit()] == list('2026')
    images = set()
    for ordinal, record in enumerate(records):
        assert record['ordinal'] == ordinal
        raw = (DIRECTORY / 'output' / record['image']).read_bytes()
        assert struct.unpack('>II', raw[16:24]) == (1280, 800)
        images.add(record['image'])
        images.update(record['ownedWindowImages'])
    assert sum(len(row['ownedWindowImages']) for row in records) == report['ownedWindowImages'] == 52
    assert len(images) == 168 and images == {path.name for path in (DIRECTORY / 'output').glob('*.png')}
    cases = read('cases.json')
    assert len(cases) == report['cases'] == 21

    def state(name):
        case = cases[name]
        record = records[case['observationOrdinal']]
        assert case['image'] == record['image'] and case['imageSha256'] == digest(DIRECTORY / 'output' / record['image'])
        value = record['state']
        assert value['windowKey'] is value['applicationActive'] is value['activeSpace'] is True
        assert value['configuration']['locale'] == 'en_US' and value['configuration']['calendar'] == 'gregorian'
        assert value['configuration']['timeZone'] == 'UTC'
        return value

    for name in cases:
        state(name)
    for name, instant in [('keyboard-year', 1741536000.625), ('keyboard-day', 1741622400.625),
            ('typed-year', 1773158400.625), ('stepper-month', 1775836800.625), ('field-month-increment', 1712678400.625)]:
        value = state(name)
        assert value['model']['start'] == value['nativeControls']['datePickers'][0]['date'] == instant
        assert instant % 86400 == 57600.625
    initial = state('initial-calendar-request')['model']
    assert initial['start'] == initial['requests'][0]['requested'] == 1710000000.625
    assert state('ignored-caller-update')['model']['start'] == state('ignored-caller-update')['nativeControls']['datePickers'][0]['date'] == 1710000000.625
    applied = state('delayed-owner-apply')['model']
    assert applied['start'] == 1741536000.625 and applied['pending'] == {}
    for owner in ['ignore', 'delay']:
        values = []
        checksums = []
        for mode in range(3):
            name = owner + '-mode' + str(mode)
            value = state(name)
            model = value['model']
            assert value['mode'] == mode and value['configuration']['owner'] == owner
            assert model['start'] == 1710000000.625 and value['nativeControls']['datePickers'][0]['date'] == 1741536000.625
            assert model['end'] == 1710864000.125
            assert model['pending'] == ({} if owner == 'ignore' else {'start': 1741536000.625})
            assert model['requests'][-1]['requested'] == 1741536000.625
            values.append({key: model[key] for key in ['start', 'end', 'pending', 'requests']})
            checksums.append(cases[name]['imageSha256'])
        assert values[0] == values[1] == values[2] and len(set(checksums)) == 1
    assert all(row['pixelsEqual'] is row['bindingValuesEqual'] is True for row in read('owner-comparisons.json'))
    crossed = state('independent-end-crossing')['model']
    assert crossed['start'] == 1710000000.625 and crossed['end'] == 1679241600.125
    assert crossed['requests'][-1]['endpoint'] == 'end'
    calendar = state('calendar-pointer-selection')
    assert calendar['model']['start'] == 1741536000.625
    assert calendar['model']['pending'] == {'start': 1739894400.625}
    assert calendar['nativeControls']['datePickers'][0]['date'] == 1739894400.625
    for name, instant in [('upper-bound-clamp', 1711843200), ('lower-bound-clamp', 1709251200)]:
        value = state(name)
        assert value['model']['start'] == value['nativeControls']['datePickers'][0]['date'] == instant
    disabled = state('disabled-input')
    assert all(picker['enabled'] is False for picker in disabled['nativeControls']['datePickers'])
    assert disabled['model']['start'] == 1710000000.625 and disabled['model']['end'] == 1710864000.125
    assert len(disabled['model']['requests']) == 5
    preview, committed = map(state, ['graphical-keyboard-preview', 'graphical-space-commit'])
    assert preview['model']['start'] == 1710259200.625 and preview['nativeControls']['datePickers'][0]['date'] == 1710345600
    assert len(preview['model']['requests']) == 7
    assert committed['model']['start'] == committed['nativeControls']['datePickers'][0]['date'] == 1710345600
    assert len(committed['model']['requests']) == 8
    clock = datetime.fromtimestamp(committed['model']['start'], timezone.utc)
    assert (clock.hour, clock.minute, clock.second, clock.microsecond) == (16, 0, 0, 0)
    assert committed['model']['start'] % 86400 == 57600
    assert preview['model']['start'] % 86400 == 57600.625
    field = state('field-month-increment')
    assert field['nativeControls']['datePickers'][0]['style'] == 2 and len(field['windows']) == 1
    termination = read('termination.json')
    assert termination['terminatedViaCuaWindowClose'] is termination['processAbsent'] is True and termination['launcherExitCode'] == 0
    package = read('source-only-rebuild/package-files.json')
    artifact = read('source-only-rebuild/artifact.json')
    assert len(package) + 1 == artifact['files'] == 98 and artifact['pinnedSourceFiles'] == 89
    assert artifact['compiledOutputs'] is artifact['nativeInputReplay'] is False
    identity = json.loads((ROOT / 'evidence/reference-investigations/date-range-20261018/provenance/source-identity.json').read_text())
    assert {name.removeprefix('reference/'): row['sha256'] for name, row in package.items() if name.startswith('reference/')} == {row['path']: row['sha256'] for row in identity['fullSourceFiles']}
    inputs = read('producer-inputs.json')
    for name in ['DateCommon.swift', 'DateInteractive.swift']:
        checksums = [row['sha256'] for path, row in inputs.items() if path.endswith('/tool/' + name)]
        assert checksums == [package['tool/' + name]['sha256']]
    rebuilt = read('source-only-rebuild/replay-result.json')
    assert rebuilt['exitCode'] == 0 and rebuilt['sourceFilesUnchanged'] == 89
    assert rebuilt['prebuiltLibraryInputs'] is rebuilt['nativeInputReplayed'] is False
    assert report['sourceOnlyRebuild'] is True and report['nativeInputReplayedFromArchive'] is False
    print('Native DateRange input: 21 milestones, 82 OS events, exact six owner-state images, range and graphical preview/commit differences; complete native input and Linux acceptance pending')


if __name__ == '__main__':
    verify()
