#!/usr/bin/env python3
"""Verify native numeric oracles and locale data without accepting Qt parity."""
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/number-locales-20261016'
LOCALES = {'en_US', 'de_DE', 'es_CL', 'fr_FR', 'ja_JP', 'ar_EG', 'hi_IN'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory=DIRECTORY):
    directory = Path(directory)
    report = json.loads((directory / 'investigation.json').read_text())
    reference = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    assert report['referenceRevision'] == reference['revision']
    assert report['accepted'] is False and report['existingExpectedImagesChanged'] is False
    actual = {p.name for p in directory.iterdir() if p.is_file()}
    assert actual == set(report['files']) | {'investigation.json'}, 'Missing or extra number source evidence'
    for name, expected in report['files'].items():
        assert Path(name).name == name and digest(directory / name) == expected, name
    native = json.loads((directory / 'native-locale-data.json').read_text())
    linux = json.loads((directory / 'linux-locale-data.json').read_text())
    assert native['icuVersion'] == report['nativeIcuVersion'] == [78, 1, 0, 0]
    assert native['cldrVersion'] == report['nativeCldrVersion'] == [48, 0, 0, 0]
    assert linux['icuVersion'] == report['linuxIcuVersion'] == [74, 2, 0, 0]
    assert linux['cldrVersion'] == report['linuxCldrVersion'] == [44, 1, 0, 0]
    assert set(native['locales']) == set(linux['locales']) == set(report['locales']) == LOCALES
    assert native['locales']['ar_EG']['nan'] == 'ليس رقمًا', 'Native Arabic NaN symbol changed'
    assert native['locales']['ja_JP']['currencySymbols']['JPY'] == '¥', 'Native Japanese yen symbol changed'
    patterns = native['locales']['es_CL']['compactDecimalPatterns']
    for exponent in range(9, 12):
        assert patterns[str(10 ** exponent)] == {'one': '0' * (exponent - 8) + 'k M', 'other': '0' * (exponent - 8) + 'k M'}, 'Native compact pattern changed'

    expanded = json.loads((directory / 'native-expanded-formatting.json').read_text())
    assert expanded['sourceRevision'] == reference['revision'] and expanded['cases'] == len(expanded['results']) == 1330
    original = {}
    for name in LOCALES:
        source = ROOT / 'evidence/reference-investigations/data-metrics-20261015' / ('locale-' + name) / 'captures.json'
        for row in json.loads(source.read_text())['formatting']:
            original[(name, row['value'], row['format'], row['currencyCode'])] = row['text']
    replayed = {}
    for row in expanded['results']:
        key = (row['processLocale'], row['value'], row['format'], row['currencyCode'])
        assert row['equal'] is True and row['recorded'] == row['fresh'] == original[key], 'Original native number replay changed'
        replayed[key] = row['fresh']
    assert replayed == original and expanded['mismatches'] == 0
    rows = expanded['additionalFormatting']
    bits = {row['bits'] for row in rows}
    assert len(bits) == expanded['additionalValueCount'] == report['expandedDoubleValues'] == 278
    formats = {('number', 'USD'), ('percent', 'USD'), ('signedPercent', 'USD'), ('compact', 'USD')} | {('currency', c) for c in ['USD', 'JPY', 'CLP', 'KWD', 'EUR', 'XXX']}
    expected = {(name, bits, fmt, code) for name, bits, (fmt, code) in itertools.product(LOCALES, bits, formats)}
    assert len(rows) == report['expandedFormatterWitnesses'] == len(expected) == 19460
    assert {(r['locale'], r['bits'], r['format'], r['currencyCode']) for r in rows} == expected, 'Expanded native number coverage changed'
    dense = json.loads((directory / 'native-compact-boundaries.json').read_text())
    assert dense['referenceRevision'] == reference['revision'] and dense['randomSeed'] == '510e527fade682d1' and dense['randomSamples'] == 500
    rows = dense['results']
    bits = {row['bits'] for row in rows}
    assert len(bits) == dense['values'] == report['compactBoundaryValues'] == 4094
    assert len(rows) == dense['cases'] == report['compactBoundaryWitnesses'] == 28658
    assert {(r['locale'], r['bits']) for r in rows} == set(itertools.product(LOCALES, bits)), 'Compact native boundary coverage changed'
    assert all(r['format'] == 'compact' and r['currencyCode'] == 'USD' and isinstance(r['text'], str) and 0 <= int(r['bits'], 16) < 2 ** 64 for r in rows)

    replay = json.loads((directory / 'clean-replay.json').read_text())
    assert replay['inputFiles'] == 11 and replay['compiledInputs'] == []
    assert replay['filesCompared'] == replay['byteIdenticalFiles'] == len(replay['results']) == 3
    assert {r['path'] for r in replay['results']} == {'native-expanded-formatting.json', 'native-compact-boundaries.json', 'native-locale-data.json'}
    for row in replay['results']:
        assert row['byteIdentical'] is True and row['sha256'] == row['replaySha256'] == digest(directory / row['path']), 'Native numeric source replay changed'
    provenance = json.loads((directory / 'tooling-provenance.json').read_text())
    assert provenance['referenceRevision'] == reference['revision'] and len(provenance['toolArtifact']['files']) == 12
    for name in LOCALES:
        filename = 'inputs/locale-' + name + '/captures.json'
        assert provenance['toolArtifact']['files'][filename] == digest(ROOT / 'evidence/reference-investigations/data-metrics-20261015' / ('locale-' + name) / 'captures.json')
    return {'originalNativeReplay': 1330, 'expandedFormatterWitnesses': 19460, 'compactBoundaryWitnesses': 28658, 'locales': 7, 'accepted': False}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
