from pathlib import Path
import json,subprocess
P=Path(__file__).resolve().parent;BASE=P.parent;ROOT=P.parents[2];RUNTIME=BASE/'button-group-runtime-v2/runtime'
assert json.loads((BASE/'button-group-continuation-v3/result.json').read_text())['exitCode']==0
OUTPUT=P/'output';OUTPUT.mkdir()
definitions=json.loads((RUNTIME/'fixtures.json').read_text());by={r['variant']:r for r in definitions['fixtures']}
cases=[('empty-without-flag','absent',None),('empty-false-flag','absent',False),('nonempty-true-flag','block',True),('nonboolean-flag','block','false')]
rows=[]
for name,variant,flag in cases:
 definition=dict(by[variant]);definition['fixture']='invalid-'+name
 if flag is None:definition.pop('expectedEmpty')
 else:definition['expectedEmpty']=flag
 f=OUTPUT/(name+'.json');f.write_text(json.dumps(dict(fixtures=[definition]),indent=2)+'\n')
 command=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(RUNTIME)+':/package:ro','-v',str(OUTPUT)+':/output','-w','/package','-e','QT_QPA_PLATFORM=offscreen','-e','QT_QUICK_BACKEND=software','sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3','./install/bin/AvelinoCatalog','--fixture','reference-case','--case',definition['fixture'],'--case-definitions','/output/'+f.name,'--capture','/output/'+name+'.png']
 r=subprocess.run(command,capture_output=True,text=True);(P/(name+'.log')).write_text(r.stdout+r.stderr)
 rows.append(dict(name=name,command=command,expectedExitCode=6,actualExitCode=r.returncode,captureCreated=(OUTPUT/(name+'.png')).exists()))
 assert r.returncode==6 and not rows[-1]['captureCreated'],rows[-1]
(P/'result.json').write_text(json.dumps(dict(exitCode=0,rejected=4,rows=rows,accepted=False),indent=2)+'\n')
print('Four invalid expected-empty inputs rejected without captures')
