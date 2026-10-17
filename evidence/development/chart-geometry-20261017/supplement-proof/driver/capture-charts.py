#!/usr/bin/env python3
"""Capture all five chart families, non-finite inputs and retained histories."""
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
PROJECTION=ROOT/'tests/consumer/native-chart-witnesses.json'
CONTEXTS=list(itertools.product(['light','dark'],[1,1.5],[1,2]))
APIS=dict(line='BleeckerLineChart',bar='BleeckerBarChart',pie='BleeckerPieChart',scatter='BleeckerScatterChart',sparkline='BleeckerSparkline')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prefix(appearance,scale,dpr):return f'{appearance}-text{scale:g}-dpr{dpr:g}'
def subset(actual,expected):
    if isinstance(expected,dict):return isinstance(actual,dict) and all(k in actual and subset(actual[k],v) for k,v in expected.items())
    if isinstance(expected,list):return isinstance(actual,list) and len(actual)==len(expected) and all(subset(a,e) for a,e in zip(actual,expected))
    if isinstance(actual,bool) or isinstance(expected,bool):return type(actual)==type(expected) and actual==expected
    return actual==expected
def rows(projection=None):
    data=projection if projection is not None else json.loads(PROJECTION.read_text())
    assert data['reference']==REFERENCE and data['accepted'] is False
    assert len(data['closed'])==960 and len(data['histories'])==48 and len(data['edges'])==400
    result=[]
    for kind in ['closed','edges']:
        for row in data[kind]:
            context=prefix(row['appearance'],row['textScale'],row['dpr']);f=row['configuration']
            frame=row.get('frame',dict(x=(640-max(1,f['width']))/2,y=(400-max(1,f['height']))/2,width=max(1,f['width']),height=max(1,f['height'])))
            result.append(dict(kind='edge' if kind=='edges' else 'closed',context=context,configuration=f,
                appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],frame=frame,metrics=row.get('metrics'),
                reference=row['reference'],path=f'{context}-'+('edge-' if kind=='edges' else '')+f['id']+'.png'))
    for row in data['histories']:
        context=prefix(row['appearance'],row['textScale'],row['dpr'])
        assert [s['step'] for s in row['steps']]==['initial','data','size','appearance','text-scale','direction','disabled','restore']
        for index,step in enumerate(row['steps']):
            result.append(dict(kind='history',context=context,step=index,configuration=step['configuration'],
                appearance=step['appearance'],textScale=step['textScale'],dpr=row['dpr'],frame=step['frame'],metrics=step['metrics'],
                reference=step['reference'],path=f'{context}-{row["configuration"]["id"]}-history-step{index}.png'))
    assert len(result)==len({r['path'] for r in result})==1744
    assert {r['context'] for r in result}=={prefix(*c) for c in CONTEXTS}
    assert all(sum(r['context']==prefix(*c) for r in result)==218 for c in CONTEXTS)
    for row in result:assert (ROOT/row['reference']).is_file()
    return result
def observations(expected,actual):
    errors={}
    for key in ['configuration','appearance','textScale','dpr','kind']:
        if actual.get(key)!=expected[key]:errors[key]=dict(reference=expected[key],candidate=actual.get(key))
    if actual.get('state')!=dict(appearances=1,disappearances=0,wrapperInstances=1):errors['state']=actual.get('state')
    if expected['kind']=='history' and expected['step']==7 and actual.get('restoredInitialPixelsAndGeometry') is not True:
        errors['restoredInitialPixelsAndGeometry']=actual.get('restoredInitialPixelsAndGeometry')
    frame=actual.get('frame')==expected['frame']
    metrics='unobserved' if expected['metrics'] is None else 'passed' if subset(actual.get('metrics'),expected['metrics']) else 'failed'
    return dict(layoutStatus='passed' if frame else 'failed',nativeFrameStatus='unobserved' if expected['kind']=='edge' else 'passed' if frame else 'failed',
        nativeMetricsStatus=metrics,stateStatus='failed' if errors else 'passed',stateErrors=errors,
        referenceFrame=expected['frame'],candidateFrame=actual.get('frame'),referenceMetrics=expected['metrics'],candidateMetrics=actual.get('metrics'))
