#!/usr/bin/env python3
"""Compare every HeroCarousel observation and full image without tolerance."""
import argparse
from functools import reduce
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
PROJECTION = ROOT / 'tests/consumer/native-hero-carousel-witnesses.json'


def corpus():
    native = json.loads(PROJECTION.read_text())
    for row in native['closed']:
        context = f"{row['appearance']}-text{row['textScale']:g}-dpr{row['dpr']:g}"
        yield dict(row, kind='closed', context=context, name=row['configuration']['id'])
    for history in native['histories']:
        for row in history['steps']:
            yield dict(row, kind='history', fitHeight=history['fitHeight'], context='light-text1-dpr1',
                name=('fit-' if history['fitHeight'] else 'bounded-') + row['step'])


def compare(candidate, output):
    assert not output.exists(), 'Refusing to overwrite a comparison'
    reports = {}
    results = []
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    for row in corpus():
        context = row['context']
        if context not in reports:
            reports[context] = json.loads((candidate / (context + '.json')).read_text())
        report = reports[context]
        assert report['accepted'] is False and report['structuralChecks'] == 'passed'
        if row['kind'] == 'closed':
            matches = [entry for entry in report['closed'] if entry['configuration'] == row['configuration']]
        else:
            history, = [entry for entry in report['histories'] if entry['fitHeight'] == row['fitHeight']]
            matches = [entry for entry in history['steps'] if entry['step'] == row['step']]
        actual, = matches
        native_frame = row['frame']
        native_life = row['lifecycle']
        assert actual['nativeActiveFrame'] == native_frame and actual['nativeLifecycle'] == native_life
        frames = actual['actualActiveFrame'] == native_frame
        lifecycle = actual['lifecycle'] == native_life
        assert actual['activeFrameMatches'] is frames and actual['lifecycleMatches'] is lifecycle
        reference = ROOT / row['sourceImage']
        image = candidate / (context + '-' + row['name'] + '.png')
        with Image.open(reference) as expected, Image.open(image) as observed:
            assert expected.size == observed.size, (image, expected.size, observed.size)
            difference = ImageChops.difference(expected.convert('RGBA'), observed.convert('RGBA'))
            maximum = reduce(ImageChops.lighter, difference.split())
            histogram = maximum.histogram()
            changed = expected.width * expected.height - histogram[0]
            delta = max(index for index, count in enumerate(histogram) if count)
        results.append(dict(kind=row['kind'], image=image.name, reference=row['sourceImage'],
            candidateSha256=digest(image), referenceSha256=digest(reference),
            pixelsMatch=changed == 0, differentPixels=changed, maximumChannelDifference=delta,
            activeFramesMatch=frames, lifecycleMatches=lifecycle,
            observedSubsetMatches=changed == 0 and frames and lifecycle,
            completeGeometryAcceptance='pending' if row['kind'] == 'history' else 'pending broader contexts'))
    assert len(results) == 192 and len(reports) == 8
    summary = dict(cases=len(results), pixelsMatch=sum(row['pixelsMatch'] for row in results),
        activeFramesMatch=sum(row['activeFramesMatch'] for row in results),
        lifecycleMatches=sum(row['lifecycleMatches'] for row in results),
        observedSubsetMatches=sum(row['observedSubsetMatches'] for row in results))
    value = dict(reference=json.loads(PROJECTION.read_text())['reference'], accepted=False,
        projectionSha256=digest(PROJECTION), tolerance='none', approvedExceptions=[],
        expectedImagesChanged=False, summary=summary, results=results,
        acceptance='pending; history frames are an active projection; complete geometry, sizing, lazy timing, gestures, readers, physical input and independent replay remain unproven')
    output.write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raise SystemExit(compare(args.candidate, args.output))
