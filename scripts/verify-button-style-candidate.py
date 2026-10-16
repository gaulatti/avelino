#!/usr/bin/env python3
"""Audit the preserved ButtonStyle candidate without granting mirror acceptance."""
import hashlib
import importlib.util
import itertools
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'evidence/development/button-style'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(base, name):
    return json.loads((base / name).read_text())


def verify(base=BASE):
    report = read(base, 'candidate.json')
    assert report['status'] == 'verification-pending' and report['accepted'] is False
    assert report['referenceRevision'] == REFERENCE
    files = report['files']
    actual = {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
    assert actual == set(files) | {'candidate.json'}, 'Missing or unsealed candidate file'
    for name, checksum in files.items():
        assert digest(base / name) == checksum, f'Changed candidate bytes: {name}'
    previous = read(base, 'diagnostics/pre-paint-v1.json')
    archive = base / 'diagnostics' / previous['archive']
    assert digest(archive) == previous['sha256'] and previous['accepted'] is False
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        assert len(members) == previous['memberCount'] == len(previous['files'])
        assert {m.name for m in members} == set(previous['files'])
        for member in members:
            assert member.isfile()
            assert hashlib.sha256(tar.extractfile(member).read()).hexdigest() == previous['files'][member.name]
        acknowledgment = json.load(tar.extractfile('diagnostics/capture-acknowledgment.json'))
        assert acknowledgment['preservedAttempt']
    regression = read(base, 'diagnostics/paint-regression-v3/result.json')
    assert regression['exitCodes'] == {'baseline': 255, 'fixed': 0} and regression['sameCompiledConsumer']
    binaries = read(base, 'diagnostics/paint-regression-v3/compiled-consumer-hashes.json')
    assert len(binaries) == 2 and binaries['baseline'] == binaries['fixed']

    source = read(ROOT, 'evidence/reference-investigations/button-style-20261016/captures/captures.json')
    investigation = read(ROOT, report['sourceInvestigation'])
    captures = read(base, 'captures/capture-results.json')
    rows = source['captures']
    names = {r['paths'][0] for r in rows}
    assert len(names) == len(rows) == captures['cases'] == len(captures['records']) == 704
    assert captures['fixtures'] == 88 and captures['reference'] == REFERENCE and captures['accepted'] is False
    assert captures['sourceInvestigationSha256'] == digest(ROOT / report['sourceInvestigation'])
    assert {r['path'] for r in captures['records']} == names
    for row in captures['records']:
        assert row['sha256'] == digest(base / 'captures' / row['path'])
        assert row['metadataSha256'] == digest(base / 'captures' / (row['path'] + '.json'))
    installed = read(base, 'installed-files.json')
    assert installed['fileCount'] == len(installed['files']) == 121
    assert installed['files']['bin/AvelinoCatalog'] == captures['catalogSha256']

    spec = importlib.util.spec_from_file_location('button_style_candidate_comparison', ROOT / 'scripts/compare-button-style-captures.py')
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    comparison = read(base, 'comparison/comparison.json')
    results = comparison['results']
    assert len(results) == 704 and {r['fixture'] for r in results} == names
    by_name = {r['paths'][0]: r for r in rows}
    for result in results:
        name = result['fixture']
        assert result['referenceRevision'] == REFERENCE
        assert result['referenceSHA256'] == investigation['files']['captures/' + name]
        assert result['candidateSHA256'] == digest(base / 'captures' / name)
        observation = adapter.observations(by_name[name], read(base / 'captures', name + '.json'))
        for key, value in observation.items():
            assert result[key] == value, f'Changed measured outcome: {name} {key}'
        if result['status'] == 'passed':
            assert result['changedPixels'] == 0 and result['maximumChannelError'] == 0
            assert result['differenceBounds'] is None and result['alphaDifferenceBounds'] is None
            assert result['partFramesStatus'] == result['stateStatus'] == 'passed'
    summary = dict(cases=704, exactPixelAndGeometryMatches=sum(r['status'] == 'passed' for r in results),
                   partFrameMatches=sum(r['partFramesStatus'] == 'passed' for r in results),
                   stateMatches=sum(r['stateStatus'] == 'passed' for r in results))
    assert summary == comparison['summary'] == report['strictComparison']
    assert comparison['accepted'] is False
    assert comparison['status'] == ('passed' if summary['exactPixelAndGeometryMatches'] == 704 else 'failed')

    expected = set(itertools.product(['xcb', 'wayland'], ['software', 'opengl'], ['standard', 'scaled']))
    observed = set()
    for path in (base / 'sessions').glob('button-style-*.json'):
        row = json.loads(path.read_text())
        _, _, protocol, backend, configuration = path.stem.split('-')
        observed.add((protocol, backend, configuration))
        assert path.with_suffix('.captured').is_file()
        assert row['platform'] == protocol and row['graphicsApi'] == (1 if backend == 'software' else 3)
        assert row['dpr'] == (1 if configuration == 'standard' else 2)
        assert row['textScale'] == (1 if configuration == 'standard' else 1.5)
        assert row['appearance'] == ('light' if configuration == 'standard' else 'dark')
        assert row['fixture'] == 'button-style' and row['accepted'] is False
        assert row['closedContextCount'] == len(row['closedContexts']) == 88 and row['exactFrameSets'] == 85
        assert row['pointerPhases'] == 13 and len(row['nativeTraces']) == 2 and row['sharedHeldPixelsIdentical']
        for key in ['buttonStyleChecks', 'callerStateChecks', 'focusChecks', 'qtAccessibilityChecks', 'liveCurvePaintChecks']:
            assert row[key] == 'passed'
        assert row['physicalDisplay'] is False and row['hardwareAcceleration'] is False
        assert digest(path.with_suffix('.png')) == row['windowCaptureSha256']
        assert digest(path.parent / row['sessionCapture']) == row['sessionCaptureSha256']
    assert observed == expected, 'Incomplete virtual display matrix'
    runtime = read(base, 'runtime-validation.json')
    assert runtime['displayRunExitCode'] == 0
    assert read(base, 'runtime-inputs.json')['consumerSha256'] == runtime['compiledConsumerSha256']
    assert '100% tests passed, 0 tests failed out of 23' in (base / 'logs/full-ctest.log').read_text()
    assert 'Installed catalog: 119 fixture captures passed' in (base / 'logs/package-all-consumers-catalog.log').read_text()
    old = ROOT / 'evidence/development/tooltip/catalog'
    for path in old.glob('*.png'):
        assert path.read_bytes() == (base / 'catalog' / path.name).read_bytes()
        assert path.with_suffix('.png.json').read_bytes() == (base / 'catalog' / (path.name + '.json')).read_bytes()
    assert len(list((base / 'catalog').glob('*.png'))) == 119
    print(f'ButtonStyle candidate: {len(files)} sealed files, 704 captures, eight virtual profiles; acceptance pending')
    return report


if __name__ == '__main__':
    verify()
