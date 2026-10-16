#!/usr/bin/env python3
"""Capture every hosted Stepper source case through the installed Linux catalog."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/stepper-20261016'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def definitions(source):
    rows = source['captures']
    fixtures = {row['fixture'] for row in rows}
    assert len(rows) == 344 and len(fixtures) == 43 and {(r['fixture'], r['appearance'], r['textScale'], r['dpr']) for r in rows} == set(itertools.product(fixtures, ['light', 'dark'], [1, 1.5], [1, 2])), 'Hosted Stepper capture coverage changed'
    assert all(row['captureMethod'] == 'NSHostingView.cacheDisplay in isolated NSWindow; explicit bitmap dimensions, no image resizing' for row in rows), 'Unsupported native capture method'
    byname = {}
    keys = ['fixture', 'api', 'width', 'height', 'proposalWidth', 'intrinsic', 'label', 'lowerBound', 'upperBound', 'step', 'displayOffset', 'disabled', 'rtl', 'initializer', 'observeOnly', 'parentFont', 'requestedControlState', 'processLocale', 'environmentLocale', 'source']
    for row in source['captures']:
        definition = {key: row[key] for key in keys}
        definition.update(stepperValue=row['value'], value=row['value'] if row['api'] == 'BleeckerButton' else 0,
                          text='Publish' if row['api'] == 'BleeckerButton' else row['label'], variant='primary', size='md', flag=False)
        if row['fixture'] in byname:
            assert byname[row['fixture']] == definition, 'Non-appearance inputs differ within a source fixture'
        byname[row['fixture']] = definition
    assert len(byname) == 43
    return {'reference': source['reference'], 'fixtures': list(byname.values())}


def capture(catalog, output):
    catalog, output = Path(catalog).resolve(), Path(output).resolve()
    assert catalog.is_file() and not output.exists(), 'Catalog required; output must be new to preserve failed attempts'
    output.mkdir(parents=True)
    source = json.loads((SOURCE / 'captures/captures.json').read_text())
    report = json.loads((SOURCE / 'investigation.json').read_text())
    assert source['reference'] == report['referenceRevision'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert digest(SOURCE / 'captures/captures.json') == report['files']['captures/captures.json'], 'Native source fixture metadata changed'
    inputs = output / 'fixture-inputs.json'
    inputs.write_text(json.dumps(definitions(source), indent=2, ensure_ascii=False) + '\n')
    records = []
    for row in source['captures']:
        name = row['path']
        assert Path(name).name == name
        native = SOURCE / 'captures' / name
        assert digest(native) == report['files']['captures/' + name], 'Native source image changed'
        environment = dict(os.environ)
        environment.pop('QML_IMPORT_PATH', None)
        environment.pop('QML2_IMPORT_PATH', None)
        environment.update(QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software', QT_SCALE_FACTOR=str(row['dpr']), LANG='C.UTF-8')
        command = [str(catalog), '--fixture', 'reference-case', '--case', row['fixture'], '--case-definitions', str(inputs),
                   '--text-scale', str(row['textScale']), '--capture', str(output / name)]
        if row['appearance'] == 'dark':
            command.append('--dark')
        with (output / (name + '.log')).open('w') as log:
            result = subprocess.run(command, cwd=catalog.parent.parent.parent, env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=30)
        assert result.returncode == 0, f'Capture failed; raw attempt retained at {output / (name + ".log")}'
        image, metadata = output / name, output / (name + '.json')
        data = json.loads(metadata.read_text())
        assert struct.unpack('>II', image.read_bytes()[16:24]) == (row['width'] * row['dpr'], row['height'] * row['dpr']), 'No resizing is allowed'
        assert data['platform'] == 'offscreen' and data['qt'] == '6.8.3' and data['dpr'] == row['dpr']
        records.append({'path': name, 'sha256': digest(image), 'metadataSha256': digest(metadata), 'logSha256': digest(output / (name + '.log'))})
    (output / 'capture-results.json').write_text(json.dumps({'reference': source['reference'], 'fixtures': 43, 'cases': len(records),
        'method': 'Installed relocatable catalog; source/build QML import overrides unset; original physical pixels retained',
        'catalogSha256': digest(catalog), 'fixtureInputsSha256': digest(inputs), 'sourceInvestigationSha256': digest(SOURCE / 'investigation.json'),
        'accepted': False, 'records': records}, indent=2) + '\n')
    print(f'Installed Stepper catalog: {len(records)} captures from 43 native source fixtures')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    capture(args.catalog, args.output)
