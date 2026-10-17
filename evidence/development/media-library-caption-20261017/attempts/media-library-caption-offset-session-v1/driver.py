from pathlib import Path
import json,os,subprocess
p=Path('/package');rows=[]
for platform in ['xcb','offscreen']:
 for row in json.loads((p/'phases.json').read_text()):
  command=['install/bin/AvelinoCatalog','--fixture','reference-case','--case',row['definition']['fixture'],'--case-definitions','/package/fixture-inputs.json','--text-scale',str(row['textScale']),'--capture','/package/'+platform+'-'+row['name']+'.png']
  if row['dark']:command.append('--dark')
  with(p/(platform+'-'+row['name']+'.log')).open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,QT_QPA_PLATFORM=platform,QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1',LANG='C.UTF-8'))
  rows.append(dict(platform=platform,phase=row['name'],exitCode=r.returncode));(p/'steps.json').write_text(json.dumps(rows,indent=2)+'\n');assert r.returncode==0,rows[-1]
