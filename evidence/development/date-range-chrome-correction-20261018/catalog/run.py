from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];producer=p.parent/'date-range-qt-v20'
assert json.loads((producer/'result.json').read_text())['exitCode']==0
shutil.copytree(producer/'install',p/'install')
shutil.copy2(r/'scripts/check-installed-date-range-catalog.sh',p/'check.sh')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
(p/'inputs.json').write_text(json.dumps(dict(accepted=False,producer=producer.name,scriptSha256=sha(p/'check.sh'),packageFiles={str(f.relative_to(p/'install')):sha(f)for f in sorted((p/'install').rglob('*'))if f.is_file()}),indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','-v',str(p)+':/catalog-check','-w','/catalog-check','avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3','bash','check.sh','/catalog-check/output']
start=time.monotonic()
with(p/'catalog.log').open('w')as log: result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'commands.json').write_text(json.dumps([dict(name='installed-date-range-catalog',command=command,exitCode=result.returncode,seconds=time.monotonic()-start)],indent=2)+'\n')
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,producer=producer.name),indent=2)+'\n');print('catalog',result.returncode)
raise SystemExit(result.returncode)
