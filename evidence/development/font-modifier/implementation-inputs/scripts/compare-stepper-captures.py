#!/usr/bin/env python3
"""Compare hosted native Stepper investigation pixels and measured UI state."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/stepper-20261016'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


pixels = module('stepper_pixels', 'scripts/compare-captures.py')
native = module('stepper_native', 'scripts/verify-stepper-source.py')


def bounds(expected, actual):
    if not isinstance(actual, dict) or set(actual) != set(expected):
        return {'status': 'failed', 'reference': expected, 'candidate': actual, 'error': 'Missing or extra bounds'}
    delta = {key: actual[key] - expected[key] for key in expected}
    return {'status': 'passed' if all(abs(v) <= 1e-6 for v in delta.values()) else 'failed',
            'reference': expected, 'candidate': actual, 'delta': delta}


def compare(candidate, output):
    native.verify()
    candidate, output = Path(candidate), Path(output)
    assert not output.exists(), 'Comparison output must be new; preserve earlier attempts'
    source = json.loads((SOURCE / 'captures/captures.json').read_text())
    investigation = json.loads((SOURCE / 'investigation.json').read_text())
    fixtures = [{**row, 'sha256': investigation['files']['captures/' + row['path']],
                 'componentSize': {axis: row['componentRect'][axis] for axis in ['width', 'height']}} for row in source['captures']]
    # The comparison input is a hash/geometry projection of preserved source
    # metadata. Native images and the existing expected manifests stay untouched.
    pixels.compare(SOURCE / 'captures', candidate, output, manifest={'captures': fixtures})
    report = json.loads((output / 'comparison.json').read_text())
    byname = {row['path']: row for row in source['captures']}
    for result in report['results']:
        source_row = byname[result['fixture']]
        path = candidate / (source_row['path'] + '.json')
        if not path.is_file():
            continue
        metadata = json.loads(path.read_text())
        result['rootBounds'] = bounds(source_row['componentRect'], {**metadata.get('componentOrigin', {}), **metadata.get('componentSize', {})})
        if source_row['api'] == 'BleeckerStepper':
            expected = {key: source_row[key] for key in ['value', 'label', 'lowerBound', 'upperBound', 'step', 'displayOffset', 'formattedValue', 'decrementEnabled', 'incrementEnabled']}
            expected['displayValue'] = str(int(source_row['value']) + int(source_row['displayOffset']))
            errors = {key: {'reference': value, 'candidate': metadata.get(key)} for key, value in expected.items() if metadata.get(key) != value}
            result['stateStatus'] = 'failed' if errors else 'passed'
            result['stateErrors'] = errors
            parts = metadata.get('layoutWitnessRects', {})
            result['childBounds'] = {key: bounds(rect, parts.get(key)) for key, rect in source_row['layoutWitnessRects'].items()}
        else:
            result['stateStatus'] = 'not-applicable'
            result['childBounds'] = {}
        if result['rootBounds']['status'] == 'failed' or result['stateStatus'] == 'failed' or any(b['status'] == 'failed' for b in result['childBounds'].values()):
            result['status'] = 'failed'
    results = report['results']
    report.update(status='passed' if all(r['status'] == 'passed' for r in results) else 'failed', accepted=False,
        sourceInvestigationSha256=pixels.digest(SOURCE / 'investigation.json'),
        acceptance='Hosted native source investigation diagnostics only; no expected-image, source-pin, tolerance, font/symbol, physical or reader approval',
        captureMethodScope='Native NSHostingView inactive backing-2 windows with explicit bitmap/displayScale 1/2 versus Qt single-window captures. ImageRenderer placeholders are excluded.',
        summary={'cases': len(results), 'exactPixelAndGeometryMatches': sum(r['status'] == 'passed' for r in results),
                 'rootBoundsMatches': sum(r.get('rootBounds', {}).get('status') == 'passed' for r in results),
                 'stateMatches': sum(r.get('stateStatus') == 'passed' for r in results),
                 'childBoundsMatches': sum(b['status'] == 'passed' for r in results for b in r.get('childBounds', {}).values()),
                 'childBoundsFailures': sum(b['status'] != 'passed' for r in results for b in r.get('childBounds', {}).values())})
    (output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raise SystemExit(compare(args.candidate, args.output))
