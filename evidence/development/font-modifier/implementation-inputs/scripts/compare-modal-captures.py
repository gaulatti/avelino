#!/usr/bin/env python3
"""Compare original hosted Modal pixels, layout frames and initial state."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/modal-20261016'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


pixels = module('modal_pixels', 'compare-captures.py')
native = module('modal_native', 'verify-modal-source.py')
inputs = module('modal_inputs', 'capture-modal-cases.py')


def bounds(expected, actual):
    if (not isinstance(actual, dict) or set(actual) != set(expected)
            or any(type(actual[key]) not in [int, float] or not math.isfinite(actual[key]) for key in expected)):
        return {'status': 'failed', 'reference': expected, 'candidate': actual, 'error': 'Missing or extra bounds'}
    delta = {key: actual[key] - expected[key] for key in expected}
    return {'status': 'passed' if all(abs(value) <= 1e-6 for value in delta.values()) else 'failed',
            'reference': expected, 'candidate': actual, 'delta': delta}


def compare(candidate, output):
    native.verify()
    candidate, output = Path(candidate), Path(output)
    assert not output.exists(), 'Comparison output must be new; preserve earlier attempts'
    source = json.loads((SOURCE / 'captures/captures.json').read_text())
    investigation = json.loads((SOURCE / 'investigation.json').read_text())
    definitions = {r['fixture']: r for r in inputs.definitions(source)['fixtures']}
    fixtures = [{**definitions[row['configuration']['fixture']],
                 'appearance': row['appearance'], 'textScale': row['textScale'], 'dpr': row['dpr'],
                 'path': row['paths'][0], 'sha256': investigation['files']['captures/' + row['paths'][0]],
                 'componentSize': {axis: row['witness']['parts']['root'][axis] for axis in ['width', 'height']}}
                for row in source['captures']]
    pixels.compare(SOURCE / 'captures', candidate, output, manifest={'captures': fixtures})
    report = json.loads((output / 'comparison.json').read_text())
    byname = {row['paths'][0]: row for row in source['captures']}
    for result in report['results']:
        row = byname[result['fixture']]
        path = candidate / (row['paths'][0] + '.json')
        if not path.is_file():
            continue
        metadata, configuration = json.loads(path.read_text()), row['configuration']
        result['rootBounds'] = bounds(row['witness']['parts']['root'], {
            **metadata.get('componentOrigin', {}), **metadata.get('componentSize', {})})
        result['offeredFrame'] = bounds({
            'width': configuration['modalWidth'] if configuration['outerOffer'] is None else configuration['outerOffer'],
            'height': row['witness']['parts']['root']['height']}, metadata.get('offeredFrameSize'))
        expected = {'renderedTitle': configuration['title'], 'renderedModalWidth': configuration['modalWidth'],
                    'renderedContent': configuration['content'], 'renderedDisabled': configuration['disabled'],
                    'renderedRtl': configuration['rtl']}
        errors = {key: {'reference': value, 'candidate': metadata.get(key)}
                  for key, value in expected.items() if metadata.get(key) != value}
        result.update(stateStatus='failed' if errors else 'passed', stateErrors=errors)
        parts = metadata.get('layoutWitnessRects', {})
        result['childBounds'] = {key: bounds(value, parts.get(key)) for key, value in row['witness']['parts'].items()}
        result['childBoundsStatus'] = 'passed' if all(value['status'] == 'passed'
                                                    for value in result['childBounds'].values()) else 'failed'
        if (result['rootBounds']['status'] == 'failed' or result['offeredFrame']['status'] == 'failed'
                or errors or result['childBoundsStatus'] == 'failed'):
            result['status'] = 'failed'
    results = report['results']
    report.update(status='passed' if all(row['status'] == 'passed' for row in results) else 'failed', accepted=False,
        sourceInvestigationSha256=pixels.digest(SOURCE / 'investigation.json'),
        acceptance='Hosted source diagnostics only; no source pin, expected image, tolerance, font, symbol, physical/session or reader approval',
        captureMethodScope='Native inactive NSHostingView backing-2 windows with explicit bitmap/displayScale 1/2 versus original Qt single-window pixels',
        childFrameScope='Native GeometryReader frames versus Qt layout positions; Qt text paint translations remain separate raw metadata and original pixels',
        summary={'cases': len(results), 'exactPixelAndGeometryMatches': sum(row['status'] == 'passed' for row in results),
                 'rootBoundsMatches': sum(row.get('rootBounds', {}).get('status') == 'passed' for row in results),
                 'stateMatches': sum(row.get('stateStatus') == 'passed' for row in results),
                 'allChildBoundsMatches': sum(row.get('childBoundsStatus') == 'passed' for row in results)})
    (output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raise SystemExit(compare(args.candidate, args.output))
