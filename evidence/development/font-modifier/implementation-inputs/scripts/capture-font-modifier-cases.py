#!/usr/bin/env python3
"""Capture every sealed font caller, baseline-parent and finite-negative context."""
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
CORPORA={'caller':('font-modifier',108),'baseline':('font-baseline',90),'negative':('font-edges',9)}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rows():
    result=[]
    for kind,(name,count) in CORPORA.items():
        directory=ROOT/'evidence/reference-investigations'/f'{name}-20261016'
        sealed=json.loads((directory/'investigation.json').read_text())
        assert sealed['referenceRevision']==REFERENCE and sealed['accepted'] is False
        assert digest(directory/'captures/captures.json')==sealed['files']['captures/captures.json']
        source=json.loads((directory/'captures/captures.json').read_text())
        contexts={(r['configuration']['fixture'],r['appearance'],r['textScale'],r['dpr']) for r in source['captures']}
        fixtures={r['configuration']['fixture'] for r in source['captures']}
        assert source['reference']==REFERENCE and len(fixtures)==source['fixtures']==count
        assert len(contexts)==len(source['captures'])==count*8
        assert contexts==set(itertools.product(fixtures,['light','dark'],[1,1.5],[1,2]))
        for row in source['captures']:
            assert row['publicProbedIdentical'] is True
            name=row['paths'][0];assert digest(directory/'captures'/name)==sealed['files']['captures/'+name]
            definition=dict(row['configuration'],fixture=kind+'-'+row['configuration']['fixture'],api='View.bleeckerFont',source=REFERENCE,
                baselineParent=kind=='baseline',expectedEmpty=row['configuration']['content']=='empty-view')
            result.append(dict(kind=kind,definition=definition,source=row,directory=directory,path=kind+'-'+name))
    assert len(result)==1656 and len({r['path'] for r in result})==1656
    return result

def definitions(corpus=None):
    fixtures={}
    for row in corpus or rows():
        f=row['definition'];name=f['fixture']
        if name in fixtures:assert fixtures[name]==f
        fixtures[name]=f
    assert len(fixtures)==207
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
        assert result.returncode==0,f'Capture failed; retain {output/(name+".log")}'
        log=(output/(name+'.log')).read_text()
        assert not any(message in log for message in ['Unable to assign','QFont::','ReferenceError','TypeError']),f'Capture warning; retain {output/(name+".log")}' 
        meta=json.loads((output/(name+'.json')).read_text())
        assert meta['qt']=='6.8.3' and meta['platform']=='offscreen' and meta['dpr']==source['dpr']
        assert struct.unpack('>II',(output/name).read_bytes()[16:24])==(640*source['dpr'],400*source['dpr'])
        return dict(path=name,sha256=digest(output/name),metadataSha256=digest(output/(name+'.json')))
    records=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        for record in executor.map(one,corpus):
            records.append(record)
            if len(records)%24==0:print(f'Font modifier {len(records)}/1656 captures',flush=True)
    report=dict(reference=REFERENCE,fixtures=207,cases=1656,records=records,accepted=False,catalogSha256=digest(catalog),
        sourceInvestigations={kind:digest(ROOT/'evidence/reference-investigations'/f'{name}-20261016/investigation.json') for kind,(name,_) in CORPORA.items()},
        scope='Complete closed caller, baseline-parent and finite-negative matrix. Strict native pixels/frames and physical/reader acceptance remain separate.')
    (output/'capture-results.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('catalog',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--jobs',type=int,choices=range(1,9),default=1)
    args=parser.parse_args();capture(args.catalog,args.output,args.jobs)
