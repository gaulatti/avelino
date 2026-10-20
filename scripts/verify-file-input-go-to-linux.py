#!/usr/bin/env python3
"""Audit scoped Linux GoTo evidence without granting native mirror acceptance."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/file-input-go-to-20261018'


def metadata_section(raw, name):
    text = raw.decode()
    match = re.search(r'"' + re.escape(name) + r'"\s*:\s*', text)
    assert match
    _, length = json.JSONDecoder().raw_decode(text[match.end():])
    return text[match.end():match.end() + length].encode()


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    report = read('validation.json')
    assert report['accepted'] is report['physicalDisplay'] is report['physicalInput'] is report['physicalListening'] is False
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['baseGit'] == '78708f69205379cc858f596a913bb32063c16b9e'
    assert report['desktopCandidateCoverage'] == [75, 80] and report['acceptedDesktopEntries'] == 0
    assert report['expectedImagesChanged'] is False and report['approvedExceptions'] == [] and report['tolerance'] == 'none'
    assert report['finalFullQtSuiteRerun'] is False and report['focusedQtTargets'] == 8
    assert report['independentConsumerBuild'] is report['libraryAndConsumerSourcesAbsentAtRuntime'] is True
    assert all(status == 'pending' for status in report['gates'].values())
    assert report['gates']['goToAtSpiOrcaFlow'] == 'pending'
    assert report['toolchain'] == 'sha256:2fdc6216ef3446ebd904a1999d3e0c909c7b667e844149ad2830d68d069e77f8'
    files = read('files.json')
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name != 'files.json'}
    for name, row in files.items():
        raw = (DIRECTORY / name).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
    module_spec = importlib.util.spec_from_file_location('avelino_go_to_restore', DIRECTORY / 'tools/reconstruct.py')
    sys.dont_write_bytecode = True
    loader = importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(loader)
    sources, runtime = read('source-specs.json'), read('runtime-spec.json')
    used = set()
    for specification in [row['files'] for row in sources.values()] + [runtime]:
        for name, row in specification.items():
            digest, size = hashlib.sha256(), 0
            for part in row['chunks']:
                used.add(part['sha256']);raw = loader.chunk_bytes(part);digest.update(raw);size += len(raw)
            assert size == row['bytes'] and digest.hexdigest() == row['sha256'], name
    assert used == {path.stem for path in (DIRECTORY / 'blobs').glob('*.gz')}
    assert set(sources) == {f'file-input-qt-v{i}' for i in range(55, 61)}
    for number in range(55, 61):
        name = f'file-input-qt-v{number}'
        input_record = read('attempts/' + name + '/inputs.json')
        spec = sources[name]['files']
        assert {path: row['sha256'] for path, row in spec.items()} == input_record['files']
        terminal = read('attempts/' + name + '/result.json')
        assert terminal['exitCode'] == (8 if number in [55, 56, 58] else 0)
        if terminal['exitCode']:
            assert terminal['failedStep'] == 'ui-tests'
    assert report['finalSource'] == 'file-input-qt-v60' and len(sources[report['finalSource']]['files']) == report['sourceFiles'] == 567
    commands = read('attempts/file-input-qt-v60/commands.json')
    assert [row['name'] for row in commands] == ['configure', 'foundation-build', 'foundation-tests', 'backend-build', 'backend-tests', 'ui-build', 'ui-tests', 'install']
    assert all(row['exitCode'] == 0 for row in commands)
    for name, count in [('foundation-tests', 2), ('backend-tests', 4), ('ui-tests', 2)]:
        text = (DIRECTORY / 'attempts/file-input-qt-v60' / (name + '.log')).read_text()
        assert f'100% tests passed, 0 tests failed out of {count}' in text
    assert 'hasActiveFocus()' in (DIRECTORY / 'attempts/file-input-qt-v56/ui-tests.log').read_text()
    assert 'nested GoTo window must remain reachable' in (DIRECTORY / 'attempts/file-input-qt-v58/ui-tests.log').read_text()
    package = read('package/inputs.json')
    assert package['producer'] == report['finalSource'] and package['freshConsumerBuild'] is True and package['imageId'] == report['toolchain']
    assert {path.removeprefix('tests/consumer/'): row['sha256'] for path, row in sources[report['finalSource']]['files'].items()
            if path.startswith('tests/consumer/')} == package['consumerFiles']
    assert set(runtime) == {'install/' + name for name in package['packageFiles']} | {'consumer-build/InstalledConsumer'}
    assert {name.removeprefix('install/'): row['sha256'] for name, row in runtime.items() if name.startswith('install/')} == package['packageFiles']
    assert runtime['consumer-build/InstalledConsumer']['sha256'] == package['consumerSha256']
    assert read('package/result.json')['exitCode'] == read('display/result.json')['exitCode'] == 0
    assert read('package/result.json')['contexts'] == report['packageContexts'] == 8
    stable = read('closed-stability.json')
    assert len(stable) == 8 and sum(len(row['images']) for row in stable.values()) == report['closedImagesUnchanged'] == 256
    for name, row in stable.items():
        path, prior = DIRECTORY / 'captures' / name, ROOT / row['prior']
        record = json.loads(path.read_text())
        assert row['completeClosedAndSizingMetadataUnchanged'] is True
        for section in ['closed', 'sizing']:
            assert metadata_section(path.read_bytes(), section) == metadata_section(prior.read_bytes(), section)
        assert record['accepted'] is False and record['structuralChecks'] == 'passed'
        assert len(record['actions']) == report['consumerActionsPerContext'] == 30
        assert record['images'] == len(list((DIRECTORY / 'captures').glob(path.stem + '-*.png'))) == report['consumerImagesPerContext'] == 49
        assert record['pointerEvents'] == report['pointerEventsPerContext'] == 62 and record['keyEvents'] == report['keyEventsPerContext'] == 164
        phases = {action['phase'] for action in record['actions']}
        assert {'go-to-invalid-cancel-keeps-selection', 'go-to-suggestion-navigation', 'go-to-empty-input-recent-navigation',
                'go-to-nonmatching-file-selected', 'go-to-file-owner-result', 'go-to-remount-and-cancel'} <= phases
        assert record['goToRankingAcceptance'] == record['goToRelativeResolutionAcceptance'] == record['goToHistoryCapacityAcceptance'] == 'pending'
        for image, digest in row['images'].items():
            raw = (DIRECTORY / 'captures' / image).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == digest and raw == (prior.parent / image).read_bytes()
    profiles = list((DIRECTORY / 'display/output').glob('file-input-*.json'))
    assert len(profiles) == report['displayProfiles'] == 8
    for path in profiles:
        record = json.loads(path.read_text())
        assert record['structuralChecks'] == 'passed' and record['accepted'] is False
        assert record['images'] == 49 and len(record['actions']) == 30 and record['pointerEvents'] == 62 and record['keyEvents'] == 164
    portable = read('portable/result.json')
    assert portable['exitCode'] == 0 and portable['libraryAndConsumerSourcesAbsentAtRuntime'] is True
    restored = read('portable/light-text1-dpr1.json')
    original = (DIRECTORY / 'captures/light-text1-dpr1.json').read_bytes()
    for section in ['closed', 'sizing']:
        assert metadata_section((DIRECTORY / 'portable/light-text1-dpr1.json').read_bytes(), section) == metadata_section(original, section)
    assert len(restored['actions']) == 30 and restored['images'] == 49
    for row in restored['closed']:
        name = 'light-text1-dpr1-' + row['configuration']['id'] + '.png'
        assert (DIRECTORY / 'portable' / name).read_bytes() == (DIRECTORY / 'captures' / name).read_bytes()
    print('FileInput Linux GoTo: 8 Qt targets, fresh source-free consumer in 8 contexts, 8 virtual display profiles, exact portable replay and 256 unchanged closed PNGs; native/reader/physical gates pending')


if __name__ == '__main__':
    verify()
