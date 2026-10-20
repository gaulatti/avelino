"""Seal final announcement evidence, preserving pre-recovery attempts separately."""
from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path.cwd();runs=root/'artifacts/resumed-avelino-20261016'
d=root/'evidence/development/file-input-announcements-20261017'
base='59fd2e8d2c97fe3d89a3b71aaa1760ddd6807040'
assert not(d/'validation.json').exists()
for name in ['file-input-qt-v21','file-input-announcement-package-v3']:
 assert json.loads((runs/name/'result.json').read_text())['exitCode']==0
for name in ['file-input-error-reader-v6','file-input-error-reader-v7']:
 assert json.loads((runs/name/'operator-errors-v2/result.json').read_text())['status']=='passed'
 assert json.loads((runs/name/'session-result.json').read_text())['exitCode']==0
sha=lambda data:hashlib.sha256(data).hexdigest()
def copy(s,t):
 t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,t)
# Preserve the earlier draft source binding and successful source-20 UI proof.
prior=d/'attempts/frozen-source20';assert not prior.exists();prior.mkdir(parents=True)
for name in ['source-binding.json','overlay','final-ui-LastTest.log','tools']:
 s=d/name
 if s.exists():shutil.move(str(s),str(prior/name))
tree={row.split(b'\t',1)[1].decode():row.split(b'\t',1)[0].split()[2].decode()for row in subprocess.check_output(['git','ls-tree','-rz','--full-tree',base]).split(b'\0')if row}
inputs={n:json.loads((runs/f'file-input-qt-v{n}'/'inputs.json').read_text())['files']for n in [19,20,21]}
assert len(inputs[21])==549
records={};changes={n:[]for n in inputs}
with subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)as git:
 for name,final in sorted(inputs[21].items()):
  git.stdin.write((tree[name]+'\n').encode());git.stdin.flush();header=git.stdout.readline().split();assert header[1]==b'blob'
  data=git.stdout.read(int(header[2]));assert git.stdout.read(1)==b'\n';baseline=sha(data)
  records[name]=dict(baseBlob=tree[name],baseSha256=baseline,finalSha256=final)
  for n in inputs:
   frozen=runs/f'file-input-qt-v{n}'/'source'/name
   assert sha(frozen.read_bytes())==inputs[n][name]
   if inputs[n][name]!=baseline:
    changes[n].append(name)
    target=d/'overlay'/name if n==21 else d/f'source-overlays/file-input-qt-v{n}'/name
    copy(frozen,target)
 git.stdin.close();assert git.wait()==0
for files in changes.values():assert files==['src/Avelino/FileChooserDialog.qml','tests/components/fileinput-ui.cpp']
(d/'source-binding.json').write_text(json.dumps(dict(accepted=False,baseGit=base,finalProducer='file-input-qt-v21',changedFiles=changes[21],files=records,snapshots={f'file-input-qt-v{n}':v for n,v in inputs.items()},changedBySnapshot={f'file-input-qt-v{n}':v for n,v in changes.items()}),indent=2)+'\n')
for name in ['file-input-qt-v19','file-input-qt-v20','file-input-qt-v21','file-input-announcement-package-v1','file-input-announcement-package-v2','file-input-announcement-package-v3','file-input-error-reader-v1','file-input-error-reader-v2','file-input-error-reader-v3','file-input-error-reader-v4','file-input-error-reader-v5','file-input-error-reader-v6','file-input-error-reader-v7','recovered-toolchain-v1']:
 for f in (runs/name).rglob('*'):
  rel=f.relative_to(runs/name)
  if f.is_file()and not any(part in ['source','install','consumer-build','fresh-build','__pycache__','orca-prefs']for part in rel.parts):copy(f,d/'attempts'/name/rel)
copy(runs/'file-input-qt-v21/fresh-build/build/Testing/Temporary/LastTest.log',d/'final-ui-LastTest.log')
copy(Path(__file__),d/'tools/freeze.py')
copy(runs/'prepare-final-announcement-runtime.py',d/'tools/prepare-runtime.py')
copy(runs/'reconstruct-announcements.py',d/'tools/reconstruct.py')
copy(runs/'check-final-announcements.py',d/'tools/check-runtime-initial.py')
copy(runs/'check-final-announcements-v2.py',d/'tools/check-runtime-v2.py')
copy(runs/'check-final-announcements-v3.py',d/'tools/check-runtime-v3.py')
copy(runs/'check-final-announcements-v4.py',d/'tools/check-runtime.py')
copy(runs/'check-final-announcements-wayland.py',d/'tools/check-wayland-runtime.py')
copy(runs/'compare-announcement-captures.py',d/'tools/compare-captures.py')
print('Sealed source-21 correction with source-19/20 attempts retained')
