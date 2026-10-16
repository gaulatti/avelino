#!/usr/bin/env python3
"""Audit standalone native Activity labels and the original Qt fitting failures."""
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/activity-text-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
CHECKPOINT = 'a332c3b652b507d53d8124210f48fb4f4c157c7d'
SOURCE_SHA256 = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['referenceRevision'] == REFERENCE and report['accepted'] is False
    assert report['approvedExceptions'] == [] and report['expectedImagesChanged'] is False
    names = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert names == set(report['files']) | {'investigation.json'}
    for name, expected in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == expected, name
    provenance, inputs, build = (read(name) for name in ['tooling-provenance.json', 'inputs.json', 'source-build-result.json'])
    assert provenance['compiledInputs'] == [] and provenance['independentMachineAvailability'] == 'pending'
    assert provenance['sourceFiles'] == build['sourceFilesUnchanged'] == 89
    assert provenance['sourceTree'] == 'db61113381a51fc3c7b3d12786609cd9e76627c8'
    assert provenance['reference'] == inputs['reference'] == build['reference'] == REFERENCE
    assert provenance['sourceArchiveSha256'] == build['sourceArchiveSha256'] == inputs['files']['reference-source.tar'] == SOURCE_SHA256
    assert set(inputs['files']) == {'reference-source.tar', 'Main.swift', 'replay.py'}
    assert build['libraryBuiltFromSources'] is True and build['prebuiltLibraryInputs'] is False
    replay = read('clean-replay.json')
    assert replay['files'] == replay['byteIdenticalFiles'] == 1 and replay['mismatches'] == []
    assert len(replay['outputs']) == 1 and replay['outputs'][0]['file'] == 'queries.json'
    output = replay['outputs'][0]
    assert output['identical'] is True and output['originalSha256'] == output['replaySha256'] == digest(directory / 'queries.json')
    native = read('queries.json')
    assert native['reference'] == REFERENCE
    rows = native['queries']
    styles = [('title', 1), ('detail', 1), ('timestamp', 1), ('review', 1), ('review', 1.5), ('archive', 1), ('archive', 1.5)]
    expected = {(key, scale, width / 2, dpr) for (key, scale), width, dpr in itertools.product(styles, range(241), [1, 2])}
    key = lambda row: (row['key'], row['textScale'], row.get('proposalWidth', row.get('proposal')), row['dpr'])
    assert len(rows) == 3374 and {key(row) for row in rows} == expected, 'Standalone Text proposal coverage changed'
    labels = dict(title='Edition updated', detail='Ready for review', timestamp='2 min ago', review='Review', archive='Archive')
    for row in rows:
        assert row['text'] == labels[row['key']]
        rect = row['rect']
        assert rect['x'] + rect['width'] / 2 == 360 and rect['y'] + rect['height'] / 2 == 500
        assert 0 <= rect['height'] <= 1000 and rect['width'] >= 0
    lookup = {key(row): row for row in rows}
    assert lookup['detail', 1, 54, 1]['rect']['height'] == 45
    assert lookup['review', 1, 10, 1]['rect']['height'] == 96
    assert lookup['review', 1, 10, 2]['rect']['height'] == 80
    assert lookup['timestamp', 1, 40, 2]['rect']['width'] == 28
    qt = read('qt-probe/comparison.json')
    assert qt['reference'] == REFERENCE and qt['accepted'] is False and qt['candidateRevision'] == CHECKPOINT
    # Audit the original diagnostic against its immutable Git object, so a
    # subsequent production typography fix cannot rewrite the original failure.
    historical = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{CHECKPOINT}:src/Avelino/buttonlabel.cpp'])
    assert hashlib.sha256(historical).hexdigest() == qt['buttonLabelSha256']
    assert digest(directory / 'qt-probe/tst_text.qml') == qt['diagnosticSha256']
    probe = (directory / 'qt-probe/tst_text.qml').read_text()
    assert json.dumps(rows, separators=(',', ':')) in probe, 'Qt probe source inputs changed'
    assert qt['queries'] == 3374 and qt['mismatchCount'] == 185 and qt['matchingQueries'] == 3189
    assert len(qt['profiles']) == 2 and len(qt['mismatches']) == 185
    observed = []
    for profile, dpr, count, widths, heights in zip(qt['profiles'], [1, 2], [165, 20], [161, 20], [8, 4]):
        assert profile == dict(dpr=dpr, queries=1687, mismatches=count, widthMismatches=widths, heightMismatches=heights)
        lines = (directory / f'qt-probe/qt-dpr{dpr}.log').read_text().splitlines()
        failures = [json.loads(line.split('TEXT_MISMATCH ', 1)[1]) for line in lines if 'TEXT_MISMATCH ' in line]
        assert len(failures) == count and len({key(row) for row in failures}) == count
        assert any(f'TEXT_SUMMARY 1687 {count}' in line for line in lines)
        for row in failures:
            assert row['source'] == lookup[key(row)]['rect'] and row['dpr'] == dpr
            assert row['qt']['width'] != row['source']['width'] or row['qt']['height'] != row['source']['height']
        observed += failures
    assert observed == qt['mismatches'], 'Original Qt failures cannot be projected into success'
    return dict(queries=3374, replayIdenticalFiles=1, originalQtMismatches=185, originalQtMatches=3189)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
