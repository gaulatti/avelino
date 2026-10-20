from pathlib import Path
import gzip,hashlib,json,shutil,stat,subprocess
root=Path.cwd();runs=root/'artifacts/resumed-avelino-20261016';d=root/'evidence/development/file-input-location-20261017'
assert not d.exists();base='ab287b391ac529981bee85bbc602ce51d9d00261'
sha=lambda b:hashlib.sha256(b).hexdigest()
def copy(s,t):t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,t)
def write(name,value):p=d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
for name in ['file-input-qt-v54','file-input-location-package-v5','file-input-location-display-v5']:
 assert json.loads((runs/name/'result.json').read_text())['exitCode']==0
for n in [18,19]:
 p=runs/f'file-input-location-reader-v{n}'
 assert json.loads((p/'operator-controls-v1/result.json').read_text())['status']=='passed'
 assert json.loads((p/'exercise-result.json').read_text())['exitCode']==0
 assert json.loads((p/'session-result.json').read_text())['exitCode']==0
 assert json.loads((p/'speech-observations.json').read_text())['status']=='passed'
assert not subprocess.check_output(['docker','--context','colima-avelino-verify','ps','--format','{{.ID}}'],text=True).strip()
d.mkdir()
sources={f'file-input-qt-v{n}':json.loads((runs/f'file-input-qt-v{n}'/'inputs.json').read_text())['files']for n in range(46,55)}
final=sources['file-input-qt-v54'];assert len(final)==563
rows=subprocess.check_output(['git','ls-tree','-rz','--full-tree',base]).split(b'\0');tree={row.split(b'\t',1)[1].decode():row.split(b'\t',1)[0].split()[2].decode()for row in rows if row};baseline={}
with subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)as git:
 for name in sorted(final):
  if name not in tree:baseline[name]=None;continue
  git.stdin.write((tree[name]+'\n').encode());git.stdin.flush();header=git.stdout.readline().split();data=git.stdout.read(int(header[2]));assert git.stdout.read(1)==b'\n';baseline[name]=dict(blob=tree[name],sha256=sha(data))
 git.stdin.close();assert git.wait()==0
blobs={}
for snapshot,files in sources.items():
 for name,digest in files.items():
  f=runs/snapshot/'source'/name;raw=f.read_bytes();assert sha(raw)==digest
  if snapshot=='file-input-qt-v54':assert(root/name).read_bytes()==raw,name
  if not baseline[name]or baseline[name]['sha256']!=digest:
   target=d/'replay/blobs'/digest
   if not target.exists():copy(f,target)
   blobs[digest]=len(raw)
write('replay/source.json',dict(accepted=False,baseGit=base,final='file-input-qt-v54',baseline=baseline,snapshots=sources,blobs=blobs))
# Historical snapshots stay frozen; mutable compiler caches and source/install
# trees are excluded. Final source and package have separate complete replays.
names=[f'file-input-qt-v{n}'for n in range(46,55)]+[f'file-input-location-package-v{n}'for n in range(1,6)]+[f'file-input-location-display-v{n}'for n in [1,2,3,4,5]]+[f'file-input-location-reader-v{n}'for n in range(1,20)]
for name in names:
 p=runs/name
 for f in p.rglob('*'):
  rel=f.relative_to(p)
  if not f.is_file()or any(part in ['source','install','consumer','consumer-build','fresh-build','__pycache__','orca-prefs','runtime','output']for part in rel.parts):continue
  copy(f,d/'attempts'/name/rel)
 # Retain report JSONs for earlier successful package/display contexts; final
 # PNGs are copied once below. All earlier raw artifacts also remain local.
 for sub in ['runtime/output','output']:
  for f in(p/sub).glob('*.json'):copy(f,d/'attempts'/name/sub/f.name)
for label,source in [('captures',runs/'file-input-location-package-v5/runtime/output'),('display',runs/'file-input-location-display-v5/output')]:
 for f in source.iterdir():
  if f.is_file():copy(f,d/label/f.name)
copy(runs/'file-input-qt-v21/fresh-build/build/Testing/Temporary/LastTest.log',d/'qt-ui-LastTest.log')
# Reconstructable installed prefix and consumer ELF, with each compressed member
# expanding to at most 16 MiB, below the Linux boundary archive limit.
p=runs/'file-input-location-package-v5';package={};chunk_size=16*1024*1024
for prefix,source in [('install',p/'runtime/install'),('consumer-build',p/'runtime/consumer-build')]:
 for f in sorted(source.rglob('*')):
  if not f.is_file():continue
  raw=f.read_bytes();parts=[]
  for offset in range(0,len(raw),chunk_size):
   data=raw[offset:offset+chunk_size];digest=sha(data);target=d/'replay/package-chunks'/(digest+'.gz');target.parent.mkdir(parents=True,exist_ok=True)
   if not target.exists():
    with target.open('wb')as stream:
     with gzip.GzipFile(filename='',mode='wb',fileobj=stream,mtime=0,compresslevel=6)as archive:archive.write(data)
   parts.append(dict(sha256=digest,bytes=len(data),archive=str(target.relative_to(d))))
  package[prefix+'/'+str(f.relative_to(source))]=dict(sha256=sha(raw),bytes=len(raw),mode=stat.S_IMODE(f.stat().st_mode),parts=parts)
write('replay/package.json',dict(accepted=False,producer='file-input-qt-v54',consumer='file-input-location-package-v5',chunkBytes=chunk_size,files=package))
copy(Path(__file__),d/'tools/freeze.py')
copy(runs/'start-location-reader.py',d/'tools/start-location-reader.py')
copy(root/'scripts/check-display-sessions.sh',d/'tools/check-display-sessions.sh')
copy(runs/'reconstruct-location.py',d/'tools/reconstruct.py')
for name in ['location-weston13-fixed-image-v1','location-weston13-fixed-image-v2','location-weston13-fixed-image-v3','location-weston-stock-tooltip','location-weston-stock-tooltip-fixed13-v1']:
 p=runs/name
 for f in p.rglob('*'):
  rel=f.relative_to(p)
  if f.is_file()and 'build'not in rel.parts and f.suffix not in ['.xz','.pyc']:
   copy(f,d/'attempts'/name/rel)
for name in ['Dockerfile','install-weston.sh']:copy(root/'tools'/name,d/'tools/toolchain'/name)
write('toolchain.json',dict(accepted=False,build='location-weston13-fixed-image-v3',image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3',imageId=json.loads((runs/'location-weston13-fixed-image-v3/result.json').read_text())['imageId'],repositoryFiles={str(f.relative_to(root)):sha(f.read_bytes())for f in [root/'tools/Dockerfile',root/'tools/install-weston.sh']},compositorSource=json.loads((runs/'location-weston-debug/source-13.0.4.json').read_text()),qtVersion='6.8.3',qtLibrariesUnchanged=json.loads((runs/'location-weston13-fixed-image-v3/qt-fingerprints.json').read_text())))
print('Frozen nine Linux source snapshots, final installed location package and runtime evidence')
