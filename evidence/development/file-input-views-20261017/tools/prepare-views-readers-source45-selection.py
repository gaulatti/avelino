from pathlib import Path
import hashlib,json,shutil,subprocess
r=Path(__file__).resolve().parent;producer=r/'file-input-qt-v45'
assert json.loads((producer/'result.json').read_text())['exitCode']==0
image='avelino-toolchain:recovered-a11y-20261017-qt6.8.3';iid=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
assert iid=='sha256:cd1a2db8b8d979077bc74f0d596dea780aa485e0439df80200e90078cd9e5d5f'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for n,old in [(9,5),(10,6)]:
 p=r/f'file-input-views-reader-v{n}';p.mkdir(exist_ok=False)
 for f in ['session.py','event-monitor.py','reader-diagnostic.py','collect.py','profile.json','exercise.py']:
  shutil.copy2(r/f'file-input-views-reader-v{old}'/f,p/f)
 shutil.copytree(producer/'install',p/'install')
 shutil.copytree(r/f'file-input-views-reader-v{old}'/'fixtures',p/'fixtures')
 files={str(f.relative_to(p/'install')):sha(f)for f in sorted((p/'install').rglob('*'))if f.is_file()}
 (p/'inputs.json').write_text(json.dumps(dict(accepted=False,producer=producer.name,image=image,imageId=iid,packageFiles=files,physicalDisplay=False,physicalListening=False),indent=2)+'\n')
print('Prepared source-45 reader sessions')
