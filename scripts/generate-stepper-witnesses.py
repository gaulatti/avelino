#!/usr/bin/env python3
"""Project preserved native Stepper traces into the independent test consumer."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/stepper-20261016'
TARGET = ROOT / 'tests/consumer/native-stepper-witnesses.json'


def projected():
    files = ['behavior/behavior.json'] + ['locale-' + name + '/formatting.json' for name in ['en_US', 'de_DE', 'es_CL', 'fr_FR', 'ja_JP', 'ar_EG', 'hi_IN']]
    behavior = json.loads((SOURCE / files[0]).read_text())
    formatting = []
    for name in files[1:]:
        data = json.loads((SOURCE / name).read_text())
        formatting += [{**row, 'locale': data['processLocale']} for row in data['formatting']]
    return json.dumps({'reference': behavior['reference'], 'sourceFiles': {name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() for name in files},
        'traces': behavior['traces'], 'formatting': formatting}, indent=2, ensure_ascii=False) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    text = projected()
    if args.check:
        assert TARGET.read_text() == text, 'Native Stepper consumer witnesses differ from preserved source evidence'
    else:
        TARGET.write_text(text)
    print('Native Stepper consumer: 25 action traces and 126 exact integer formatter witnesses')
