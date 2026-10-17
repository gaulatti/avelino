#!/usr/bin/env python3
"""Compare every closed FileInput RGBA pixel and complete body/caller frame."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'


def different_pixels(left, right):
    assert left.size == right.size
    left, right = left.convert('RGBA'), right.convert('RGBA')
    bands = ImageChops.difference(left, right).split()
    changed = bands[0].point(lambda value: 255 if value else 0)
    for band in bands[1:]:
        changed = ImageChops.lighter(changed, band.point(lambda value: 255 if value else 0))
    result = changed.histogram()[255]
    assert (result == 0) == (left.tobytes() == right.tobytes())
    return result


def compare(directory, output):
    projection = json.loads((ROOT / 'tests/consumer/native-file-input-witnesses.json').read_text())
    oracle = {(r['configuration']['id'], r['appearance'], r['textScale'], r['dpr']): r for r in projection['closed']}
    reports = sorted(directory.glob('*.json'))
    contexts, seen, rows = set(), set(), []
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    for path in reports:
        report = json.loads(path.read_text())
        context = report['appearance'], report['textScale'], report['dpr']
        assert context not in contexts and report['accepted'] is False and report['reference'] == REFERENCE
        contexts.add(context)
        assert report['nativeContractStatesMatch'] == len(report['closed']) == len(report['sizing']) == 32
        for row in report['closed']:
            key = row['configuration']['id'], *context
            assert key not in seen
            seen.add(key)
            native = oracle[key]
            assert row['configuration'] == native['configuration']
            assert row['nativeFrames'] == native['frames'] and row['nativeState'] == native['nativeState']
            assert row['reference'] == native['reference'] and row['linuxContentTypes'] == native['linuxContentTypes']
            expected = ROOT / native['reference']
            candidate = directory / (path.stem + '-' + key[0] + '.png')
            left, right = Image.open(expected).convert('RGBA'), Image.open(candidate).convert('RGBA')
            assert left.size == right.size == (600 * context[2], 300 * context[2])
            # Combine changes from all four channels; no pixels are excluded.
            different = different_pixels(left, right)
            frames = row['frames'] == native['frames']
            assert row['nativeCompleteFramesMatch'] is frames
            state = row['state']
            configuration = row['configuration']
            contract = state['mounted'] is True and state['pickerVisible'] is False and state['results'] == []
            contract = contract and state['title'] == configuration.get('title', 'Choose file…')
            contract = contract and state['enabled'] is (not configuration['disabled']) and state['sourceTypes'] == configuration['types']
            assert contract and row['nativeContractStateMatch'] is True
            rows.append(dict(configuration=configuration, appearance=context[0], textScale=context[1], dpr=context[2],
                native=str(expected.relative_to(ROOT)), nativeSha256=sha(expected), candidate=candidate.name,
                candidateSha256=sha(candidate), differentPixels=different, exactPixels=different == 0,
                nativeFrames=native['frames'], candidateFrames=row['frames'], completeFramesMatch=frames, contractStateMatch=contract))
    assert contexts == set(itertools.product(['light', 'dark'], [1, 1.5], [1, 2]))
    assert seen == set(oracle) and len(rows) == 256
    result = dict(reference=REFERENCE, accepted=False, expectedImagesChanged=False, tolerance='none', approvedExceptions=[],
        contexts=len(contexts), pairs=len(rows), exactPixels=sum(r['exactPixels'] for r in rows),
        completeFrames=sum(r['completeFramesMatch'] for r in rows), contractStates=sum(r['contractStateMatch'] for r in rows),
        directSizingAcceptance='pending', nativeTypeConformance='pending', nativeChooserPresentation='pending',
        nativeErrorResults='unobserved', physicalInputAcceptance='pending', readerAcceptance='pending', rows=rows)
    output.mkdir(parents=True)
    (output / 'observations.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(f"FileInput strict comparison: {result['exactPixels']}/256 pixels, {result['completeFrames']}/256 complete frames, {result['contractStates']}/256 contract states; acceptance pending")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output must be a fresh directory')
    compare(args.input, args.output)
