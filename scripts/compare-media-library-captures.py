#!/usr/bin/env python3
"""Compare every observed MediaLibrary pixel, frame and lifecycle with no tolerance."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

inputs = module('media_capture_inputs', 'capture-media-library.py')
def compare(candidate, output):
    pixels = module('media_pixels', 'compare-captures.py')
    candidate, output = Path(candidate), Path(output)
    assert not output.exists()
    corpus = inputs.rows()
    manifest = {'captures': [dict(path=r['path'], source=inputs.REFERENCE,
        sha256=inputs.digest(ROOT / r['reference']), api='BleeckerMediaLibrary', fixture=r['path'],
        width=640, height=400, dpr=r['dpr'], textScale=r['textScale'], appearance=r['appearance']) for r in corpus]}
    with tempfile.TemporaryDirectory(prefix='avelino-media-reference-') as temporary:
        refs = Path(temporary)
        for row in corpus:
            (refs / row['path']).symlink_to((ROOT / row['reference']).resolve())
        pixels.compare(refs, candidate, output, manifest=manifest)
    report = json.loads((output / 'comparison.json').read_text())
    expected = {r['path']: r for r in corpus}
    for result in report['results']:
        row = expected[result['fixture']]
        result['reference'] = str(ROOT / row['reference'])
        result['kind'] = row['kind']
        meta = candidate / (row['path'] + '.json')
        result.update(inputs.observations(row, json.loads(meta.read_text()) if meta.is_file() else {}))
        result['pixelStatus'] = result['status']
        if any(result[k] == 'failed' for k in ['nativeFrameStatus', 'nativeLifecycleStatus', 'stateStatus', 'retainedRasterStatus']):
            result['status'] = 'failed'
    results = report['results']
    summary = dict(cases=len(results), exactMatches=sum(r['status'] == 'passed' for r in results),
        pixelMatches=sum(r['pixelStatus'] == 'passed' for r in results),
        nativeFrameMatches=sum(r['nativeFrameStatus'] == 'passed' for r in results),
        nativeLifecycleMatches=sum(r['nativeLifecycleStatus'] == 'passed' for r in results),
        stateMatches=sum(r['stateStatus'] == 'passed' for r in results),
        sizingObservations=0, nativeSizingContexts=496, nativeSizingQueries=7440,
        retainedRestoreObservations=48, retainedRestorePixelMatches=sum(expected[r['fixture']]['kind']=='history' and expected[r['fixture']]['step']=='restore' and r['retainedRasterStatus']=='passed' for r in results),
        byKind={kind: dict(cases=sum(r['kind'] == kind for r in results),
            exactMatches=sum(r['kind'] == kind and r['status'] == 'passed' for r in results)) for kind in ['closed', 'edge', 'history']})
    report.update(accepted=False, status='failed', summary=summary,
        acceptance='Complete strict diagnostic; direct sizing is unobserved. Native sizing, lazy timing, raster, physical input, readers and independent-machine replay remain pending. No inputs excluded.')
    (output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raise SystemExit(compare(args.candidate, args.output))
