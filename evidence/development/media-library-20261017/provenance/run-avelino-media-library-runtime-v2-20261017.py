from pathlib import Path
import hashlib,json,shutil,subprocess,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016';prior=base/'media-library-package-final-v2';p=base/'media-library-runtime-v2';assert not p.exists();p.mkdir();(p/'consumer-build').mkdir()
while not (prior/'result.json').exists():time.sleep(.25)
assert json.loads((prior/'result.json').read_text())['exitCode']==0
assert json.loads((prior/'steps.json').read_text())[0]['exitCode']==0
shutil.copytree(prior/'install',p/'install');shutil.copy2(prior/'consumer-build/InstalledConsumer',p/'consumer-build/InstalledConsumer');shutil.copy2(prior/'environment.json',p/'environment.json')
script=(root/'scripts/check-display-sessions.sh').read_text();line=next(s for s in script.splitlines() if s.strip().startswith('for fixture in '));script=script.replace(line,'    for fixture in media-library; do');(p/'replay.sh').write_text(script)
digest=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
inputs=dict(accepted=False,scope='Eight complete profiles for MediaLibrary; compiled canonical consumer/install only. Source/consumer/build checkouts absent. OpenGL uses software rendering.',files={str(f.relative_to(p)):digest(f) for f in p.rglob('*') if f.is_file()})
(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-media-library-runtime-v2','-v',str(p)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','bash','replay.sh']
start=time.monotonic()
with (p/'run.log').open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start,expectedSessions=8),indent=2)+'\n')
print(p.name,r.returncode);print((p/'run.log').read_text()[-3000:]);raise SystemExit(r.returncode)
