#!/usr/bin/env python3
"""Project preserved native number witnesses into the source-free consumer."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/number-locales-20261016'
OUTPUT = ROOT / 'tests/consumer/native-metric-formatting.json'
LOCALES = ['en_US', 'de_DE', 'es_CL', 'fr_FR', 'ja_JP', 'ar_EG', 'hi_IN']


def build():
    files = {}
    cases = []

    def read(path):
        files[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        return json.loads(path.read_text())

    for name in LOCALES:
        data = read(ROOT / 'evidence/reference-investigations/data-metrics-20261015' / ('locale-' + name) / 'captures.json')
        cases.extend({**row, 'group': 'original'} for row in data['formatting'])
    for filename, key, group in [('native-expanded-formatting.json', 'additionalFormatting', 'wide-double'),
                                 ('native-compact-boundaries.json', 'results', 'compact-boundaries')]:
        for row in read(SOURCE / filename)[key]:
            cases.append({'bits': row['bits'].zfill(16), 'format': 'percent' if row['format'] == 'signedPercent' else row['format'],
                          'signedPercent': row['format'] == 'signedPercent', 'currencyCode': row['currencyCode'],
                          'processLocale': row['locale'], 'text': row['text'], 'group': group})
    return {'schemaVersion': 2, 'reference': 'fe8a1d462fbd793d883fb92086a16aa2947e32c9', 'sourceFiles': files,
            'groups': {'original': 1330, 'wide-double': 19460, 'compact-boundaries': 28658}, 'cases': cases}


def render(data):
    metadata = {key: value for key, value in data.items() if key != 'cases'}
    return json.dumps(metadata, indent=2, ensure_ascii=True)[:-2] + ',\n  "cases": [\n' + ',\n'.join(
        '    ' + json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(',', ':')) for row in data['cases']) + '\n  ]\n}\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    arguments = parser.parse_args()
    content = render(build())
    if arguments.check:
        assert OUTPUT.read_text() == content, 'Embedded native number witnesses need regeneration'
    else:
        OUTPUT.write_text(content)
    print('Native formatter projection: 49,448 cases across seven locales')
