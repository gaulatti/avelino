from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';P=B/'media-library-caption-fonts-v1';assert not P.exists();P.mkdir();shutil.copytree(B/'media-library-caption-build-v1/install',P/'install')
spec=importlib.util.spec_from_file_location('fonts',R/'scripts/capture-font-modifier-cases.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);corpus=m.rows()
files={'scripts/capture-font-modifier-cases.py'}
for kind,(name,_)in m.CORPORA.items():
 base=f'evidence/reference-investigations/{name}-20261016';files|={base+'/investigation.json',base+'/captures/captures.json'}
for row in corpus:files.add(str((row['directory']/'captures'/row['source']['paths'][0]).relative_to(R)))
for name in files:
 target=P/'driver'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,target)
(P/'inputs.json').write_text(json.dumps({str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest()for folder in ['install','driver']for p in(P/folder).rglob('*')if p.is_file()},indent=2)+'\n')
c=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-media-caption-fonts-v1','-v',str(P)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','python3','driver/scripts/capture-font-modifier-cases.py','install/bin/AvelinoCatalog','captures','--jobs','4'];start=time.monotonic()
with(P/'run.log').open('w')as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT)
(P/'result.json').write_text(json.dumps(dict(exitCode=r.returncode,command=c,seconds=time.monotonic()-start,sourceAndBuildAbsent=True),indent=2)+'\n');print('Complete font corpus',r.returncode);print((P/'run.log').read_text()[-1000:]);raise SystemExit(r.returncode)
