from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];producer=p.parent/'navigation-cjk-qt-v5'
steps=json.loads((producer/'commands.json').read_text());assert all(s['exitCode']==0 for s in steps[:4])and steps[3]['name']=='install'
shutil.copytree(producer/'install',p/'install');shutil.copy2(r/'scripts/check-installed-catalog.sh',p/'check.sh');sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(p/'inputs.json').write_text(json.dumps(dict(accepted=False,producer=producer.name,scriptSha256=sha(p/'check.sh'),packageFiles={str(f.relative_to(p/'install')):sha(f)for f in sorted((p/'install').rglob('*'))if f.is_file()}),indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/catalog-check','-w','/catalog-check','avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3','bash','check.sh','/catalog-check/output']
start=time.monotonic()
with(p/'catalog.log').open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'commands.json').write_text(json.dumps([dict(command=command,exitCode=result.returncode,seconds=time.monotonic()-start)],indent=2)+'\n');(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode),indent=2)+'\n');print('installed catalog',result.returncode);raise SystemExit(result.returncode)
