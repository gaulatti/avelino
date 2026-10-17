#!/usr/bin/env python3
"""Capture all 52 sealed generic surface callers in all eight source contexts."""
import argparse
import concurrent.futures
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REFERENCE='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
DIRECTORY=ROOT/'evidence/reference-investigations/surface-modifier-20261016'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def definition(configuration):
    return dict(configuration,fixture="surface-"+configuration["fixture"],api="BleeckerSurfaceModifier",source=REFERENCE,expectedEmpty=configuration["content"]=="empty")

def verify_capture_log(log):
    assert not any(message in log for message in ["Unable to assign","QFont::","ReferenceError","TypeError","Binding loop"]),"Surface capture contains a Qt binding or font diagnostic"

def rows():
    sealed=json.loads((DIRECTORY/'investigation.json').read_text())
    assert sealed['reference']==REFERENCE and sealed['accepted'] is False
    assert digest(DIRECTORY/'captures/captures.json')==sealed['files']['captures/captures.json']
    source=json.loads((DIRECTORY/'captures/captures.json').read_text())
    fixtures={r['configuration']['fixture'] for r in source['captures']}
    contexts={(r['configuration']['fixture'],r['appearance'],r['textScale'],r['dpr']) for r in source['captures']}
    assert source['reference']==REFERENCE and len(fixtures)==source['fixtures']==52
    assert len(contexts)==len(source['captures'])==416
    assert contexts==set(itertools.product(fixtures,['light','dark'],[1,1.5],[1,2]))
    result=[]
    for row in source['captures']:
        assert row['publicProbedIdentical'] is True and row['publicWitnessIdentical'] is True
        name=row['paths'][0];assert digest(DIRECTORY/'captures'/name)==sealed['files']['captures/'+name]
        assert row['states'][1]['baselines']=={},'Add a measured baseline adapter before extending this centered corpus'
        result.append(dict(definition=definition(row['configuration']),source=row,directory=DIRECTORY,path='surface-'+name))
    assert len({r['path'] for r in result})==416
    return result

def definitions(corpus=None):
    fixtures={}
    for row in corpus or rows():
        f=row['definition'];name=f['fixture']
        if name in fixtures:assert fixtures[name]==f
        fixtures[name]=f
    assert len(fixtures)==52
    return dict(reference=REFERENCE,fixtures=list(fixtures.values()))

def capture(catalog,output,jobs=1):
    catalog,output=Path(catalog).resolve(),Path(output).resolve()
    assert catalog.is_file() and not output.exists(),'Use a new directory and retain earlier attempts'
    corpus=rows();output.mkdir(parents=True)
    inputs=output/'fixture-inputs.json';inputs.write_text(json.dumps(definitions(corpus),indent=2,ensure_ascii=False)+'\n')
    def one(row):
        environment=dict(os.environ)
        for key in ['QML_IMPORT_PATH','QML2_IMPORT_PATH']:environment.pop(key,None)
        source=row['source'];name=row['path']
        environment.update(QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR=str(source['dpr']),LANG='C.UTF-8')
        command=[str(catalog),'--fixture','reference-case','--case',row['definition']['fixture'],'--case-definitions',str(inputs),
            '--text-scale',str(source['textScale']),'--capture',str(output/name)]
        if source['appearance']=='dark':command.append('--dark')
        with (output/(name+'.log')).open('w') as log:result=subprocess.run(command,env=environment,cwd=catalog.parent.parent,stdout=log,stderr=subprocess.STDOUT)
        receipt=dict(command=command,exitCode=result.returncode)
        (output/(name+'.result.json')).write_text(json.dumps(receipt,indent=2)+'\n')
        assert result.returncode==0,f'Capture failed; retain {output/(name+".log")}'
        log=(output/(name+'.log')).read_text()
        verify_capture_log(log)
        meta=json.loads((output/(name+'.json')).read_text())
        assert meta['qt']=='6.8.3' and meta['platform']=='offscreen' and meta['dpr']==source['dpr']
        assert meta['asyncShapeFrameChecks']=='passed'
        assert struct.unpack('>II',(output/name).read_bytes()[16:24])==(640*source['dpr'],400*source['dpr'])
        return dict(path=name,sha256=digest(output/name),metadataSha256=digest(output/(name+'.json')))
    records=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        for record in executor.map(one,corpus):
            records.append(record)
            if len(records)%16==0:print(f'Surface modifier {len(records)}/416 captures',flush=True)
    report=dict(reference=REFERENCE,fixtures=52,cases=416,records=records,accepted=False,catalogSha256=digest(catalog),
        sourceInvestigation=digest(DIRECTORY/'investigation.json'),
        scope='All closed native surface callers; strict pixels/geometry and source baseline/hit-test, physical and reader acceptance remain separate.')
    (output/'capture-results.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('catalog',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--jobs',type=int,choices=range(1,9),default=1)
    args=parser.parse_args();capture(args.catalog,args.output,args.jobs)
