from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import time

root=Path('/Users/gaulatti/source/gaulatti/avelino')
base=root/'artifacts/resumed-avelino-20261016'
name=sys.argv[1]
attempt=base/name;assert not attempt.exists();attempt.mkdir()
cache=base/(sys.argv[3] if len(sys.argv)>3 else 'surface-matrix-package-v3')
install=Path(sys.argv[2]) if len(sys.argv)>2 else cache/'install'
shutil.copytree(root/'tests/consumer',attempt/'consumer',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(install,attempt/'install')
shutil.copytree(cache/'consumer-build',attempt/'consumer-build',ignore=shutil.ignore_patterns('Testing'))
snapshot={str(p.relative_to(attempt)):hashlib.sha256(p.read_bytes()).hexdigest()
          for directory in ['consumer','install'] for p in (attempt/directory).rglob('*') if p.is_file()}
(attempt/'inputs.json').write_text(json.dumps(snapshot,indent=2)+'\n')
(attempt/'results').mkdir()
runner='''from pathlib import Path
import json,os,subprocess,time
p=Path('/package');rows=[]
commands=[['cmake','-S','consumer','-B','consumer-build','-G','Ninja','-DCMAKE_PREFIX_PATH=/package/install;/opt/qt'],
 ['cmake','--build','consumer-build','--parallel','2'],
 ['consumer-build/InstalledConsumer','--charts','--charts-observe','--charts-report','/package/results/charts'],
 ['consumer-build/InstalledConsumer','--surface-modifier'],
 ['consumer-build/InstalledConsumer','--font-modifier']]
for i,c in enumerate(commands):
 start=time.monotonic()
 with (p/f'{i}.log').open('w') as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software'))
 rows.append(dict(command=c,exitCode=r.returncode,seconds=time.monotonic()-start,log=f'{i}.log'))
 (p/'steps.json').write_text(json.dumps(rows,indent=2)+'\\n');print(i,r.returncode,flush=True)
 if i<2 and r.returncode:raise SystemExit(r.returncode)
raise SystemExit(1 if any(r['exitCode'] for r in rows) else 0)
'''
(attempt/'run.py').write_text(runner)
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-'+name,
 '-v',str(attempt)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','python3','run.py']
start=time.monotonic()
with (attempt/'run.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(attempt/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n')
print(name,r.returncode)
print((attempt/'run.log').read_text()[-1500:])
raise SystemExit(r.returncode)
