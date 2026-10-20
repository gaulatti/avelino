from pathlib import Path
import gzip,hashlib,json,shutil,stat,subprocess
root=Path.cwd();runs=root/'artifacts/resumed-avelino-20261016';d=root/'evidence/development/file-input-views-20261017'
assert not d.exists();d.mkdir();base='6008f0c3fd14e25194b989c0c3cd0242eeeb6624'
sha=lambda b:hashlib.sha256(b).hexdigest()
def copy(s,t):t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,t)
def write(name,value):p=d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
for name in ['file-input-qt-v45','file-input-views-package-v4','file-input-views-display-v3']:
 assert json.loads((runs/name/'result.json').read_text())['exitCode']==0
for n in [9,10]:
 p=runs/f'file-input-views-reader-v{n}'
 assert json.loads((p/'operator-controls-v1/result.json').read_text())['status']=='passed'
 assert json.loads((p/'exercise-result.json').read_text())['exitCode']==0
 assert json.loads((p/'session-result.json').read_text())['exitCode']==0
 assert json.loads((p/'speech-observations.json').read_text())['status']=='passed'
assert not subprocess.check_output(['docker','--context','colima-avelino-verify','ps','--format','{{.ID}}'],text=True).strip()
sources={f'file-input-qt-v{n}':json.loads((runs/f'file-input-qt-v{n}'/'inputs.json').read_text())['files']for n in range(30,46)}
final=sources['file-input-qt-v45'];assert len(final)==557
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
  if snapshot=='file-input-qt-v45':assert(root/name).read_bytes()==raw,name
  if not baseline[name]or baseline[name]['sha256']!=digest:
   target=d/'replay/blobs'/digest
   if not target.exists():copy(f,target)
   blobs[digest]=len(raw)
write('replay/source.json',dict(accepted=False,baseGit=base,final='file-input-qt-v45',baseline=baseline,snapshots=sources,blobs=blobs))
# Historical snapshots stay frozen; mutable compiler caches and source/install
# trees are excluded. Final source and package have separate complete replays.
names=[f'file-input-qt-v{n}'for n in range(30,46)]+[f'file-input-views-package-v{n}'for n in range(1,5)]+[f'file-input-views-display-v{n}'for n in [1,2,3]]+[f'file-input-views-reader-v{n}'for n in range(1,11)]
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
for label,source in [('captures',runs/'file-input-views-package-v4/output'),('display',runs/'file-input-views-display-v3/output')]:
 for f in source.iterdir():
  if f.is_file():copy(f,d/label/f.name)
copy(runs/'file-input-qt-v21/fresh-build/build/Testing/Temporary/LastTest.log',d/'qt-ui-LastTest.log')
# Reconstructable installed prefix and consumer ELF, with each compressed member
# expanding to at most 16 MiB, below the Linux boundary archive limit.
p=runs/'file-input-views-package-v4';package={};chunk_size=16*1024*1024
for prefix,source in [('install',p/'install'),('consumer-build',p/'consumer-build')]:
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
write('replay/package.json',dict(accepted=False,producer='file-input-qt-v45',consumer='file-input-views-package-v4',chunkBytes=chunk_size,files=package))
copy(Path(__file__),d/'tools/freeze.py')
for name in ['start-views-reader.py','views-operator-body.py','prepare-views-readers-source45.py','prepare-views-readers-source45-selection.py']:
 copy(runs/name,d/'tools'/name)
copy(root/'scripts/check-display-sessions.sh',d/'tools/check-display-sessions.sh')
print('Frozen sixteen Linux source snapshots, final installed package and owned-view runtime evidence')
