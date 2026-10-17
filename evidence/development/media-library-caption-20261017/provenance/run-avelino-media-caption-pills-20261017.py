from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';P=B/'media-library-caption-pills-v1';Q=B/'media-library-caption-package-final-v1';assert not P.exists();P.mkdir()
while not(Q/'result.json').exists():time.sleep(1)
assert json.loads((Q/'result.json').read_text())['exitCode']==0
shutil.copytree(Q/'install',P/'install');(P/'consumer-build').mkdir();shutil.copy2(Q/'consumer-build/InstalledConsumer',P/'consumer-build/InstalledConsumer');shutil.copy2(Q/'environment.json',P/'environment.json')
spec=importlib.util.spec_from_file_location('pills',R/'scripts/capture-pill-modifier-cases.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);corpus=m.rows();files={'scripts/capture-pill-modifier-cases.py','tests/consumer/native-pill-witnesses.json'}|{r['reference']for r in corpus}
for name in files:
 target=P/'driver'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,target)
(P/'inputs.json').write_text(json.dumps({str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest()for folder in['install','consumer-build','driver']for p in(P/folder).rglob('*')if p.is_file()},indent=2)+'\n')
c=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-media-caption-pills-v1','-v',str(P)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','python3','driver/scripts/capture-pill-modifier-cases.py','consumer-build/InstalledConsumer','captures','--jobs','2'];start=time.monotonic()
with(P/'run.log').open('w')as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT)
(P/'result.json').write_text(json.dumps(dict(exitCode=r.returncode,command=c,seconds=time.monotonic()-start,sourceAndBuildAbsent=True),indent=2)+'\n');print('Complete pill corpus',r.returncode);print((P/'run.log').read_text()[-1000:]);raise SystemExit(r.returncode)
