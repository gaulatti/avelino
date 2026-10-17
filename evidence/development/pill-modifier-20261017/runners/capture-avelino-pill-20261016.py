from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016'
p=base/sys.argv[1];package=base/sys.argv[2];assert not p.exists();p.mkdir();(p/'consumer-build').mkdir()
assert json.loads((package/'result.json').read_text())['exitCode']==0
shutil.copytree(package/'install',p/'install');shutil.copy2(package/'consumer-build/InstalledConsumer',p/'consumer-build/InstalledConsumer')
script=root/'scripts/capture-pill-modifier-cases.py';spec=importlib.util.spec_from_file_location('pill_capture',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
paths={'scripts/capture-pill-modifier-cases.py','tests/consumer/native-pill-witnesses.json'}|{r['reference'] for r in m.rows()}
for name in paths:
 target=p/'driver'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,target)
digest=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
inputs=dict(scope='Canonical executable/install plus Linux capture driver and immutable reference PNG/JSON data only; producer and consumer source/build files absent',consumerSha256=digest(p/'consumer-build/InstalledConsumer'),files={str(f.relative_to(p)):digest(f) for directory in ['driver','install'] for f in (p/directory).rglob('*') if f.is_file()})
(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-'+p.name,'-v',str(p)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','python3','driver/scripts/capture-pill-modifier-cases.py','consumer-build/InstalledConsumer','captures','--jobs','2']
start=time.monotonic()
with (p/'run.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n')
print(p.name,r.returncode);print((p/'run.log').read_text()[-3000:]);raise SystemExit(r.returncode)
