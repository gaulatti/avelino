#!/usr/bin/env python3
"""Compare every original native PNG and caller observation without tolerance."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def compare(candidate, output):
    capture = module('spotlight_capture', ROOT / 'scripts/capture-command-spotlight.py')
    strict = module('strict_compare', ROOT / 'scripts/compare-captures.py')
    rows = capture.rows()
    assert not output.exists(), 'Use a fresh comparison directory'
    output.mkdir(parents=True)
    aliases = output / 'candidate-inputs'
    manifest, witnesses = [], []
    assert len({Path(row['reference']).stem for row in rows}) == len(rows)
    for row in rows:
        path = candidate / row['path']
        assert path.is_file() and Path(str(path) + '.json').is_file(), path
        actual = json.loads(Path(str(path) + '.json').read_text())
        alias = aliases / row['reference']
        alias.parent.mkdir(parents=True, exist_ok=True)
        alias.symlink_to(path.resolve())
        Path(str(alias) + '.json').symlink_to(Path(str(path) + '.json').resolve())
        manifest.append(dict(path=row['reference'], source=capture.REFERENCE,
            sha256=strict.digest(ROOT / row['reference']),
            dpr=row['dpr'], textScale=row['textScale'], appearance=row['appearance']))
        witnesses.append(dict(path=row['path'], reference=row['reference'], **capture.observations(row, actual)))
    result = strict.compare(ROOT, aliases, output / 'pixels', manifest=dict(captures=manifest))
    pixels = json.loads((output / 'pixels/comparison.json').read_text())
    report = dict(accepted=False, reference=capture.REFERENCE, cases=len(rows),
        tolerance='none', expectedImagesChanged=False,
        exactPixels=sum(row['status'] == 'passed' for row in pixels['results']),
        frames=sum(row['nativeFrameStatus'] == 'passed' for row in witnesses),
        states=sum(row['stateStatus'] == 'passed' for row in witnesses),
        retainedRasterChecks=sum(row['retainedRasterStatus'] == 'passed' for row in witnesses),
        witnesses=witnesses)
    (output / 'observations.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'witnesses'}, indent=2))
    return 0 if result == 0 and report['frames'] == report['states'] == report['retainedRasterChecks'] == len(rows) else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    raise SystemExit(compare(args.candidate.resolve(), args.output.resolve()))
