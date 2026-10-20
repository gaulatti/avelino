#!/usr/bin/env python3
"""Check Chinese date evidence while retaining all acceptance boundaries."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];CAP=ROOT/'evidence/reference-investigations/date-range-chinese-20261018'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    manifest=read(CAP/'files.json');assert set(manifest)=={str(p.relative_to(CAP)) for p in CAP.rglob('*') if p.is_file() and p.name!='files.json'}
    for name,value in manifest.items():
        p=CAP/name;assert p.stat().st_size==value['bytes'] and sha(p)==value['sha256'],name
    result=read(CAP/'result.json');assert result['accepted'] is False and result['sourceOnlyExactOutputs']==153 and result['approvedExceptions']==[] and result['tolerance']=='none'
    samples=read(CAP/'samples/output/samples.json')['rows'];diags={r['configuration']['id']:r for r in read(CAP/'diagnostics/output/private-subfields.json')['rows']};assert len(samples)==len(diags)==36
    initial={r['configuration']['locale']:r for r in read(CAP/'initial/output/bare.json')['rows']};endpoint_count=0
    for row in samples:
        cfg=row['configuration'];name=cfg['id'];assert row['originalImagesEqual'] and diags[name]['originalImagesEqual']
        assert row['model']['requests']==[] and row['model']['start']==cfg['start'] and row['model']['end']==cfg['end']
        a=CAP/'samples/output'/(name+'.png');assert a.read_bytes()==(CAP/'samples/output'/(name+'-after.png')).read_bytes()
        assert a.read_bytes()==(CAP/'diagnostics/output'/(name+'.png')).read_bytes()==(CAP/'diagnostics/output'/(name+'-after.png')).read_bytes()
        if '-ordinary-regular' in name:
            old=initial[cfg['locale']]['configuration']['id'];assert a.read_bytes()==(CAP/'initial/output'/(old+'.png')).read_bytes()==(CAP/'initial/output'/(old+'-after.png')).read_bytes()
        for index,e in enumerate(row['editors']):
            assert e['date']==cfg['start' if index==0 else 'end']
            assert all(e['source'+k]==e['bare'+k] for k in ['Intrinsic','CellSize','Insets'])
            fields=[{v['name']:v.get('value') for v in f['ivars']} for f in diags[name]['endpoints'][index]['privateSubfields']]
            assert ''.join(f['_stringValue'] for f in fields)==e['candidateText']
            assert e['components']['leapMonth']==('-leap-' in name);endpoint_count+=1
    assert endpoint_count==72
    validation=read(CAP/'validation/output/validation.json');observations=[o for r in validation['rows'] for o in r['observations']]
    assert len(observations)==864 and all(o['matches'] and o['actualCellWidth']==o['predictedCellWidth'] and o['actualIntrinsicWidth']==o['predictedIntrinsicWidth'] for o in observations)
    for row in validation['rows']:
        name=row['configuration']['id'];assert row['originalImagesEqual']
        assert (CAP/'validation/output'/(name+'.png')).read_bytes()==(CAP/'validation/output'/(name+'-after.png')).read_bytes()==(CAP/'samples/output'/(name+'.png')).read_bytes()
    archive=read(CAP/'source-only-artifact.json');assert archive['files']==len(archive['sourceFiles'])==99 and archive['pinnedSourceFiles']==89 and archive['compiledOutputs'] is False
    previous=read(ROOT/'evidence/reference-investigations/date-range-reservation-20261018/source-only-artifact.json')['sourceFiles']
    pinned={k:v for k,v in archive['sourceFiles'].items() if k.startswith('source/')};assert len(pinned)==89 and all(previous[k]==v for k,v in pinned.items())
    replay=read(CAP/'source-only-result.json');assert replay['exitCode']==0 and replay['differences']==[] and replay['outputFiles']==replay['exactOutputs']==153 and not replay['privateDiagnosticsReplayed']
    for folder,row in replay['outputs'].items():
        label={'initial-output':'initial','samples-output':'samples','validation-output':'validation'}[folder];actual={str(p.relative_to(CAP/label/'output')):sha(p) for p in (CAP/label/'output').rglob('*') if p.is_file()};assert row['exact'] and row['sha256']==actual
    assert 'MMMddd -> 正月029' in (CAP/'icu/before/format.log').read_text() and 'MMMddd -> 正月廿九' in (CAP/'icu/after/format.log').read_text()
    print('Chinese source: 72 calibrated endpoints, 864 exact public sizing observations and 153 exact source-only files; acceptance pending')
if __name__=='__main__':verify()
