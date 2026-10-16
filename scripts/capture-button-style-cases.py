#!/usr/bin/env python3
"""Capture the complete pinned ButtonStyle matrix without resizing its pixels."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'evidence/reference-investigations/button-style-20261016'
REFERENCE='fe8a1d462fbd793d883fb92086a16aa2947e32c9'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def definitions(source):
    rows=source['captures'];fixtures={r['configuration']['fixture'] for r in rows}
    contexts={(r['configuration']['fixture'],r['appearance'],r['textScale'],r['dpr']) for r in rows}
    assert source['reference']==REFERENCE and source['fixtures']==len(fixtures)==88
    assert len(rows)==len(contexts)==704
    assert contexts==set(itertools.product(fixtures,['light','dark'],[1,1.5],[1,2]))
    result={}
    for row in rows:
        assert row['publicProbedIdentical'] and row['publicWitnessIdentical']
        definition={**row['configuration'],'api':'BleeckerButtonStyle','source':REFERENCE,
                    'value':0,'flag':False,'expectedEmpty':row['configuration']['content']=='empty'}
        name=definition['fixture']
        if name in result:assert result[name]==definition
        result[name]=definition
    return {'reference':REFERENCE,'fixtures':list(result.values())}

def capture(catalog,output):
    catalog,output=Path(catalog).resolve(),Path(output).resolve()
    assert catalog.is_file() and not output.exists(),'Use a new output directory; preserve prior attempts'
    output.mkdir(parents=True)
    report=json.loads((SOURCE/'investigation.json').read_text())
    assert report['referenceRevision']==REFERENCE and digest(SOURCE/'captures/captures.json')==report['files']['captures/captures.json']
    source=json.loads((SOURCE/'captures/captures.json').read_text())
    inputs=output/'fixture-inputs.json';inputs.write_text(json.dumps(definitions(source),indent=2,ensure_ascii=False)+'\n')
    records=[]
    for row in source['captures']:
        name=row['paths'][0]
        for path in row['paths']:assert digest(SOURCE/'captures'/path)==report['files']['captures/'+path]
        environment=dict(os.environ)
        for key in ['QML_IMPORT_PATH','QML2_IMPORT_PATH']:environment.pop(key,None)
        environment.update(QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR=str(row['dpr']),LANG='C.UTF-8')
        command=[str(catalog),'--fixture','reference-case','--case',row['configuration']['fixture'],
                 '--case-definitions',str(inputs),'--text-scale',str(row['textScale']),'--capture',str(output/name)]
        if row['appearance']=='dark':command.append('--dark')
        with (output/(name+'.log')).open('w') as log:
            result=subprocess.run(command,env=environment,cwd=catalog.parent.parent,stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0,f'Capture failed: retain {output/(name+".log")}'
        meta=json.loads((output/(name+'.json')).read_text())
        assert struct.unpack('>II',(output/name).read_bytes()[16:24])==(640*row['dpr'],400*row['dpr'])
        assert meta['qt']=='6.8.3' and meta['platform']=='offscreen' and meta['dpr']==row['dpr']
        records.append(dict(path=name,sha256=digest(output/name),metadataSha256=digest(output/(name+'.json'))))
        if len(records)%16==0:print(f'ButtonStyle {len(records)}/704 captures',flush=True)
    (output/'capture-results.json').write_text(json.dumps(dict(reference=REFERENCE,fixtures=88,cases=704,
        records=records,accepted=False,catalogSha256=digest(catalog),sourceInvestigationSha256=digest(SOURCE/'investigation.json'),
        scope='Original-size installed-catalog closed bodies and actual per-part frames; strict comparison and session acceptance separate'),indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('catalog',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();capture(args.catalog,args.output)
