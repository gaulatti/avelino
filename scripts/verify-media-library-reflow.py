#!/usr/bin/env python3
"""Audit the corrected media candidate and every preserved earlier observation."""
import importlib.util
import json
import io
from pathlib import Path
import tarfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/media-library-reflow-20261017'
PREVIOUS = ROOT / 'evidence/development/media-library-20261017'
spec = importlib.util.spec_from_file_location('media_evidence', ROOT / 'scripts/verify-media-library-candidate.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)

def validate_report(report):
    assert report['reference'] == evidence.inputs.REFERENCE and report['accepted'] is False
    assert report['baseRevision'] == '97fa3c1fd95eb3088271425eb5824344dcb82933'
    assert report['previousCandidateSha256'] == evidence.digest(PREVIOUS / 'candidate.json')
    assert report['status'] == 'verification-pending' and report['remainingAcceptance'] == evidence.GATES
    assert report['tolerance'] == 'none' and report['approvedExceptions'] == [] and report['expectedImagesChanged'] is False
    assert report['strictComparisonStatus'] == 'failed'
    summary = report['strictComparison']
    expected = dict(cases=1608, exactMatches=1008, pixelMatches=1168, nativeFrameMatches=1288,
        nativeLifecycleMatches=1608, stateMatches=1608, sizingObservations=0,
        nativeSizingContexts=496, nativeSizingQueries=7440, retainedRestoreObservations=48, retainedRestorePixelMatches=48)
    assert all(summary[k] == value for k, value in expected.items())
    assert summary['byKind'] == dict(closed=dict(cases=496, exactMatches=344),
        edge=dict(cases=104, exactMatches=80), history=dict(cases=1008, exactMatches=584))
    validation = report['validation']
    for key, value in dict(componentChecksDpr1=15, componentChecksDpr2=15, fullQtTargets=33,
            malformedConfigurations=13, isolatedCatalogInputs=76, independentModes=34, catalogCaptures=139,
            installedFiles=134, virtualProfiles=8, operatorControls=14, operatorClicks=23, operatorStates=24,
            operatorExactStates=20, strictDefaultExitCode=1, strictImageExitCode=1, fatalProcesses=8,
            virtualRestoreObservations=48, virtualRestorePixelMatches=48, legacyPngs=139, legacyMetadata=139).items():
        assert validation[key] == value, key
    assert validation['operatorStatus'] == 'failed'
    assert validation['physicalDisplay'] is False and validation['hardwareAcceleration'] is False

def verify(directory=DIRECTORY):
    directory = Path(directory)
    report = evidence.verify(directory, report_validator=validate_report)
    old = json.loads((PREVIOUS / 'comparison/comparison.json').read_text())
    new = json.loads((directory / 'comparison/comparison.json').read_text())
    previous = {r['fixture']: r for r in old['results']}
    current = {r['fixture']: r for r in new['results']}
    assert previous.keys() == current.keys() and len(current) == 1608
    for name, before in previous.items():
        after = current[name]
        for key in ['pixelStatus', 'nativeFrameStatus', 'nativeLifecycleStatus', 'stateStatus', 'retainedRasterStatus']:
            if before[key] == 'passed':
                assert after[key] == 'passed', (name, key)
    regression = json.loads((directory / 'regression/native-pairs.json').read_text())
    assert regression['comparedPairs'] == 1608 and regression['regressions'] == []
    assert regression['previousComparisonSha256'] == evidence.digest(PREVIOUS / 'comparison/comparison.json')
    assert regression['currentComparisonSha256'] == evidence.digest(directory / 'comparison/comparison.json')
    catalogs = json.loads((directory / 'regression/catalogs.json').read_text())
    assert catalogs['status'] == 'passed' and catalogs['accepted'] is False and len(catalogs['records']) == 139
    for row in catalogs['records']:
        for suffix, before_key, after_key in [('', 'previousSha256', 'currentSha256'),
                ('.json', 'previousMetadataSha256', 'currentMetadataSha256')]:
            before = evidence.digest(PREVIOUS / 'catalogs' / (row['path'] + suffix))
            after = evidence.digest(directory / 'catalogs' / (row['path'] + suffix))
            assert row[before_key] == before == after == row[after_key]
        assert row['pixelsIdentical'] is True and row['metadataIdentical'] is True
    strict = json.loads((directory / 'package/strict-images.json').read_text())
    assert len(strict) == 201
    for row in strict.values():
        assert row['identical'] is True
        assert row['sha256'] == evidence.digest(directory / 'captures' / row['identicalCapture'])
    producer = json.loads((directory / 'qt/inputs.json').read_text())['sourceFiles']
    assert not any('__pycache__' in Path(name).parts or name.endswith('.pyc') for name in producer)
    for path in (directory / 'captures').glob('*.log'):
        assert 'QPainter::begin:' not in path.read_text(), path.name
    profiles = sorted((directory / 'runtime').glob('media-library-*.json'))
    assert len(profiles) == 8
    restored_pairs = []
    for path in profiles:
        value = json.loads(path.read_text())
        assert value['structuralChecks'] == 'passed' and value['retainedRestoreRasterStatus'] == 'passed'
        assert value['retainedRestorePixelMatches'] == 6 and value['physicalDisplay'] is False and value['hardwareAcceleration'] is False
        assert len(value['histories']) == 6
        for history in value['histories']:
            assert history['steps'][13]['step'] == 'restore' and history['steps'][13]['matchesInitialPixels'] is True
            stem = 'runtime/' + path.stem + '-' + history['configuration']['id'] + '-history-step'
            restored_pairs.append((stem + '0.png', stem + '13.png'))
    required = {name for pair in restored_pairs for name in pair}
    restored_images = {}
    for key, record in report['archives'].items():
        if not key.startswith('runtime-images-'):
            continue
        with tarfile.open(directory / record['archive']) as stream:
            for member in stream.getmembers():
                if member.name in required:
                    with Image.open(io.BytesIO(stream.extractfile(member).read())) as bitmap:
                        restored_images[member.name] = (bitmap.size, bitmap.convert('RGBA').tobytes())
    assert set(restored_images) == required and len(restored_pairs) == 48
    assert all(restored_images[first] == restored_images[last] for first, last in restored_pairs)
    before = (directory / 'attempts/media-library-reflow-regression-v1/run.log').read_text()
    assert '11 passed, 4 failed' in before and before.count('FAIL!') == 4
    for name in ['qt/run.log', 'qt/full/run.log']:
        assert '15 passed, 0 failed' in (directory / name).read_text()
    if 'hostCommands' in report['validation']:
        host = json.loads((directory / 'host/result.json').read_text())
        commands = json.loads((directory / 'host/results.json').read_text())
        assert host['exitCode'] == 0 and host['commands'] == len(commands) == report['validation']['hostCommands']
        assert host['contractTests'] == report['validation']['hostContractTests']
        assert all(row['exitCode'] == 0 for row in commands)
        initial = directory / report['validation']['hostCandidateInput']
        frozen_inputs = json.loads((directory / 'host/inputs.json').read_text())
        assert frozen_inputs[str(directory.relative_to(ROOT) / 'candidate.json')] == evidence.digest(initial)
        assert report['validation']['cleanLinuxEvidenceReplay'] is True
        assert json.loads((directory / 'host/clean-linux/result.json').read_text())['exitCode'] == 0
        assert 'Ran 51 tests' in (directory / 'host/clean-linux/run.log').read_text()
    print('Corrected media: 1008 exact pairs, all 1608 native lifecycles, no previous passing observation regressed; sizing and complete mirror acceptance pending')
    return report

if __name__ == '__main__':
    verify()
