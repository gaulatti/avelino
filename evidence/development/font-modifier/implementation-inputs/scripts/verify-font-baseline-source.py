#!/usr/bin/env python3
"""Audit public first-baseline measurements and preserve strict raster failures."""
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import struct
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/font-baseline-20261016'
spec = importlib.util.spec_from_file_location('font_baseline_contexts', ROOT / 'scripts/verify-font-modifier-source.py')
contexts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contexts)
REFERENCE = contexts.REFERENCE
ARCHIVE_SHA256 = 'a1838774f37f3ec4b7d825d20ec3242293dd997761bf66e785c6754abf6739ab'
INPUTS = {
    'README.md': 'eab143a8a2fdd260743a2ca743c1608a1a47029b1c692888d2398530014e4532',
    'reference-source.tar': contexts.SOURCE_SHA256,
    'replay.py': '25f7a956a2b938b6c30d5aa1fc1a1dc653bc498b575ebba5e3d33cf84e26d3e7',
    'tool/CaptureMain.swift': 'a7536e1dc16b2ad5a0c97b5f87de2bbc5dc46b22c64216a866675540463f7f55',
    'tool/Common.swift': contexts.INPUTS['tool/Common.swift'],
}
CONTENTS = {'own-font', 'system-font', 'nil-font', 'bold', 'italic', 'attributed', 'nested-font',
            'inner-scale', 'scaled-subtree', 'zero', 'empty-view', 'rectangle', 'hstack', 'vstack'}
WITNESS_DIFFERENCES = {('primary-ultraLight', 'light', 1, 1), ('secondary-ultraLight', 'light', 1, 1),
                       ('size-primary-48.0', 'light', 1.5, 2)}


