from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016';p=base/'media-library-package-final-v2';assert not p.exists();p.mkdir();cache=base/'media-library-package-final-v1'
assert json.loads((cache/'result.json').read_text())['exitCode']==0
for name in ['consumer','consumer-build']:shutil.copytree(cache/name,p/name)
shutil.copytree(root/'tests/consumer',p/'consumer',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(base/'media-library-build-v9/install',p/'install')
for name in ['check-installed.sh','check-installed-catalog.sh']:shutil.copy2(root/'scripts'/name,p/name)
shutil.copy2(base/'surface-matrix-package-v3/environment.json',p/'environment.json')
shutil.copy2('/Users/gaulatti/.codex/tmp/collect-avelino-charts-environment-20261017.py',p/'collect-environment.py')
script=root/'scripts/capture-media-library.py';spec=importlib.util.spec_from_file_location('chart_capture',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
paths={'scripts/capture-media-library.py','tests/consumer/native-media-library-witnesses.json'}|{r['reference'] for r in m.rows()}
for name in paths:
 target=p/'driver'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,target)
digest=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
(p/'inputs.json').write_text(json.dumps({str(f.relative_to(p)):digest(f) for directory in ['consumer','install','driver'] for f in (p/directory).rglob('*') if f.is_file()},indent=2)+'\n')
runner="""from pathlib import Path
import json,os,subprocess,time
p=Path('/package');rows=[]
commands=[(['bash','check-installed.sh'],0),(['python3','driver/scripts/capture-media-library.py','consumer-build/InstalledConsumer','captures','--jobs','2'],0),(['consumer-build/InstalledConsumer','--media-library','--media-library-report','/package/strict'],1)]
for i,(command,expected) in enumerate(commands):
 start=time.monotonic()
 with (p/f'{i}.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software'))
 rows.append(dict(command=command,exitCode=r.returncode,expectedExitCode=expected,seconds=time.monotonic()-start,log=f'{i}.log'))
 (p/'steps.json').write_text(json.dumps(rows,indent=2)+'\\n');print(i,r.returncode,flush=True)
 if r.returncode!=expected:raise SystemExit(1)
 if i==0:subprocess.run(['python3','collect-environment.py'],check=True)
"""
(p/'run.py').write_text(runner)
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-media-library-package-final-v2','-v',str(p)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','python3','run.py']
start=time.monotonic()
with (p/'run.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n')
print(p.name,r.returncode);print((p/'run.log').read_text()[-2000:]);raise SystemExit(r.returncode)
