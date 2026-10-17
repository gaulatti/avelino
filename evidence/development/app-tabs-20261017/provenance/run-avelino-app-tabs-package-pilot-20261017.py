from pathlib import Path
import hashlib,json,shutil,subprocess,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016';p=base/'app-tabs-package-pilot-v1';assert not p.exists();p.mkdir();cache=base/'media-library-caption-package-final-v1'
for name in ['consumer','consumer-build']:shutil.copytree(cache/name,p/name)
shutil.copytree(root/'tests/consumer',p/'consumer',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
shutil.copytree(base/'app-tabs-build-v2/install',p/'install')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'inputs.json').write_text(json.dumps({str(f.relative_to(p)):sha(f)for d in ['consumer','install']for f in (p/d).rglob('*')if f.is_file()},indent=2)+'\n')
runner='''from pathlib import Path
import json,os,subprocess,time
p=Path('/package');rows=[]
commands=[['cmake','-S','consumer','-B','consumer-build','-G','Ninja','-DCMAKE_PREFIX_PATH=/package/install;/opt/qt'],['cmake','--build','consumer-build','--parallel','2'],['consumer-build/InstalledConsumer','--app-tabs','--app-tabs-observe','--app-tabs-report','/package/pilot'],['install/bin/AvelinoCatalog','--fixture','app-tabs','--capture','/package/gallery.png']]
for i,c in enumerate(commands):
 start=time.monotonic()
 with (p/(str(i)+'.log')).open('w')as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software'))
 rows.append(dict(command=c,exitCode=r.returncode,seconds=time.monotonic()-start,log=str(i)+'.log'));(p/'steps.json').write_text(json.dumps(rows,indent=2)+'\\n');print(i,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
'''
(p/'run.py').write_text(runner)
c=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-app-tabs-package-pilot-v1','-v',str(p)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','python3','run.py'];start=time.monotonic()
with (p/'run.log').open('w')as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=c,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print(p.name,r.returncode);print((p/'run.log').read_text()[-2500:]);raise SystemExit(r.returncode)
