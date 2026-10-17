#!/usr/bin/env python3
"""Capture all supplemental native chart inputs through the installed catalog."""
import argparse
import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
source=module('chart_geometry_native','verify-chart-geometry-source.py')
inputs=module('chart_geometry_canonical','capture-charts.py')
def rows():
    return [dict(r,path=r['group']+'-'+r['configuration']['id']+'-dpr'+f'{r["dpr"]:g}'+'.png',reference=str((source.DIRECTORY/r['group']/r['paths'][0]).relative_to(ROOT))) for r in source.contexts()]
def capture(catalog,output,jobs):
    catalog,output=Path(catalog).resolve(),Path(output).resolve();assert catalog.is_file() and not output.exists();output.mkdir(parents=True)
    corpus=rows();definitions={}
    for row in corpus:
        f=row['configuration'];definition=dict(f,api=inputs.APIS[f['kind']],fixture='chart-'+f['id'],source=inputs.REFERENCE,chartWidth=f['width'],chartHeight=f['height'],width=640,height=400)
        if f['id'] in definitions:assert definition==definitions[f['id']]
        definitions[f['id']]=definition
    assert len(definitions)==45
    config=output/'definitions.json';config.write_text(json.dumps(dict(fixtures=list(definitions.values())),indent=2,ensure_ascii=False)+'\n')
    def one(row):
        path=output/row['path'];f=row['configuration'];definition=definitions[f['id']]
        command=[str(catalog),'--fixture','reference-case','--case',definition['fixture'],'--case-definitions',str(config),'--text-scale','1','--capture',str(path)]
        environment=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR=str(row['dpr']),LANG='C.UTF-8')
        for key in ['QML_IMPORT_PATH','QML2_IMPORT_PATH']:environment.pop(key,None)
        start=time.monotonic()
        with (output/(row['path']+'.log')).open('w') as log:r=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT)
        log=(output/(row['path']+'.log')).read_text();assert r.returncode==0,(row['path'],r.returncode,log)
        assert not any(word in log for word in ['Unable to assign','ReferenceError','TypeError','Error:','QFont::','Binding loop']),log
        meta=json.loads(Path(str(path)+'.json').read_text())
        assert meta['qt']=='6.8.3' and meta['platform']=='offscreen' and meta['dpr']==row['dpr']
        assert meta['width']==640 and meta['height']==400
        assert struct.unpack('>II',path.read_bytes()[16:24])==(640*row['dpr'],400*row['dpr'])
        assert meta['chartMetrics']['kind']==f['kind'] and meta['chartMetrics']['nativeRasterAcceptance']=='pending'
        assert meta['chartState']==dict(appearances=1,disappearances=0,wrapperInstances=1)
        metadata=dict(qt=meta['qt'],platform=meta['platform'],width=640,height=400,dpr=row['dpr'],appearance='light',textScale=1,api=definition['api'],fixture=row['path'],source=inputs.REFERENCE,accepted=False,configuration=f,frame=meta['chartFrame'],metrics=meta['chartMetrics'],state=meta['chartState'],catalogMetadata=meta)
        Path(str(path)+'.json').write_text(json.dumps(metadata,indent=2,ensure_ascii=False)+'\n')
        return dict(path=row['path'],sha256=inputs.digest(path),metadataSha256=inputs.digest(Path(str(path)+'.json')),command=command,exitCode=r.returncode,seconds=time.monotonic()-start)
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:records=list(pool.map(one,corpus))
    assert len(records)==125
    report=dict(reference=inputs.REFERENCE,accepted=False,cases=125,catalogSha256=inputs.digest(catalog),records=records,scope='Every supplemental tiny-frame, requested-DPR and categorical/legend input; strict native comparison and physical acceptance remain separate.')
    (output/'capture-results.json').write_text(json.dumps(report,indent=2)+'\n');print('Installed supplemental charts: 125 cases; native acceptance pending')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('catalog',type=Path);parser.add_argument('output',type=Path);parser.add_argument('--jobs',type=int,choices=range(1,9),default=2);args=parser.parse_args();capture(args.catalog,args.output,args.jobs)
