#!/usr/bin/env python3
"""Compare original native and installed-consumer PNGs without pixel transforms."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir()  # Refuse to overwrite earlier comparison evidence.
    reference = args.output / 'reference'
    candidate = args.output / 'candidate'
    reference.mkdir(); candidate.mkdir()
    sealed = json.loads((ROOT / "evidence/reference-investigations/date-range-20261018/files.json").read_text())
    captures = []
    originals = []
    for report_path in args.report:
        report = json.loads(report_path.read_text())
        assert report['fixture'] == 'date-range' and report['accepted'] is False
        assert len(report['closed']) == 48
        pairs = [(row, 'output', report_path.stem + '-' + row['configuration']['id'] + '.png') for row in report['closed']]
        pairs += [(row, 'history-output', report_path.stem + '-history-' + row['step'] + '.png') for row in report.get('histories', [])]
        for row, directory, name in pairs:
            native = row['native']
            if directory == 'output': assert native['configuration'] == row['configuration']
            original = ROOT / 'evidence/reference-investigations/date-range-20261018' / directory / native['referenceCapture']
            actual = report_path.with_name(name)
            assert original.is_file() and actual.is_file()
            (reference / name).symlink_to(original.resolve())
            (candidate / name).symlink_to(actual.resolve())
            metadata = {key: report[key] for key in ('width', 'height', 'dpr', 'textScale', 'appearance')}
            metadata['api'] = 'BleeckerDateRangePicker'
            expected_metadata = dict(metadata)
            if directory == 'history-output':
                metadata['appearance'] = 'dark' if row['actualDark'] else 'light'
                expected_metadata['appearance'] = 'dark' if native['dark'] else 'light'
            (candidate / (name + '.json')).write_text(json.dumps(metadata) + '\n')
            captures.append(dict(path=name, source=report['reference'], sha256=sealed[directory+'/'+native['referenceCapture']]['sha256'], **expected_metadata))
            originals.append(dict(path=name, native=str(original), actual=str(actual),
                exactModelMatches=row['modelMatches'], exactGeometryMatches=row['geometryMatches']))
    spec = importlib.util.spec_from_file_location('avelino_compare', ROOT / 'scripts/compare-captures.py')
    comparator = importlib.util.module_from_spec(spec); spec.loader.exec_module(comparator)
    (args.output / 'original-paths.json').write_text(json.dumps(originals, indent=2) + '\n')
    result = comparator.compare(reference, candidate, args.output / 'comparison', manifest={'captures': captures})
    print(f'DateRangePicker: {len(captures)} exact original-image comparisons; no transformations or acceptance exceptions')
    raise SystemExit(result)


if __name__ == '__main__':
    main()
