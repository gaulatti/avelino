#!/usr/bin/env python3
"""Compare original hosted OTP source pixels, geometry and initial getter state."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/otp-20261016'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


pixels = module('otp_pixels', 'compare-captures.py')
native = module('otp_native', 'verify-otp-source.py')


def bounds(expected, actual):
    if not isinstance(actual, dict) or set(actual) != set(expected):
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
    fixtures = [{**row, 'sha256': investigation['files']['captures/' + row['path']],
                 'componentSize': {axis: row['native']['componentRect'][axis] for axis in ['width', 'height']}}
                for row in source['captures']]
    pixels.compare(SOURCE / 'captures', candidate, output, manifest={'captures': fixtures})
    report = json.loads((output / 'comparison.json').read_text())
    byname = {row['path']: row for row in source['captures']}
    for result in report['results']:
        row = byname[result['fixture']]
        path = candidate / (row['path'] + '.json')
        if not path.is_file():
            continue
        metadata = json.loads(path.read_text())
        result['rootBounds'] = bounds(row['native']['componentRect'], {**metadata.get('componentOrigin', {}), **metadata.get('componentSize', {})})
        if row['api'] == 'BleeckerOTPInput':
            expected = {'renderedCode': row['code'], 'renderedFieldValue': row['native']['fieldValue'],
                        'renderedPlaceholder': row['native']['placeholder'], 'renderedLength': row['length'],
                        'renderedDisabled': row['disabled'], 'renderedCenterAligned': True}
            errors = {key: {'reference': value, 'candidate': metadata.get(key)} for key, value in expected.items() if metadata.get(key) != value}
            result.update(stateStatus='failed' if errors else 'passed', stateErrors=errors)
            result['editorAdapterBounds'] = bounds(row['native']['fieldRect'], metadata.get('layoutWitnessRects', {}).get('qtTextField'))
            result['editorBoundsScope'] = 'AppKit field inside the SwiftUI presentation versus Qt template including its padding/background. Raw adapter frames retained separately; no like-for-like child-layout correspondence established. Public body bounds and original pixels remain strict.'
        else:
            result.update(stateStatus='not-applicable', editorAdapterBounds={'status': 'not-applicable'})
        if result['rootBounds']['status'] == 'failed' or result['stateStatus'] == 'failed':
            result['status'] = 'failed'
    results = report['results']
    report.update(status='passed' if all(row['status'] == 'passed' for row in results) else 'failed', accepted=False,
        sourceInvestigationSha256=pixels.digest(SOURCE / 'investigation.json'),
        acceptance='Hosted source diagnostics only; no source pin, expected image, tolerance, font, native lifecycle, physical/session or reader approval',
        captureMethodScope='Native inactive NSHostingView backing-2 windows with explicit bitmap/displayScale 1/2 versus original Qt single-window pixels',
        summary={'cases': len(results), 'exactPixelAndGeometryMatches': sum(row['status'] == 'passed' for row in results),
                 'rootBoundsMatches': sum(row.get('rootBounds', {}).get('status') == 'passed' for row in results),
                 'stateMatches': sum(row.get('stateStatus') == 'passed' for row in results),
                 'editorAdapterBoundsMatches': sum(row.get('editorAdapterBounds', {}).get('status') == 'passed' for row in results),
                 'editorAdapterBoundsDifferences': sum(row.get('editorAdapterBounds', {}).get('status') == 'failed' for row in results)})
    (output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raise SystemExit(compare(args.candidate, args.output))
