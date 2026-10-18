#!/usr/bin/env python3
"""Recompute the frozen HeroCarousel diagnostics without accepting parity."""
import gzip
import hashlib
import io
import json
from pathlib import Path
from functools import reduce
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/hero-carousel-20261018'
CHUNK = 8 * 1024 * 1024


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    digest = lambda raw: hashlib.sha256(raw).hexdigest()
    report = read('validation.json')
    assert report['accepted'] is report['physicalInput'] is report['physicalDisplay'] is False
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['desktopCandidateCoverage'] == [76, 80] and report['acceptedDesktopEntries'] == 0
    assert report['sourceAttempts'] == list(range(1, 8)) and report['producer'] == 'hero-carousel-qt-v7'
    assert report['focusedQtTargets'] == 5 and report['finalFullQtSuiteRerun'] is False
    assert report['packageContexts'] == report['galleryContexts'] == report['displayProfiles'] == 8
    assert report['expectedImagesChanged'] is False and report['tolerance'] == 'none' and report['approvedExceptions'] == []
    for key in ['nativeDirectSizing', 'nativeLazyTiming', 'nativeGestureTiming', 'nativeSystemFontMetrics', 'readerAcceptance', 'independentMachine']:
        assert report[key] == 'pending'
    files = read('files.json')
    assert set(files) == {str(path.relative_to(DIRECTORY)) for path in DIRECTORY.rglob('*')
        if path.is_file() and path.name != 'files.json'}
    for name, row in files.items():
        raw = (DIRECTORY / name).read_bytes()
        assert len(raw) == row['bytes'] and digest(raw) == row['sha256'], name
    sources, runtime, records = map(read, ['source-specs.json', 'runtime-spec.json', 'records-spec.json'])
    chunks = {}

    def raw_record(row):
        values = []
        for part in row['chunks']:
            checksum = part['sha256']
            assert len(checksum) == 64 and all(char in '0123456789abcdef' for char in checksum)
            assert 0 < part['bytes'] <= CHUNK
            if checksum not in chunks:
                with gzip.GzipFile(fileobj=io.BytesIO((DIRECTORY / 'blobs' / (checksum + '.gz')).read_bytes())) as stream:
                    chunks[checksum] = stream.read(CHUNK + 1)
            value = chunks[checksum]
            assert len(value) == part['bytes'] and digest(value) == checksum
            values.append(value)
        value = b''.join(values)
        assert len(value) == row['bytes'] and digest(value) == row['sha256']
        return value

    def record(name):
        return json.loads(raw_record(records[name]))

    assert set(sources) == {f'hero-carousel-qt-v{number}' for number in range(1, 8)}
    for table in [*(value['files'] for value in sources.values()), runtime, records]:
        for name, row in table.items():
            assert not Path(name).is_absolute() and '..' not in Path(name).parts
            raw_record(row)
    assert set(chunks) == {path.stem for path in (DIRECTORY / 'blobs').glob('*.gz')}
    for name, source in sources.items():
        assert len(source['files']) == report['sourceCounts'][name]
        assert record('producers/' + name + '/inputs.json')['files'] == {key: row['sha256'] for key, row in source['files'].items()}
        result = record('producers/' + name + '/result.json')
        if name == 'hero-carousel-qt-v5':
            assert result['exitCode'] == 8 and result['failedStep'] == 'hero-tests'
            assert b'QWindow::devicePixelRatio()' in raw_record(records['producers/' + name + '/hero-tests.log'])
        else:
            assert result['exitCode'] == 0
    final = sources[report['producer']]['files']
    assert len(final) == 584
    verbose = raw_record(records['producers/hero-carousel-qt-v7/ctest-verbose.log']).decode()
    for test in ['allocationOriginTracksFractionalScenePlacement', 'identitiesSurviveEditsReorderAndEmptyRestore',
            'publicRightToLeftKeepsLogicalOrderAndTargets', 'publicPointerReleaseSettlesOnAViewBoundary',
            'ownerRemovalDuringActivityCallback', 'ownerRemovalDuringDataCallback']:
        assert verbose.count('PASS   : HeroCarouselTests::' + test + '()') == 2, test
    package = record('package/result.json')
    assert package['exitCode'] == 0 and package['contexts'] == package['galleryContexts'] == 8
    assert package['freshConsumerBuild'] is package['libraryAndConsumerProjectSourcesAbsentAtRuntime'] is True
    inputs = record('package/inputs.json')
    assert inputs['producer'] == report['producer']
    assert inputs['packageFiles'] == {name.removeprefix('install/'): row['sha256'] for name, row in runtime.items() if name.startswith('install/')}
    assert inputs['consumerSha256'] == runtime['consumer-build/InstalledConsumer']['sha256']
    assert inputs['consumerFiles'] == {name.removeprefix('tests/consumer/'): row['sha256'] for name, row in final.items() if name.startswith('tests/consumer/')}
    native = json.loads(raw_record(final['tests/consumer/native-hero-carousel-witnesses.json']))
    comparisons = {row['image']: row for row in record('package/comparison.json')['results']}
    observations = []
    for row in native['closed']:
        context = f"{row['appearance']}-text{row['textScale']:g}-dpr{row['dpr']:g}"
        actual, = [value for value in read('captures/' + context + '.json')['closed'] if value['configuration'] == row['configuration']]
        observations.append((row, actual, context + '-' + row['configuration']['id'] + '.png'))
    for history in native['histories']:
        group, = [value for value in read('captures/light-text1-dpr1.json')['histories'] if value['fitHeight'] == history['fitHeight']]
        for row in history['steps']:
            actual, = [value for value in group['steps'] if value['step'] == row['step']]
            assert actual['configuration'] == dict(row['configuration'], fitHeight=history['fitHeight'])
            assert actual['nativeRawCachedSlideFrames'] == row['rawCachedSlideFrames']
            observations.append((row, actual, 'light-text1-dpr1-' + ('fit-' if history['fitHeight'] else 'bounded-') + row['step'] + '.png'))
    assert len(observations) == len(comparisons) == 192
    totals = dict(cases=192, pixelsMatch=0, activeFramesMatch=0, lifecycleMatches=0, observedSubsetMatches=0)
    for row, actual, name in observations:
        expected = comparisons[name]
        reference, candidate = ROOT / row['sourceImage'], DIRECTORY / 'captures' / name
        assert expected['reference'] == row['sourceImage']
        assert digest(reference.read_bytes()) == expected['referenceSha256']
        assert digest(candidate.read_bytes()) == expected['candidateSha256']
        assert actual['nativeActiveFrame'] == row['frame'] and actual['nativeLifecycle'] == row['lifecycle']
        frame = actual['actualActiveFrame'] == row['frame']
        lifecycle = actual['lifecycle'] == row['lifecycle']
        assert frame is actual['activeFrameMatches'] is expected['activeFramesMatch']
        assert lifecycle is actual['lifecycleMatches'] is expected['lifecycleMatches']
        with Image.open(reference) as first, Image.open(candidate) as second:
            assert first.size == second.size
            difference = reduce(ImageChops.lighter, ImageChops.difference(first.convert('RGBA'), second.convert('RGBA')).split())
            histogram = difference.histogram()
            changed = first.width * first.height - histogram[0]
            maximum = max(index for index, count in enumerate(histogram) if count)
        pixels = changed == 0
        assert expected['differentPixels'] == changed and expected['maximumChannelDifference'] == maximum
        assert pixels is expected['pixelsMatch']
        subset = pixels and frame and lifecycle
        assert subset is expected['observedSubsetMatches']
        for key, value in [('pixelsMatch', pixels), ('activeFramesMatch', frame), ('lifecycleMatches', lifecycle), ('observedSubsetMatches', subset)]:
            totals[key] += value
    assert totals == report['strictComparison'] == dict(cases=192, pixelsMatch=108, activeFramesMatch=184, lifecycleMatches=168, observedSubsetMatches=84)
    assert record('package/comparison-result.json')['exitCode'] == record('strict-default/result.json')['exitCode'] == 1
    stability = record('package/closed-stability.json')['files']
    assert len(stability) == 200
    for name, checksum in stability.items():
        current = (DIRECTORY / 'captures' / name).read_bytes()
        assert digest(current) == checksum and current == (DIRECTORY / 'aligned-captures' / name).read_bytes()
    galleries = sorted((DIRECTORY / 'captures').glob('gallery-*.json'))
    assert len(galleries) == 8
    for path in galleries:
        value = json.loads(path.read_text())
        assert value['accepted'] is False and value['structuralChecks'] == 'passed'
        assert len(value['operatorClicks']) == 17 and len(value['states']) == 21 and value['tabKeyEvents'] == 25
        assert value['callerSpaceActivation'] is value['arrowKeysDoNotNavigate'] is value['disabledPointerAndTab'] is True
        assert value['nativeInputTimingAcceptance'] == value['readerAcceptance'] == value['physicalInputAcceptance'] == 'pending'
        assert len(list(path.parent.glob(path.stem + '-*.png'))) == 21
    assert record('catalog/result.json')['catalogMatchesInstalledConsumerInitialGallery'] is True
    assert (DIRECTORY / 'catalog/gallery.png').read_bytes() == (DIRECTORY / 'captures/gallery-light-text1-dpr1-initial.png').read_bytes()
    profiles = [path for path in (DIRECTORY / 'display/output').glob('*.json') if path.name != 'environment.json']
    assert len(profiles) == 8 and record('display/result.json')['exitCode'] == 0
    assert record('display/inputs.json')['consumerSha256'] == inputs['consumerSha256']
    for path in profiles:
        value = json.loads(path.read_text())
        assert value['accepted'] is False and value['structuralChecks'] == 'passed'
        session = value['displaySession']
        assert session['physicalInput'] is session['physicalDisplay'] is session['hardwareAcceleration'] is False
        assert digest((path.parent / session['sessionCapture']).read_bytes()) == session['sessionCaptureSha256']
        assert digest((path.parent / session['finalWindowCapture']).read_bytes()) == session['finalWindowCaptureSha256']
    replay = read('portable/result.json')
    assert replay['accepted'] is False and replay['exitCode'] == 0 and replay['contexts'] == replay['galleryContexts'] == 8
    assert replay['projectSourcesAbsent'] is True and replay['exactOutputFiles'] == 376
    for name, checksum in replay['files'].items():
        assert digest((DIRECTORY / 'captures' / name).read_bytes()) == checksum
    ci = read('ci/result.json')
    assert ci['accepted'] is False and ci['exitCode'] == 0 and ci['projectSourcesAbsent'] is True
    assert ci['installedGalleryFiles'] == 22 and ci['catalogContexts'] == 4
    assert all(command['exitCode'] == 0 for command in read('ci/commands.json'))
    assert read('ci-preflight/result.json')['failedStep'] == 'fragment-preflight'
    for name, checksum in read('ci/inputs.json').items():
        assert digest((DIRECTORY / 'ci' / Path(name).name).read_bytes()) == checksum
    for path in (DIRECTORY / 'ci/installed-gallery').iterdir():
        name = path.name.replace('gallery', 'gallery-light-text1-dpr1', 1)
        assert path.read_bytes() == (DIRECTORY / 'captures' / name).read_bytes()
    for appearance in ['light', 'dark']:
        for dpr in [1, 2]:
            actual = DIRECTORY / f'ci/catalog-{appearance}-dpr{dpr}.png'
            expected = DIRECTORY / f'captures/gallery-{appearance}-text1-dpr{dpr}-initial.png'
            assert actual.read_bytes() == expected.read_bytes()
    print('HeroCarousel candidate: seven frozen sources, 192 strict observations, eight galleries/display profiles and exact portable replay; acceptance pending')


if __name__ == '__main__':
    verify()
