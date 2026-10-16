#!/usr/bin/env python3
"""Project native RadioGroup identity facts and consumer traces without changing source evidence."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/radio-20261016'


def projected():
    names = ['behavior/behavior.json', 'native-string-identity.json', 'native-normalization-data.json']
    data = {name: json.loads((SOURCE / name).read_text()) for name in names}
    hashes = {name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() for name in names}
    profile = data[names[2]]
    assert profile['unicodeVersion'] == [17, 0, 0, 0] and len(profile['decompositions']) == 13253
    # The 11,172 Hangul syllables use the standard algorithm instead of a lookup table.
    canonical = {key: value for key, value in profile['decompositions'].items() if not 0xac00 <= int(key, 16) < 0xac00 + 11172}
    assert len(canonical) == 2081 and len(profile['combiningClasses']) == 968
    resource = {'unicodeVersion': '17.0.0', 'canonical': canonical, 'combiningClasses': profile['combiningClasses']}
    consumer = {'reference': profile['reference'], 'sourceFiles': hashes, 'traces': data[names[0]]['traces'],
                'pointerPhases': data[names[0]]['pointerPhases'], 'stringPairs': data[names[1]]['results']}
    return {
        ROOT / 'src/Avelino/unicode-normalization-17.json': json.dumps(resource, separators=(',', ':'), sort_keys=True) + '\n',
        ROOT / 'tests/consumer/native-radio-witnesses.json': json.dumps(consumer, indent=2, ensure_ascii=False) + '\n',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, text in projected().items():
        if args.check:
            assert path.read_text() == text, f'Native RadioGroup projection differs: {path.relative_to(ROOT)}'
        else:
            path.write_text(text)
    print('Native RadioGroup: Unicode 17 NFD facts, 24 binding traces, 11 pointer phases, 13,762 String pairs')
