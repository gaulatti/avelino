#!/usr/bin/env python3
"""Compare native app-tab pixels, layout and binding state without tolerance."""
import argparse
import importlib.util
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('app_tab_capture', ROOT / 'scripts/capture-app-tabs.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


def compare(directory):
    directory = Path(directory)
    records = []
    totals = dict(cases=0, exactMatches=0, pixelMatches=0, nativeFrameMatches=0, stateMatches=0,
        retainedRestoreObservations=0, retainedRestorePixelMatches=0, sizingObservations=0,
        nativeSizingContexts=344, nativeSizingQueries=5160)
    for expected in capture.rows():
        path = expected['path']
        actual = json.loads((directory / (path + '.json')).read_text())
        observed = capture.observations(expected, actual)
        with Image.open(ROOT / expected['reference']) as source, Image.open(directory / path) as candidate:
            assert source.size == candidate.size == (640 * expected['dpr'], 400 * expected['dpr'])
            difference = ImageChops.difference(source.convert('RGBA'), candidate.convert('RGBA'))
            identical = all(bounds == (0, 0) for bounds in difference.getextrema())
        exact = identical and all(observed[key] == 'passed' for key in ['nativeFrameStatus', 'stateStatus', 'retainedRasterStatus'])
        records.append(dict(fixture=path, kind=expected['kind'], reference=expected['reference'],
            referenceSHA256=capture.digest(ROOT / expected['reference']), candidateSHA256=capture.digest(directory / path),
            status='passed' if exact else 'failed', pixelStatus='passed' if identical else 'failed', **observed))
        totals['cases'] += 1
        totals['exactMatches'] += exact
        totals['pixelMatches'] += identical
        totals['nativeFrameMatches'] += observed['nativeFrameStatus'] == 'passed'
        totals['stateMatches'] += observed['stateStatus'] == 'passed'
        if expected['kind'] == 'history' and expected['step'] == 'restore':
            totals['retainedRestoreObservations'] += 1
            totals['retainedRestorePixelMatches'] += observed['retainedRasterStatus'] == 'passed'
    return dict(reference=capture.REFERENCE, accepted=False, tolerance='none', approvedExceptions=[],
        expectedImagesChanged=False, status='failed', summary=totals, results=records,
        remainingAcceptance=['nativeGeometryRasterAndLabelFitting', 'nativeSizing', 'nativeGenericIdentity',
            'nativeKeyboardAndInputTiming', 'nativeAccessibility', 'physicalDisplaysInput', 'readers', 'independentMachineReplay'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('captures', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = compare(args.captures)
    if args.output:
        assert not args.output.exists(), 'Preserve earlier comparison attempts'
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))
    raise SystemExit(1)


if __name__ == '__main__':
    main()
