#!/usr/bin/env python3
"""Preserve native HeroCarousel observations for an independent Linux consumer."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/hero-carousel-20261018'
HISTORY = ROOT / 'evidence/reference-investigations/hero-carousel-history-20261018'
OUTPUT = ROOT / 'tests/consumer/native-hero-carousel-witnesses.json'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'


def projected():
    read = lambda path: json.loads(path.read_text())
    closed = []
    for row in read(SOURCE / 'output/captures.json')['rows']:
        assert row['publicProbedIdentical'] and row['publicLiteralIdentical']
        public, probe = row['states'][:2]
        closed.append(dict(configuration=row['configuration'], appearance=row['appearance'],
            textScale=row['textScale'], dpr=row['dpr'],
            frame=dict(carousel=probe['carouselFrame'], caller=probe['callerFrame'], slides=probe['slideFrames']),
            lifecycle=public['lifecycle'], sourceImage=str((SOURCE / 'output' / row['paths'][0]).relative_to(ROOT))))
    histories = []
    for row in read(HISTORY / 'attempt3/output/histories.json')['histories']:
        steps = []
        for step in row['steps']:
            assert step['publicProbedIdentical'] and step['publicLiteralIdentical']
            public, probe = step['states'][:2]
            # SwiftUI's geometry preference retains stale frames for hidden and
            # removed slides. Preserve those bytes and identify this projection.
            active = {key: value for key, value in probe['slideFrames'].items()
                if public['lifecycle']['activeSlideStates'].get(key)}
            steps.append(dict(step=step['step'], configuration=step['configuration'],
                frame=dict(carousel=probe['carouselFrame'], slides=active),
                rawCachedSlideFrames=probe['slideFrames'], callerFrameStatus='unobserved in history helper',
                lifecycle=public['lifecycle'],
                sourceImage=str((HISTORY / 'attempt3/output' / step['paths'][0]).relative_to(ROOT))))
        histories.append(dict(fitHeight=row['fitHeight'], appearance='light', textScale=1, dpr=1, steps=steps))
    assert len(closed) == 160 and len(histories) == 2 and all(len(row['steps']) == 16 for row in histories)
    return dict(reference=REFERENCE, accepted=False, closed=closed, histories=histories,
        limitValueObservation=read(HISTORY / 'limit-value/result.json'),
        sizing=read(SOURCE / 'sizing-output/sizing.json')['rows'],
        scope='Native observations only; history frame comparison covers active slides, preserves raw cached frames, and does not close complete native geometry or lazy timing')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    value = json.dumps(projected(), indent=2) + '\n'
    if arguments.check:
        assert OUTPUT.read_text() == value, 'Native HeroCarousel projection changed'
    else:
        OUTPUT.write_text(value)
    print('HeroCarousel witnesses: 160 closed, 32 history and 160 sizing contexts; acceptance pending')
