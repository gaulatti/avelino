#!/usr/bin/env python3
"""Exercise the complete surface catalog adapter and malformed definition boundary."""
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
capture=load('surface_catalog_inputs','capture-surface-modifier-cases.py')
compare=load('surface_catalog_observations','surface-modifier-observations.py')
corpus=capture.rows();definitions=capture.definitions(corpus)
with tempfile.TemporaryDirectory(prefix='avelino-surface-catalog-') as temporary:
 directory=Path(temporary);inputs=directory/'fixtures.json';inputs.write_text(json.dumps(definitions,ensure_ascii=False))
 environment=dict(os.environ,QML_IMPORT_PATH=str(imports),QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1')
 chosen=[r for r in corpus if r['source']['appearance']=='light' and r['source']['textScale']==1 and r['source']['dpr']==1]
 def one(row):
  name=row['definition']['fixture'];image=directory/(name+'.png')
  result=subprocess.run([str(catalog),'--fixture','reference-case','--case',name,'--case-definitions',str(inputs),'--capture',str(image)],env=environment,capture_output=True)
  assert result.returncode==0,(name,result.returncode,result.stderr.decode(errors='replace'))
  log=(result.stdout+result.stderr).decode(errors='replace')
  capture.verify_capture_log(log)
  actual=json.loads(Path(str(image)+'.json').read_text());observations=compare.observations(row,actual)
  assert observations['stateStatus']=='passed',(name,observations['stateErrors'])
  assert isinstance(actual['surfaceModifierParts'],dict) and isinstance(actual['surfaceModifierBaselines'],dict)
  assert len(actual['renderedCallerObjects'])==(0 if row['definition']['content']=='empty' else 2 if row['definition']['content']=='multi' else 1)
  if row['definition']['content'] in ['clear','rectangle','fractional','opaque','overflow','hidden','empty','zero','wide','multi','hstack','vstack']:assert observations['partFramesStatus']=='passed',(name,observations)
  if name=='surface-rtl':
   reference=row['directory']/'captures'/row['source']['paths'][0]
   for x,y in [(280,180),(360,180),(280,220),(360,220)]:
    def sample(path):return subprocess.check_output(['convert',str(path),'-crop',f'1x1+{x}+{y}','-depth','8','RGBA:-'])
    expected,rendered=sample(reference),sample(image)
    assert len(expected)==len(rendered)==4 and expected==rendered,('RTL semantic corner',x,y,expected,rendered)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(one,chosen))
 default=definitions['fixtures'][0]
 invalid=[dict(default,radius="12"),dict(default,radius=0,resolvedRadius=12),dict(default,resolvedRadius=0),dict(default,offer=-1),
  dict(default,parentLayout='grid'),dict(default,content='unknown'),dict(default,parentFont=32),dict(default,parentRed='false'),
  dict(default,rtl=1),dict(default,expectedEmpty=True),dict(default,text=[]),dict(default,width=320),dict(default,height=240),dict(default,source='unapproved'),dict(default,extra='ignored')]
 for key in ['radius','resolvedRadius','offer','content','parentFont','parentRed','rtl','expectedEmpty']:
  forged=dict(default);del forged[key];invalid.append(forged)
 for index,forged in enumerate(invalid):
  inputs.write_text(json.dumps({'fixtures':[forged]}))
  result=subprocess.run([str(catalog),'--fixture','reference-case','--case',forged['fixture'],'--case-definitions',str(inputs),'--capture',str(directory/f'invalid-{index}.png')],env=environment,capture_output=True)
  assert result.returncode==6,(forged,result.returncode,result.stderr)
print('Surface catalog: 52 actual caller states, complete frame metadata and explicitly unrequested baselines and 23 malformed definitions checked; strict pixels/geometry separate')
