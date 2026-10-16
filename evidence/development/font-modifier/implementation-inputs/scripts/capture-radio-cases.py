#!/usr/bin/env python3
"""Capture every hosted RadioGroup source case through the installed Linux catalog."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/radio-20261016'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def definitions(source):
    rows = source['captures']
    fixtures = {row['fixture'] for row in rows}
    assert len(rows) == 440 and len(fixtures) == 55 and {(r['fixture'], r['appearance'], r['textScale'], r['dpr']) for r in rows} == set(itertools.product(fixtures, ['light', 'dark'], [1, 1.5], [1, 2])), 'Hosted RadioGroup capture coverage changed'
    assert all(row['captureMethod'] == 'NSHostingView.cacheDisplay in isolated NSWindow; explicit bitmap dimensions, no image resizing' for row in rows), 'Unsupported native capture method'
    byname = {}
    keys = ['fixture', 'api', 'width', 'height', 'proposalWidth', 'intrinsic', 'selection',
            'orientation', 'disabled', 'rtl', 'observeOnly', 'parentFont', 'parentFontKind',
            'parentFontWeight', 'parentForeground', 'processLocale', 'environmentLocale', 'source']
    for row in source['captures']:
        definition = {key: row[key] for key in keys}
        definition.update(expectedEmpty=row["api"]=="BleeckerRadioGroup" and not row["options"], options=[{key: option[key] for key in ['value', 'label', 'disabled']} for option in row['options']],
                          value=0, text='Publish', variant='primary', size='md', flag=False)
        if row['fixture'] in byname:
            assert byname[row['fixture']] == definition, 'Non-appearance inputs differ within a source fixture'
        byname[row['fixture']] = definition
    assert len(byname) == 55
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
        failure = None
        with (output / (name + '.log')).open('w') as log:
            try:
                result = subprocess.run(command, cwd=catalog.parent.parent.parent, env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=30)
                if result.returncode != 0:
                    failure = {'returnCode': result.returncode}
            except subprocess.TimeoutExpired:
                failure = {'failure': 'timeout', 'timeoutSeconds': 30}
        if failure is not None:
            (output / 'failed-capture.json').write_text(json.dumps({'path': name, **failure,
                'pngWritten': (output / name).exists(), 'metadataWritten': (output / (name + '.json')).exists(),
                'catalogSha256': digest(catalog), 'command': command}, indent=2) + '\n')
            raise AssertionError(f'Capture failed: {failure}; raw attempt retained at {output / (name + ".log")}')
        image, metadata = output / name, output / (name + '.json')
        data = json.loads(metadata.read_text())
        assert struct.unpack('>II', image.read_bytes()[16:24]) == (row['width'] * row['dpr'], row['height'] * row['dpr']), 'No resizing is allowed'
        assert data['platform'] == 'offscreen' and data['qt'] == '6.8.3' and data['dpr'] == row['dpr']
        records.append({'path': name, 'sha256': digest(image), 'metadataSha256': digest(metadata), 'logSha256': digest(output / (name + '.log'))})
    (output / 'capture-results.json').write_text(json.dumps({'reference': source['reference'], 'fixtures': 55, 'cases': len(records),
        'method': 'Installed relocatable catalog; source/build QML import overrides unset; original physical pixels retained',
        'catalogSha256': digest(catalog), 'fixtureInputsSha256': digest(inputs), 'sourceInvestigationSha256': digest(SOURCE / 'investigation.json'),
        'accepted': False, 'records': records}, indent=2) + '\n')
    print(f'Installed RadioGroup catalog: {len(records)} captures from 55 native source fixtures')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    capture(args.catalog, args.output)