def capture(consumer,output,jobs=1):
    consumer,output=Path(consumer).resolve(),Path(output).resolve()
    assert consumer.is_file() and not output.exists(),'Use a new output and preserve earlier attempts'
    corpus=rows();output.mkdir(parents=True)
    def one(context):
        appearance,scale,dpr=context;name=prefix(*context);target=output/name
        environment=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR=str(dpr),LANG='C.UTF-8')
        for key in ['QML_IMPORT_PATH','QML2_IMPORT_PATH']:environment.pop(key,None)
        command=[str(consumer),'--charts','--charts-observe','--text-scale',str(scale),'--charts-report',str(target)]
        if appearance=='dark':command.append('--dark')
        start=time.monotonic()
        with (output/(name+'.log')).open('w') as log:result=subprocess.run(command,cwd=consumer.parent,env=environment,stdout=log,stderr=subprocess.STDOUT)
        receipt=dict(command=command,exitCode=result.returncode,seconds=time.monotonic()-start,log=name+'.log')
        (output/(name+'-process.json')).write_text(json.dumps(receipt,indent=2)+'\n')
        assert result.returncode==0,(name,result.returncode)
        log=(output/(name+'.log')).read_text()
        assert not any(word in log for word in ['Unable to assign','ReferenceError','TypeError','Error:','QFont::','Binding loop','Could not find any constructor']),log[-4000:]
        report=json.loads(Path(str(target)+'.json').read_text())
        assert report['qt']=='6.8.3' and report['platform']=='offscreen' and report['dpr']==dpr
        assert report['width']==640 and report['height']==400 and report['structuralChecks']=='passed' and report['accepted'] is False
        assert report['inputContexts']==10 and report['qtAccessibilityChecks'].startswith('passed') and report['inputChecks'].startswith('passed')
        actual={}
        for kind,key in [('closed','closed'),('edge','edges')]:
            for row in report[key]:
                path=f'{name}-'+('edge-' if kind=='edge' else '')+row['configuration']['id']+'.png'
                assert path not in actual;actual[path]=dict(row,appearance=appearance,textScale=scale,kind=kind)
        for history in report['histories']:
            assert len(history['steps'])==8
            for index,step in enumerate(history['steps']):
                path=f'{name}-{history["configuration"]["id"]}-history-step{index}.png'
                assert path not in actual;actual[path]=dict(step,kind='history')
        expected={r['path']:r for r in corpus if r['context']==name}
        assert actual.keys()==expected.keys() and len(actual)==218
        records=[]
        for path,value in actual.items():
            value.update(qt=report['qt'],platform=report['platform'],width=640,height=400,dpr=dpr,
                api=APIS[value['configuration']['kind']],fixture=path,source=REFERENCE,accepted=False)
            assert observations(expected[path],value)['stateStatus']=='passed',(path,observations(expected[path],value)['stateErrors'])
            image=output/path
            assert struct.unpack('>II',image.read_bytes()[16:24])==(640*dpr,400*dpr)
            metadata=output/(path+'.json');metadata.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
            records.append(dict(path=path,sha256=digest(image),metadataSha256=digest(metadata)))
        print(f'Charts {name}: 218 displayed observations and images',flush=True)
        return dict(context=name,process=receipt,records=records)
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:contexts=list(pool.map(one,CONTEXTS))
    assert sum(len(r['records']) for r in contexts)==1744
    report=dict(reference=REFERENCE,accepted=False,cases=1744,closedContexts=960,edgeContexts=400,histories=48,contexts=contexts,
        consumerSha256=digest(consumer),projectionSha256=digest(PROJECTION),scope='Every closed/edge context and all eight steps of every retained history. Strict native comparison remains separate; bar NaN initialization is unresolved.')
    (output/'capture-results.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('consumer',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--jobs',type=int,choices=range(1,9),default=1);args=parser.parse_args();capture(args.consumer,args.output,args.jobs)
