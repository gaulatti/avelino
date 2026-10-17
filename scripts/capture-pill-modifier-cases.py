#!/usr/bin/env python3
"""Capture every public/bare pill context and every retained history step."""
import argparse
import concurrent.futures
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
REFERENCE='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
PROJECTION=ROOT/'tests/consumer/native-pill-witnesses.json'
CONTEXTS=list(itertools.product(['light','dark'],[1,1.5],[1,2]))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prefix(appearance,scale,dpr):return f'{appearance}-text{scale:g}-dpr{dpr:g}'
def report_path(prefix):return Path(str(prefix)+'.json')
def verify_capture_log(log):
    assert not any(word in log for word in ['Unable to assign','ReferenceError','TypeError','Error:','QFont::','Binding loop','Could not find any constructor']),log[-4000:]
def rows(projection=None):
    data=projection if projection is not None else json.loads(PROJECTION.read_text())
    assert data['reference']==REFERENCE and data['accepted'] is False
    assert len(data['closed'])==888 and len(data['histories'])==56
    result=[]
    for row in data['closed']:
        context=prefix(row['appearance'],row['textScale'],row['dpr']);configuration=row['configuration']
        for mode in [0,3]:
            expected=row if mode==0 else row['bare']
            result.append(dict(kind='public' if mode==0 else 'bare',context=context,mode=mode,configuration=configuration,
                appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],parts=expected['parts'],guides=expected['guides'],
                reference=expected['reference'],path=f'{context}-{configuration["id"]}-mode{mode}.png'))
    for row in data['histories']:
        context=prefix(row['appearance'],row['textScale'],row['dpr'])
        assert [s['step'] for s in row['steps']]==['initial','text','appearance','text-scale','direction','restore']
        for index,step in enumerate(row['steps']):
            result.append(dict(kind='history',context=context,step=index,configuration=step['configuration'],
                appearance=step['appearance'],textScale=step['textScale'],dpr=row['dpr'],parts=step['parts'],guides=step['guides'],
                reference=step['reference'],path=f'{context}-{row["configuration"]["id"]}-history-step{index}.png'))
    assert len(result)==len({r['path'] for r in result})==2112
    assert {r['context'] for r in result}=={prefix(*c) for c in CONTEXTS}
    assert all(sum(r['context']==prefix(*c) for r in result)==264 for c in CONTEXTS)
    for row in result:assert (ROOT/row['reference']).is_file()
    return result
def observations(expected,actual):
    errors={}
    for key in ['configuration','appearance','textScale','dpr','kind']:
        if actual.get(key)!=expected[key]:errors[key]=dict(reference=expected[key],candidate=actual.get(key))
    if actual.get('state')!=dict(appearances=1,disappearances=0,callerInstances=1):errors['state']=actual.get('state')
    if expected['kind']=='history' and expected['step']==5 and actual.get('restoredInitialPixelsAndGeometry') is not True:
        errors['restoredInitialPixelsAndGeometry']=actual.get('restoredInitialPixelsAndGeometry')
    return dict(partFramesStatus='passed' if actual.get('parts')==expected['parts'] else 'failed',
        baselineStatus='passed' if actual.get('guides')==expected['guides'] else 'failed',
        stateStatus='failed' if errors else 'passed',stateErrors=errors,
        referenceParts=expected['parts'],candidateParts=actual.get('parts'),referenceGuides=expected['guides'],candidateGuides=actual.get('guides'))
def capture(consumer,output,jobs=1):
    consumer,output=Path(consumer).resolve(),Path(output).resolve()
    assert consumer.is_file() and not output.exists(),'Use a new output and preserve earlier attempts'
    corpus=rows();output.mkdir(parents=True)
    def one(context):
        appearance,scale,dpr=context;name=prefix(*context);target=output/name
        environment=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR=str(dpr),LANG='C.UTF-8')
        for key in ['QML_IMPORT_PATH','QML2_IMPORT_PATH']:environment.pop(key,None)
        command=[str(consumer),'--pill-modifier','--pill-observe','--text-scale',str(scale),'--pill-report',str(target)]
        if appearance=='dark':command.append('--dark')
        start=time.monotonic()
        with (output/(name+'.log')).open('w') as log:result=subprocess.run(command,cwd=consumer.parent,env=environment,stdout=log,stderr=subprocess.STDOUT)
        receipt=dict(command=command,exitCode=result.returncode,seconds=time.monotonic()-start,log=name+'.log')
        (output/(name+'-process.json')).write_text(json.dumps(receipt,indent=2)+'\n')
        assert result.returncode==0,(name,result.returncode)
        verify_capture_log((output/(name+'.log')).read_text())
        report=json.loads(report_path(target).read_text())
        assert report['qt']=='6.8.3' and report['platform']=='offscreen' and report['dpr']==dpr
        assert report['width']==640 and report['height']==400 and report['structuralChecks']=='passed' and report['accepted'] is False
        actual={}
        for row in report['rows']:
            for mode in row['modes']:
                path=f'{name}-{row["configuration"]["id"]}-mode{mode["mode"]}.png'
                assert path not in actual
                actual[path]=dict(mode,configuration=row['configuration'],appearance=appearance,textScale=scale,kind='public' if mode['mode']==0 else 'bare')
        for history in report['histories']:
            assert len(history['steps'])==6
            for index,step in enumerate(history['steps']):
                path=f'{name}-{history["configuration"]["id"]}-history-step{index}.png'
                assert path not in actual
                actual[path]=dict(step,kind='history')
        expected={r['path']:r for r in corpus if r['context']==name}
        assert actual.keys()==expected.keys() and len(actual)==264
        records=[]
        for path,value in actual.items():
            value.update(qt=report['qt'],platform=report['platform'],width=640,height=400,dpr=dpr,api='Text.bleeckerPill',fixture=path,
                source=REFERENCE,accepted=False)
            assert observations(expected[path],value)['stateStatus']=='passed',(path,observations(expected[path],value)['stateErrors'])
            image=output/path
            assert struct.unpack('>II',image.read_bytes()[16:24])==(640*dpr,400*dpr)
            metadata=output/(path+'.json');metadata.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
            records.append(dict(path=path,sha256=digest(image),metadataSha256=digest(metadata)))
        print(f'Pill {name}: 264 displayed measurements and images',flush=True)
        return dict(context=name,process=receipt,records=records)
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:contexts=list(pool.map(one,CONTEXTS))
    assert sum(len(r['records']) for r in contexts)==2112
    report=dict(reference=REFERENCE,accepted=False,cases=2112,closedContexts=888,histories=56,contexts=contexts,
        consumerSha256=digest(consumer),projectionSha256=digest(PROJECTION),scope='Every public/bare context and all six steps of every retained history. Strict reference comparison remains separate.')
    (output/'capture-results.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('consumer',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--jobs',type=int,choices=range(1,9),default=1);args=parser.parse_args();capture(args.consumer,args.output,args.jobs)