def configurations():
    result = {name: value for name, value in contexts.configurations().items()
              if name.startswith('size-') or name == value['family'] + '-' + value['weight']
              or value['content'] in CONTENTS or name in ['text-empty', 'text-lines', 'text-unicode', 'text-bidi']}
    assert len(result) == 90
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['referenceRevision'] == REFERENCE and report['accepted'] is False
    assert report['linuxImplementation'] == report['rasterAcceptance'] == 'pending'
    assert report['expectedImagesChanged'] is False and report['approvedExceptions'] == []
    assert report['captureBackend'] == 'ImageRenderer firstTextBaseline parent'
    assert report['hostedWindowAcceptance'] == report['physicalDisplayAcceptance'] == report['screenReaderAcceptance'] == 'pending'
    files = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert files == set(report['files']) | {'investigation.json'}
    for name, expected in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == expected, name
    inputs, build, provenance = (read(name) for name in ['inputs.json', 'source-build-result.json', 'tooling-provenance.json'])
    assert inputs['reference'] == build['reference'] == provenance['reference'] == REFERENCE
    assert inputs['files'] == INPUTS and inputs['compiledInputs'] == provenance['compiledInputs'] == []
    assert build['sourceArchiveSha256'] == contexts.SOURCE_SHA256 and build['sourceFilesUnchanged'] == 89
    assert build['libraryBuiltFromSources'] is True and build['prebuiltLibraryInputs'] is False
    assert read('replay-build/source-build-result.json') == build
    assert provenance['sourceOnlyReplayArchiveSha256'] == ARCHIVE_SHA256
    assert provenance['sourceOnlyReplayMembers'] == sorted([*INPUTS, 'inputs.json'])
    assert provenance['independentMachineAvailability'] == 'pending' and provenance['accepted'] is False
    archive = Path(provenance['sourceOnlyReplayArchive'])
    if archive.exists():
        assert digest(archive) == ARCHIVE_SHA256
        with tarfile.open(archive) as source:
            assert sorted(member.name for member in source) == provenance['sourceOnlyReplayMembers']
            for name, expected in INPUTS.items():
                assert hashlib.sha256(source.extractfile(name).read()).hexdigest() == expected
    corpus = read('captures/captures.json')
    assert corpus['reference'] == REFERENCE and corpus['fixtures'] == 90
    configs = configurations()
    identity = lambda row: (row['configuration']['fixture'], row['appearance'], row['textScale'], row['dpr'])
    rows = corpus['captures']
    lookup = {identity(row): row for row in rows}
    assert len(rows) == len(lookup) == report['groups'] == 720
    assert set(lookup) == set(itertools.product(configs, ['light', 'dark'], [1, 1.5], [1, 2]))
    used = set()
    differences = set()
    for row in rows:
        assert row['configuration'] == configs[row['configuration']['fixture']]
        assert len(row['paths']) == len(row['states']) == 3
        images = []
        for name in row['paths']:
            name = 'captures/' + name
            assert name in files and name.endswith('.png')
            used.add(name)
            data = (directory / name).read_bytes()
            assert data[:8] == b'\x89PNG\r\n\x1a\n'
            assert struct.unpack('>II', data[16:24]) == (640*row['dpr'], 400*row['dpr'])
            images.append(data)
        assert row['publicProbedIdentical'] is True and images[0] == images[1], 'Baseline instrumentation changed public pixels'
        same = images[0] == images[2]
        assert row['publicWitnessIdentical'] is same
        if not same:
            differences.add(identity(row))
        assert row['states'][1] == row['states'][2], 'Expression witness changed geometry or baseline'
        unprobed, measured = row['states'][:2]
        assert unprobed['partInstances'] == unprobed['baselines'] == unprobed['ambientFontsAtProbe'] == {}
        empty = row['configuration']['content'] == 'empty-view'
        for state in row['states']:
            assert state['appearances'] == state['callerInstances'] == (0 if empty else 1)
            assert state['disappearances'] == 0
        parts, baselines = measured['partInstances'], measured['baselines']
        keys = {'parent', 'reference'} if empty else {'parent', 'reference', 'label', 'styled', 'root'}
        if row['configuration']['content'] in ['hstack', 'vstack']:
            keys.update(['first', 'second'])
        assert set(parts) == set(measured['ambientFontsAtProbe']) == keys
        assert set(baselines) == keys - {'parent'}
        assert all(len(values) == 1 for values in parts.values()), 'Baseline supplement contains only single emitted views'
        for values in parts.values():
            assert set(values[0]) == {'x', 'y', 'width', 'height'}
            assert all(math.isfinite(value) for value in values[0].values())
            assert values[0]['width'] >= 0 and values[0]['height'] >= 0
        assert all(math.isfinite(value) for value in baselines.values())
        parent, reference = parts['parent'][0], parts['reference'][0]
        assert reference['width'] == 3 and reference['height'] == baselines['reference'] == 30
        assert parent['x'] + parent['width']/2 == 320 and parent['y'] + parent['height']/2 == 200
        if empty:
            assert parent == reference
            continue
        assert parts['root'] == parts['styled'] == parts['label']
        label = parts['label'][0]
        assert baselines['root'] == baselines['styled'] == baselines['label']
        assert label['y'] + baselines['label'] == reference['y'] + 30
        assert label['x'] == parent['x'] and reference['x'] == label['x'] + label['width'] + 11
        assert parent['width'] == label['width'] + 14
        assert parent['y'] == min(label['y'], reference['y'])
        assert parent['height'] == max(label['y'] + label['height'], reference['y'] + 30) - parent['y']
        config = row['configuration']
        if config['fixture'] == 'text-empty':
            assert label['width'] == 0 and label['height'] == 14 and baselines['label'] == 11
        elif config['content'] == 'text' and config['fixture'] not in ['text-unicode', 'text-bidi']:
            assert baselines['label'] == math.floor(measured['ambientFontsAtProbe']['label']['ascent'] + .5)
        elif config['content'] in ['own-font', 'nil-font', 'system-font']:
            assert baselines['label'] == (31 if config['content'] == 'system-font' else 13)
    assert used == {name for name in files if name.startswith('captures/') and name.endswith('.png')}
    assert len(used) == 2160
    assert differences == WITNESS_DIFFERENCES
    assert report['publicProbePixelMatches'] == report['partAndBaselineWitnessMatches'] == 720
    assert report['publicWitnessPixelMatches'] == 717 and report['publicWitnessPixelDifferences'] == 3
    assert {tuple(row) for row in report['witnessDifferenceContexts']} == WITNESS_DIFFERENCES
    replay = read('clean-replay.json')
    assert replay['sourceOnlyRebuild'] is True
    assert replay['files'] == replay['identicalFiles'] == len(replay['outputs']) == 2161
    assert {row['file'] for row in replay['outputs']} == {name.removeprefix('captures/') for name in files if name.startswith('captures/')}
    for row in replay['outputs']:
        assert row['identical'] is True and row['originalSha256'] == row['replaySha256'] == digest(directory/'captures'/row['file'])
    return dict(groups=720, publicProbePixelMatches=720, publicWitnessPixelDifferences=3,
                sourceReplayFiles=2161, accepted=False)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
