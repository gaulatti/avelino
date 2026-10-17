from pathlib import Path
import hashlib,json,shutil,subprocess,time
root=Path('/Users/gaulatti/source/gaulatti/avelino');base=root/'artifacts/resumed-avelino-20261016';prior=base/'app-tabs-matrix-package-v3';p=base/'app-tabs-readiness-v1';assert not p.exists();assert json.loads((prior/'result.json').read_text())['exitCode']==0;p.mkdir()
for d in ['consumer','consumer-build','install']:shutil.copytree(prior/d,p/d)
for n in ['check-installed.sh','check-installed-catalog.sh']:shutil.copy2(root/'scripts'/n,p/n)
shutil.copy2(base/'media-library-caption-package-final-v1/environment.json',p/'environment-seed.json')
collector=Path('/Users/gaulatti/.codex/tmp/collect-avelino-media-library-environment-20261017.py').read_text().replace("old=p/'environment.json';old.rename(p/'environment-seed.json')","old=p/'environment.json'").replace('Current installed-media-library reflow package','Current installed AppTabs package')
(p/'collect-environment.py').write_text(collector)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'inputs.json').write_text(json.dumps({str(f.relative_to(p)):sha(f)for d in ['consumer','install']for f in (p/d).rglob('*')if f.is_file()},indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-app-tabs-readiness-v1','-v',str(p)+':/package:rw','-w','/package','avelino-toolchain:clipping-qt6.8.3','bash','-lc','python3 collect-environment.py && bash check-installed.sh'];start=time.monotonic()
with (p/'run.log').open('w')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'result.json').write_text(json.dumps(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start),indent=2)+'\n');print(p.name,r.returncode);print((p/'run.log').read_text()[-2800:]);raise SystemExit(r.returncode)
