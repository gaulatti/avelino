#!/usr/bin/env python3
"""Exercise all pill catalog callers and reject malformed fixture definitions."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

catalog, imports, root = map(Path, sys.argv[1:])
projection = json.loads((root/'tests/consumer/native-pill-witnesses.json').read_text())
chosen = [r for r in projection['closed'] if r['appearance']=='light' and r['textScale']==1 and r['dpr']==1]
assert len(chosen)==111
definitions = [dict(r['configuration'], api='Text.bleeckerPill', source=projection['reference'],
    fixture='pill-'+r['configuration']['id'], width=640, height=400) for r in chosen]
with tempfile.TemporaryDirectory(prefix='avelino-pill-catalog-') as temporary:
    directory=Path(temporary);inputs=directory/'fixtures.json';inputs.write_text(json.dumps({'fixtures':definitions},ensure_ascii=False))
    environment=dict(os.environ,QML_IMPORT_PATH=str(imports),QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1')
    def one(definition):
        name=definition['fixture'];image=directory/(name+'.png')
        result=subprocess.run([str(catalog),'--fixture','reference-case','--case',name,'--case-definitions',str(inputs),'--capture',str(image)],env=environment,capture_output=True)
        log=(result.stdout+result.stderr).decode(errors='replace')
        assert result.returncode==0,(name,result.returncode,log)
        assert not any(word in log for word in ['Unable to assign','ReferenceError','TypeError','Error:','QFont::','Binding loop']), (name,log)
        meta=json.loads(Path(str(image)+'.json').read_text())
        assert meta['pillState']==dict(appearances=1,disappearances=0,callerInstances=1), (name,meta['pillState'])
        parts=meta['pillParts'];outer,inner=parts['styled'][0],parts['label'][0]
        assert outer['width']==inner['width']+14 and outer['height']==inner['height']+8,(name,parts)
        assert set(meta['pillBaselines'])==({'root','styled','label','reference'} if definition['parentLayout']=='baseline' else set())
        assert meta['asyncTextResourceChecks']=='passed'
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(one,definitions))
    default=definitions[0]
    invalid=[dict(default,offer=-1),dict(default,offer='35'),dict(default,lineLimit=0),dict(default,lineLimit=1.5),dict(default,lineLimit=2147483648),
        dict(default,parentLayout='grid'),dict(default,style='button'),dict(default,text=[]),dict(default,parentFont=32),dict(default,parentRed='false'),
        dict(default,hidden=1),dict(default,disabled=1),dict(default,rtl=1),dict(default,width=320),dict(default,height=240),dict(default,source='unapproved'),dict(default,id='forged'),dict(default,extra='ignored')]
    for key in default:
        if key=='api':continue
        forged=dict(default);del forged[key];invalid.append(forged)
    for index,forged in enumerate(invalid):
        inputs.write_text(json.dumps({'fixtures':[forged]}))
        result=subprocess.run([str(catalog),'--fixture','reference-case','--case',default['fixture'],'--case-definitions',str(inputs),'--capture',str(directory/f'invalid-{index}.png')],env=environment,capture_output=True)
        assert result.returncode==6,(forged,result.returncode,result.stderr.decode(errors='replace'))
print(f'Pill catalog: 111 retained Text callers, actual padding/baselines and {len(invalid)} malformed definitions checked; native parity separate')
