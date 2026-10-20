#!/usr/bin/env python3
"""Verify public sizing evidence without granting renderer acceptance."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'evidence/reference-investigations/date-range-reservation-20261018'
PIN='fe8a1d462fbd793d883fb92086a16aa2947e32c9'

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    manifest=read(NATIVE/'files.json')
    assert set(manifest)=={str(p.relative_to(NATIVE)) for p in NATIVE.rglob('*') if p.is_file() and p.name!='files.json'}
    for name,value in manifest.items():
        path=NATIVE/name
        assert path.stat().st_size==value['bytes'] and sha(path)==value['sha256'],name
    result=read(NATIVE/'result.json')
    assert result['accepted'] is False and result['reference']==PIN
    assert result['approvedExceptions']==[] and result['tolerance']=='none'
    assert not result['privateDiagnosticsAcceptance'] and not result['independentMachineAcceptance']
    baseline=read(NATIVE/'baseline-bindings.json');assert len(baseline)==59
    for row in baseline:
        original=ROOT/row['path'];assert sha(original)==row['sha256']
        for suffix in ['', '-after']:
            assert (NATIVE/'calibration/output'/(row['configuration']+suffix+'.png')).read_bytes()==original.read_bytes()
    calibration=read(NATIVE/'calibration/output/bare.json');assert calibration['accepted'] is False and calibration['reference']==PIN
    endpoints=0
    for row in calibration['rows']:
        assert row['originalImagesEqual']
        for editor in row['editors']:
            assert all(editor['source'+key]==editor['bare'+key] for key in ['Intrinsic','CellSize','Insets']);endpoints+=1
    assert endpoints==118
    validation=read(NATIVE/'validation/output/validation.json');assert validation['accepted'] is False and validation['reference']==PIN
    observations=[o for row in validation['rows'] for o in row['observations']]
    assert len(observations)==472
    assert all(o['actualIntrinsicWidth']==o['predictedIntrinsicWidth'] for o in observations)
    assert sum(o['actualCellWidth']==o['predictedCellWidth'] for o in observations)==456
    source=[o for o in observations if o['fontProfile']=='source'];assert len(source)==118
    assert all(o['matches'] and o['actualCellWidth']==o['predictedCellWidth'] for o in source)
    for label,filename in [('validation','validation.json'),('vocabulary','vocabulary.json'),('diagnostics','private-subfields.json')]:
        data=read(NATIVE/label/'output'/filename);assert data['accepted'] is False and data['reference']==PIN
        for row in data['rows']:
            assert row['originalImagesEqual']
            name=row['configuration']['id']
            assert (NATIVE/label/'output'/(name+'.png')).read_bytes()==(NATIVE/label/'output'/(name+'-after.png')).read_bytes()
            assert (NATIVE/label/'output'/(name+'.png')).read_bytes()==(NATIVE/'calibration/output'/(name+'.png')).read_bytes()
    years=read(NATIVE/'year-boundaries/output/bounds.json');assert years['accepted'] is False and years['reference']==PIN
    fixtures=read(NATIVE/'year-boundaries/fixtures.json');assert len(years['rows'])==len(fixtures)==63
    configurations={row['id']:row for row in fixtures}
    widths={}
    for row in years['rows']:
        cfg=row['configuration'];expected=configurations[cfg['id']]
        # Swift Codable omits nil optional fixture fields on re-encoding.
        decoded={key:value for key,value in expected.items() if not (key in {'lower','upper','width','height'} and value is None)}
        assert cfg==decoded
        for editor in row['editors']:
            assert editor['date']==expected['start']
            widths.setdefault((cfg['locale'],cfg['calendar']),set()).add(tuple(editor['intrinsic'][key] for key in ['width','height']))
        name=cfg['id']
        assert (NATIVE/'year-boundaries/output'/(name+'.png')).read_bytes()==(NATIVE/'year-boundaries/output'/(name+'-after.png')).read_bytes()
    assert len(widths)==7 and all(len(values)==1 for values in widths.values())
    archive=read(NATIVE/'source-only-artifact.json');assert archive['files']==len(archive['sourceFiles'])==102
    assert archive['pinnedSourceFiles']==89 and archive['compiledOutputs'] is False
    earlier=read(ROOT/'evidence/reference-investigations/date-range-width-20261018/source-only-replay/artifact.json')
    pinned={name:value for name,value in archive['sourceFiles'].items() if name.startswith('source/')}
    assert len(pinned)==89 and all(earlier['sourceFiles'][name]==value for name,value in pinned.items())
    replay=read(NATIVE/'source-only-result.json');assert replay['exitCode']==0 and replay['outputFiles']==replay['exactOutputs']==380
    assert replay['differences']==[] and not replay['privateDiagnosticsReplayed']
    prior=read(NATIVE/'source-only-prior/result.json')
    assert prior['exitCode']==1 and prior['outputFiles']==380 and prior['differences']==['vocabulary-output/vocabulary.json']
    assert read(NATIVE/'vocabulary/prior-output.json')==read(NATIVE/'vocabulary/output/vocabulary.json')
    labels={'calibration-output':'calibration','validation-output':'validation','vocabulary-output':'vocabulary','year-output':'year-boundaries'}
    for folder,row in replay['outputs'].items():
        directory=NATIVE/labels[folder]/'output';actual={str(p.relative_to(directory)):sha(p) for p in directory.rglob('*') if p.is_file()}
        assert row['exact'] and row['files']==len(actual) and row['sha256']==actual
    print('Date reservation evidence verified: 118 calibrated endpoints, 472 exact intrinsic widths, 380 exact source-only outputs; acceptance pending')

if __name__=='__main__':
    verify()
