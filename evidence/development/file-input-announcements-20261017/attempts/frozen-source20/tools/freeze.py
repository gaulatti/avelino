"""Retain the location-error correction and its scoped reader/package proof."""
from pathlib import Path
import hashlib, json, shutil, subprocess

root=Path.cwd();runs=root/'artifacts/resumed-avelino-20261016'
destination=root/'evidence/development/file-input-announcements-20261017'
base='59fd2e8d2c97fe3d89a3b71aaa1760ddd6807040'
assert not destination.exists();destination.mkdir()
digest=lambda data:hashlib.sha256(data).hexdigest()
def copy(source,target):
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
producer=runs/'file-input-qt-v20'
assert json.loads((producer/'result.json').read_text())['exitCode']==0
inputs=json.loads((producer/'inputs.json').read_text())
tree={r.split(b'\t',1)[1].decode():r.split(b'\t',1)[0].split()[2].decode()
      for r in subprocess.check_output(['git','ls-tree','-rz','--full-tree',base]).split(b'\0')if r}
changed=[];source={}
with subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)as git:
    for name,sha in sorted(inputs['files'].items()):
        frozen=producer/'source'/name;assert digest(frozen.read_bytes())==sha
        git.stdin.write((tree[name]+'\n').encode());git.stdin.flush();header=git.stdout.readline().split()
        assert header[:2]==[tree[name].encode(),b'blob'];data=git.stdout.read(int(header[2]));assert git.stdout.read(1)==b'\n'
        source[name]=dict(baseBlob=tree[name],baseSha256=digest(data),finalSha256=sha)
        if digest(data)!=sha:
            changed.append(name);copy(frozen,destination/'overlay'/name)
    git.stdin.close();assert git.wait()==0
assert changed==['src/Avelino/FileChooserDialog.qml','tests/components/fileinput-ui.cpp']
(destination/'source-binding.json').write_text(json.dumps(dict(accepted=False,baseGit=base,changedFiles=changed,files=source,
    productionChange='Announce visible chooser errors through the Qt 6.8.3 public announcement API; defer and coalesce without moving focus'),indent=2)+'\n')
for name in ['file-input-qt-v19','file-input-qt-v20','file-input-announcement-package-v1','file-input-error-reader-v1']:
    path=runs/name
    for file in path.rglob('*'):
        relative=file.relative_to(path)
        if file.is_file() and not any(part in ['source','install','consumer-build','__pycache__','orca-prefs']for part in relative.parts):
            copy(file,destination/'attempts'/name/relative)
copy(runs/'file-input-build/build/Testing/Temporary/LastTest.log',destination/'final-ui-LastTest.log')
copy(Path(__file__),destination/'tools/freeze.py')
print('Frozen two-file source change, final Qt checks, unchanged closed captures and actual X11/Orca announcements')
