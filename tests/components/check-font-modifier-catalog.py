#!/usr/bin/env python3
"""Exercise the complete font catalog adapter and malformed definition boundary."""
import concurrent.futures
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
catalog,imports,root=map(Path,sys.argv[1:])
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,root/'scripts'/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
capture=load('font_catalog_inputs','capture-font-modifier-cases.py')
compare=load('font_catalog_observations','font-modifier-observations.py')
corpus=capture.rows();definitions=capture.definitions(corpus)
with tempfile.TemporaryDirectory(prefix='avelino-font-catalog-') as temporary:
 directory=Path(temporary);inputs=directory/'fixtures.json';inputs.write_text(json.dumps(definitions,ensure_ascii=False))
 environment=dict(os.environ,QML_IMPORT_PATH=str(imports),QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1')
 chosen=[r for r in corpus if r['source']['appearance']=='light' and r['source']['textScale']==1 and r['source']['dpr']==1]
 def one(row):
  name=row['definition']['fixture'];image=directory/(name+'.png')
  result=subprocess.run([str(catalog),'--fixture','reference-case','--case',name,'--case-definitions',str(inputs),'--capture',str(image)],env=environment,capture_output=True)
  assert result.returncode==0,(name,result.returncode,result.stderr.decode(errors='replace'))
  log=(result.stdout+result.stderr).decode(errors='replace')
  assert not any(message in log for message in ['Unable to assign','QFont::','ReferenceError','TypeError']), (name,log)
  actual=json.loads(Path(str(image)+'.json').read_text());observations=compare.observations(row,actual)
  assert observations['stateStatus']=='passed',(name,observations['stateErrors'])
  assert isinstance(actual['fontModifierParts'],dict) and isinstance(actual['fontModifierBaselines'],dict)
  assert len(actual['renderedCallerObjects'])==(0 if row['definition']['content']=='empty-view' else 2 if row['definition']['content']=='multi' else 1)
  if name=='caller-primary-regular':assert observations['partFramesStatus']=='passed',observations
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(one,chosen))
 default=definitions['fixtures'][0]
 invalid=[dict(default,family='unknown'),dict(default,weight='unknown'),dict(default,size='14'),dict(default,offer=-1),
  dict(default,parentLayout='grid'),dict(default,content='unknown'),dict(default,parentFont=32),dict(default,outerSystem='false'),
  dict(default,outerFontModifier=None),dict(default,rtl=1),dict(default,baselineParent='false'),dict(default,expectedEmpty=True),
  dict(default,text=[]),dict(default,width=320),dict(default,height=240),dict(default,source='unapproved')]
 for key in ['size','weight','offer','content','baselineParent']:
  forged=dict(default);del forged[key];invalid.append(forged)
 for index,forged in enumerate(invalid):
  inputs.write_text(json.dumps({'fixtures':[forged]}))
  result=subprocess.run([str(catalog),'--fixture','reference-case','--case',forged['fixture'],'--case-definitions',str(inputs),'--capture',str(directory/f'invalid-{index}.png')],env=environment,capture_output=True)
  assert result.returncode==6,(forged,result.returncode,result.stderr)
print('Font catalog: 207 actual caller states, complete frame/baseline metadata and 21 malformed definitions checked; strict pixels/geometry separate')
