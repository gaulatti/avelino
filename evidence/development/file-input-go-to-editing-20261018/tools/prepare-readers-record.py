from pathlib import Path
import hashlib,json,shutil,subprocess
b=Path(__file__).resolve().parent;producer=b/'file-input-qt-v61'
assert json.loads((producer/'result.json').read_text())['exitCode']==0
image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3'
image_id=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
assert image_id=='sha256:2fdc6216ef3446ebd904a1999d3e0c909c7b667e844149ad2830d68d069e77f8'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in [5,6]:
 p=b/f'file-input-go-to-reader-v{n}'
 shutil.copytree(producer/'install',p/'install')
 inputs=dict(accepted=False,producer=producer.name,image=image,imageId=image_id,packageFiles={str(f.relative_to(p/'install')):sha(f)for f in sorted((p/'install').rglob('*'))if f.is_file()},fixtureFiles={str(f.relative_to(p/'fixtures')):sha(f)for f in sorted((p/'fixtures').rglob('*'))if f.is_file()},fixtureDirectories=[str(f.relative_to(p/'fixtures'))for f in sorted((p/'fixtures').rglob('*'))if f.is_dir()],profile=json.loads((p/'profile.json').read_text()),priorAttempt=f'file-input-go-to-reader-v{4 if n==5 else 3}',lookupPolicy='Locate distinct accessible modal objects; preserve raw duplicate traversal edges.',speechLogLevel=5)
 (p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
 print(p.name,len(inputs['packageFiles']),'installed files')
