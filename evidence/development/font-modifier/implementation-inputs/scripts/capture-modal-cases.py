#!/usr/bin/env python3
"""Capture every original hosted Modal case through the installed Linux catalog."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/modal-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def definitions(source):
    assert source['reference'] == REFERENCE and source['fixtures'] == 36
    rows = source['captures']
    fixtures = {row['configuration']['fixture'] for row in rows}
    contexts = {(r['configuration']['fixture'], r['appearance'], r['textScale'], r['dpr']) for r in rows}
    assert len(rows) == 288 and len(fixtures) == 36 and contexts == set(itertools.product(
        fixtures, ['light', 'dark'], [1, 1.5], [1, 2])), 'Hosted Modal capture coverage changed'
    byname = {}
    for row in rows:
        assert row['publicProbedIdentical'] is True and row['publicWitnessIdentical'] is True
        assert len(row['paths']) == 3 and all(Path(path).name == path for path in row['paths'])
        definition = dict(row['configuration'])
        definition.update(api='BleeckerModal', source=REFERENCE,
                          expectedEmpty=definition['modalWidth'] == 0,
                          value=definition['modalWidth'], text=definition['title'],
                          variant='default', size='md', flag=False)
        name = definition['fixture']
        if name in byname:
            assert byname[name] == definition, 'Non-appearance inputs differ within a source fixture'
        byname[name] = definition
    return {'reference': REFERENCE, 'fixtures': list(byname.values())}


def capture(catalog, output):
    catalog, output = Path(catalog).resolve(), Path(output).resolve()
    assert catalog.is_file() and not output.exists(), 'Catalog required; output must be new to preserve failed attempts'
    output.mkdir(parents=True)
    source = json.loads((SOURCE / 'captures/captures.json').read_text())
    report = json.loads((SOURCE / 'investigation.json').read_text())
    assert report['referenceRevision'] == REFERENCE
    assert digest(SOURCE / 'captures/captures.json') == report['files']['captures/captures.json'], 'Native source fixture metadata changed'
    inputs = output / 'fixture-inputs.json'
    inputs.write_text(json.dumps(definitions(source), indent=2, ensure_ascii=False) + '\n')
    records = []
    for row in source['captures']:
        name, configuration = row['paths'][0], row['configuration']
        for original in row['paths']:
            assert digest(SOURCE / 'captures' / original) == report['files']['captures/' + original], 'Native source image changed'
        environment = dict(os.environ)
        environment.pop('QML_IMPORT_PATH', None)
        environment.pop('QML2_IMPORT_PATH', None)
        environment.update(QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
                           QT_SCALE_FACTOR=str(row['dpr']), LANG='C.UTF-8')
        command = [str(catalog), '--fixture', 'reference-case', '--case', configuration['fixture'],
                   '--case-definitions', str(inputs), '--text-scale', str(row['textScale']),
                   '--capture', str(output / name)]
        if row['appearance'] == 'dark':
            command.append('--dark')
        failure = None
        with (output / (name + '.log')).open('w') as log:
            try:
                result = subprocess.run(command, cwd=catalog.parent.parent.parent, env=environment,
                                        stdout=log, stderr=subprocess.STDOUT, timeout=30)
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
        assert struct.unpack('>II', image.read_bytes()[16:24]) == (
            configuration['width'] * row['dpr'], configuration['height'] * row['dpr']), 'No resizing is allowed'
        assert data['platform'] == 'offscreen' and data['qt'] == '6.8.3' and data['dpr'] == row['dpr']
        records.append({'path': name, 'sha256': digest(image), 'metadataSha256': digest(metadata),
                        'logSha256': digest(output / (name + '.log'))})
    (output / 'capture-results.json').write_text(json.dumps({'reference': REFERENCE, 'fixtures': 36, 'cases': len(records),
        'method': 'Installed relocatable catalog; source/build QML import overrides unset; original physical pixels retained',
        'catalogSha256': digest(catalog), 'fixtureInputsSha256': digest(inputs),
        'sourceInvestigationSha256': digest(SOURCE / 'investigation.json'),
        'accepted': False, 'records': records}, indent=2) + '\n')
    print(f'Installed Modal catalog: {len(records)} captures from 36 native source fixtures')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    capture(args.catalog, args.output)
