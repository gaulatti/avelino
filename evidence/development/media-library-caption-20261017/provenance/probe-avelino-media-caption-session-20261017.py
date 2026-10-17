from pathlib import Path
import json,shutil,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';P=B/'media-library-caption-session-v1';Q=B/'media-library-reflow-operator-v1';assert not P.exists();P.mkdir();shutil.copytree(Q/'install',P/'install')
for n in['phases.json','fixture-inputs.json']:shutil.copy2(Q/n,P/n)
(P/'driver.py').write_text('''from pathlib import Path
import json,os,subprocess
p=Path('/package');rows=[]
for platform in ['xcb','offscreen']:
 for row in json.loads((p/'phases.json').read_text()):
  command=['install/bin/AvelinoCatalog','--fixture','reference-case','--case',row['definition']['fixture'],'--case-definitions','/package/fixture-inputs.json','--text-scale',str(row['textScale']),'--capture','/package/'+platform+'-'+row['name']+'.png']
  if row['dark']:command.append('--dark')
  with(p/(platform+'-'+row['name']+'.log')).open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,QT_QPA_PLATFORM=platform,QT_QUICK_BACKEND='software',QT_SCALE_FACTOR='1',LANG='C.UTF-8'))
  rows.append(dict(platform=platform,phase=row['name'],exitCode=r.returncode));(p/'steps.json').write_text(json.dumps(rows,indent=2)+'\\n');assert r.returncode==0,rows[-1]
''')
(P/'run.sh').write_text('''set -euo pipefail
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp -noreset 3>/package/display >/package/xvfb.log 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true' EXIT
while [[ ! -s /package/display ]]; do kill -0 "$pid";sleep .1;done
export DISPLAY=":$(cat /package/display)"
xdpyinfo >/package/display-info.txt
python3 driver.py
''')
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--name','avelino-media-caption-session-v1','-v',str(P)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','bash','run.sh'];start=time.monotonic()
with(P/'run.log').open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(P/'result.json').write_text(json.dumps(dict(exitCode=r.returncode,command=command,seconds=time.monotonic()-start),indent=2)+'\n');print('Fresh session probe',r.returncode);raise SystemExit(r.returncode)
