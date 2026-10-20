from pathlib import Path
import hashlib,json,shutil,subprocess,time
r=Path(__file__).resolve().parent;producer=r/'file-input-qt-v29'
while not(producer/'result.json').exists():time.sleep(.2)
assert json.loads((producer/'result.json').read_text())['exitCode']==0
image='avelino-toolchain:recovered-a11y-20261017-qt6.8.3';iid=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip();sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for n,old in [(8,3),(9,5)]:
 p=r/f'file-input-navigation-reader-v{n}';p.mkdir(exist_ok=False)
 for f in ['session.py','event-monitor.py','reader-diagnostic.py','collect.py','profile.json']:shutil.copy2(r/f'file-input-navigation-reader-v{old}'/f,p/f)
 shutil.copytree(producer/'install',p/'install');(p/'fixtures').mkdir();(p/'fixtures/untitled folder').mkdir();(p/'fixtures/one.txt').write_text('Avelino controlled reader fixture\n')
 files={str(f.relative_to(p/'install')):sha(f)for f in sorted((p/'install').rglob('*'))if f.is_file()}
 (p/'inputs.json').write_text(json.dumps(dict(accepted=False,producer=producer.name,image=image,imageId=iid,packageFiles=files,physicalDisplay=False,physicalListening=False),indent=2)+'\n')
print('Prepared final modal-adapter reader sessions')
