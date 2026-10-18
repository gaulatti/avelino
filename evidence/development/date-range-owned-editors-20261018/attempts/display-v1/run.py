from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];package=p.parent/'date-range-package-v1'
runtime=p/'runtime';runtime.mkdir();shutil.copytree(package/'runtime/install',runtime/'install');(runtime/'consumer-build').mkdir();shutil.copy2(package/'runtime/consumer-build/InstalledConsumer',runtime/'consumer-build/InstalledConsumer')
shutil.copy2(r/'scripts/check-display-sessions-date-range.sh',runtime/'check.sh')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3'
imageId=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
assert imageId=='sha256:2fdc6216ef3446ebd904a1999d3e0c909c7b667e844149ad2830d68d069e77f8'
environment=dict(accepted=False,package=package.name,consumerSha256=sha(runtime/'consumer-build/InstalledConsumer'),scriptSha256=sha(runtime/'check.sh'),imageId=imageId,physicalDisplay=False,hardwareAcceleration=False)
(runtime/'environment.json').write_text(json.dumps(environment,indent=2)+'\n');(p/'inputs.json').write_text(json.dumps(environment,indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','-v',str(runtime)+':/display-check','-w','/display-check',image,'bash','check.sh','/display-check/output']
start=time.monotonic()
with(p/'display.log').open('w')as log: result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(p/'commands.json').write_text(json.dumps([dict(name='display-sessions',command=command,exitCode=result.returncode,seconds=time.monotonic()-start)],indent=2)+'\n')
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,profiles=8 if result.returncode==0 else None),indent=2)+'\n');print('display',result.returncode)
raise SystemExit(result.returncode)
