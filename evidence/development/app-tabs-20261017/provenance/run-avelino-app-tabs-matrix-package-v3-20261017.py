from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016';p=base/'app-tabs-matrix-package-v3';assert not p.exists();p.mkdir();cache=base/'app-tabs-matrix-package-v2'
for name in ['consumer','consumer-build']:shutil.copytree(cache/name,p/name)
shutil.copytree(root/'tests/consumer',p/'consumer',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(base/'app-tabs-build-v8/install',p/'install')
spec=importlib.util.spec_from_file_location('app_tabs',root/'scripts/capture-app-tabs.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
paths={'scripts/capture-app-tabs.py','tests/consumer/native-app-tabs-witnesses.json'}|{r['reference']for r in m.rows()}
for name in paths:
 target=p/'driver'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,target)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'inputs.json').write_text(json.dumps({str(f.relative_to(p)):sha(f)for d in ['consumer','install','driver']for f in (p/d).rglob('*')if f.is_file()},indent=2)+'\n')
runner='''from pathlib import Path
import json,os,subprocess,time
p=Path('/package');rows=[]
commands=[(['cmake','-S','consumer','-B','consumer-build','-G','Ninja','-DCMAKE_PREFIX_PATH=/package/install;/opt/qt'],0),(['cmake','--build','consumer-build','--parallel','2'],0),(['python3','driver/scripts/capture-app-tabs.py','consumer-build/InstalledConsumer','captures','--jobs','2'],0),(['consumer-build/InstalledConsumer','--app-tabs','--app-tabs-report','/package/strict'],1),(['install/bin/AvelinoCatalog','--fixture','app-tabs','--capture','/package/gallery.png'],0)]
for i,(c,expected)in enumerate(commands):
 start=time.monotonic()
 with (p/(str(i)+'.log')).open('w')as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software'))
 rows.append(dict(command=c,exitCode=r.returncode,expectedExitCode=expected,seconds=time.monotonic()-start,log=str(i)+'.log'));(p/'steps.json').write_text(json.dumps(rows,indent=2)+'\\n');print(i,r.returncode,flush=True)
 if r.returncode!=expected:raise SystemExit(1)
'''
(p/'run.py').write_text(runner)
c=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-app-tabs-matrix-package-v3','-v',str(p)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','python3','run.py'];start=time.monotonic()
with (p/'run.log').open('w')as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=c,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print(p.name,r.returncode);print((p/'run.log').read_text()[-2500:]);raise SystemExit(r.returncode)
