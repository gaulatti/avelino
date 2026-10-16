#!/usr/bin/env python3
"""Preserve original-size closed Tooltip captures from an installed catalog."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/reference-investigations/tooltip-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def definitions(source):
    rows = source['captures']
    fixtures = {r['configuration']['fixture'] for r in rows}
    contexts = {(r['configuration']['fixture'],r['appearance'],r['textScale'],r['dpr']) for r in rows}
    assert source['reference'] == REFERENCE and source['fixtures'] == len(fixtures) == 21
    assert len(rows) == len(contexts) == 168
    assert contexts == set(itertools.product(fixtures,['light','dark'],[1,1.5],[1,2]))
    byname = {}
    for row in rows:
        assert all(row[k] for k in ['publicProbedIdentical','publicWitnessIdentical','publicUnwrappedIdentical'])
        definition = dict(row['configuration'])
        definition.update(api='BleeckerTooltip',source=REFERENCE,helpAttached=True,
                          expectedEmpty=definition['content'] in ['empty','zero','hidden'],
                          variant='default',text=definition['hint'],value=0,size='md',flag=False)
        name = definition['fixture']
        if name in byname:
            assert byname[name] == definition
        byname[name] = definition
    return {'reference':REFERENCE,'fixtures':list(byname.values())}

def capture(catalog, output):
    catalog,output=Path(catalog).resolve(),Path(output).resolve()
    assert catalog.is_file() and not output.exists(), 'Catalog required; preserve every previous output attempt'
    output.mkdir(parents=True);(output/'bare').mkdir()
    report=json.loads((SOURCE/'investigation.json').read_text())
    assert report['referenceRevision']==REFERENCE and digest(SOURCE/'closed/captures.json')==report['files']['closed/captures.json']
    source=json.loads((SOURCE/'closed/captures.json').read_text());inputs=definitions(source)
    for name,bare in [('fixture-inputs.json',False),('bare-inputs.json',True)]:
        data={'reference':REFERENCE,'fixtures':[{**d,'helpAttached':not bare} for d in inputs['fixtures']]}
        (output/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    records=[]
    for row in source['captures']:
        name=row['paths'][0];configuration=row['configuration']
        for path in row['paths']:
            assert digest(SOURCE/'closed'/path)==report['files']['closed/'+path]
        environment=dict(os.environ)
        for key in ['QML_IMPORT_PATH','QML2_IMPORT_PATH']:environment.pop(key,None)
        environment.update(QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR=str(row['dpr']),LANG='C.UTF-8')
        for bare in [False,True]:
            directory=output/'bare' if bare else output
            command=[str(catalog),'--fixture','reference-case','--case',configuration['fixture'],'--case-definitions',str(output/('bare-inputs.json' if bare else 'fixture-inputs.json')),'--text-scale',str(row['textScale']),'--capture',str(directory/name)]
            if row['appearance']=='dark':command.append('--dark')
            with (directory/(name+'.log')).open('w') as log:
                result=subprocess.run(command,env=environment,cwd=catalog.parent.parent.parent,stdout=log,stderr=subprocess.STDOUT)
            assert result.returncode==0, f'Capture failed; retain {directory/(name+".log")}'
            data=json.loads((directory/(name+'.json')).read_text())
            assert struct.unpack('>II',(directory/name).read_bytes()[16:24])==(640*row['dpr'],400*row['dpr'])
            assert data['platform']=='offscreen' and data['qt']=='6.8.3' and data['dpr']==row['dpr']
            assert data['tooltipVisible'] is False and data['helpAttached'] is not bare
        identical=(output/name).read_bytes()==(output/'bare'/name).read_bytes()
        assert identical, 'The attached help adapter changed closed body pixels'
        records.append({'path':name,'sha256':digest(output/name),'metadataSha256':digest(output/(name+'.json')),
                        'bareSha256':digest(output/'bare'/name),'bareMetadataSha256':digest(output/'bare'/(name+'.json')),
                        'adapterBodyIdentical':identical})
    (output/'capture-results.json').write_text(json.dumps({'reference':REFERENCE,'fixtures':21,'cases':168,'records':records,
        'accepted':False,'catalogSha256':digest(catalog),'sourceInvestigationSha256':digest(SOURCE/'investigation.json'),
        'captureScope':'Closed body only; installed catalog without QML import overrides; original physical pixels retained'},indent=2)+'\n')
    print('168 installed closed Tooltip captures; all attached/bare pairs byte-identical')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('catalog',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();capture(args.catalog,args.output)
