from pathlib import Path
import json,os,subprocess
p=Path('/package');environment=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1',LANG='C.UTF-8')
for row in json.loads((p/'phases.json').read_text()):
 command=['install/bin/AvelinoCatalog','--fixture','reference-case','--case',row['definition']['fixture'],'--case-definitions','/package/fixture-inputs.json','--text-scale',str(row['textScale']),'--capture','/package/references/'+row['name']+'.png']
 if row['dark']:command.append('--dark')
 with (p/'references'/(row['name']+'.log')).open('w') as log:r=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,(row['name'],r.returncode)
for scale in [1,1.5]:
 command=['install/bin/AvelinoCatalog','--fixture','app-tabs','--text-scale',str(scale),'--capture','/package/references/gallery-text'+str(scale)+'.png']
 with (p/'references'/('gallery-text'+str(scale)+'.log')).open('w') as log:r=subprocess.run(command,env=environment,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,scale
