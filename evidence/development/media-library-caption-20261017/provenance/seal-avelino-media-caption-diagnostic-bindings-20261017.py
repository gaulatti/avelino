from pathlib import Path
import gzip,hashlib,importlib.util,io,json,shutil,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/media-library-caption-20261017';OLD=R/'evidence/development/media-library-reflow-20261017'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
current=read(D/'package/artifact-binding.json')['installedFiles'];previous=read(OLD/'package/artifact-binding.json')['installedFiles'];records={};blobs={}
for run,producer in [('media-library-caption-trace-operator-v1','media-library-caption-trace-build-v1'),('media-library-caption-glyph-trace-operator-v1','media-library-caption-glyph-trace-build-v2'),('media-library-caption-session-v1',None),('media-library-caption-offset-session-v1','media-library-caption-offset-build-v1')]:
 files={str(p.relative_to(B/run/'install')):sha(p)for p in(B/run/'install').rglob('*')if p.is_file()}
 expected={str(p.relative_to(B/producer/'install')):sha(p)for p in(B/producer/'install').rglob('*')if p.is_file()}if producer else previous
 assert files==expected,run
 manifest=D/'attempts'/producer/'inputs.json'if producer else OLD/'qt/inputs.json'
 locations={}
 for name,digest in files.items():
  if current.get(name)==digest:location='current:install/'+name
  elif previous.get(name)==digest:location='previous:install/'+name
  else:location='diagnostic-binaries/'+digest;blobs.setdefault(digest,B/run/'install'/name)
  locations[name]=dict(sha256=digest,location=location)
 records[run]=dict(producer=producer or'published-reflow',producerSourceManifestSha256=sha(manifest),installedFiles=locations)
report=read(D/'candidate.json');pending={};size=0;archives={}
def pack(key,files):
 manifest={};path=D/(key+'.tar.gz')
 with path.open('xb')as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0)as gz,tarfile.open(fileobj=gz,mode='w')as stream:
  for name,p in sorted(files.items()):
   data=p.read_bytes();entry=tarfile.TarInfo(name);entry.size=len(data);entry.mode=p.stat().st_mode&0o777;entry.mtime=0;stream.addfile(entry,io.BytesIO(data));manifest[name]=dict(sha256=sha(p),bytes=len(data),mode=entry.mode)
 m=D/(key+'-manifest.json');m.write_text(json.dumps(manifest,indent=2)+'\n');return dict(archive=path.name,manifest=m.name,files=len(files))
for digest,p in sorted(blobs.items()):
 if size+p.stat().st_size>=48*1024*1024:
  key='diagnostic-binaries-'+str(len(archives)+1);archives[key]=pack(key,pending);pending={};size=0
 pending['diagnostic-binaries/'+digest]=p;size+=p.stat().st_size
if pending:key='diagnostic-binaries-'+str(len(archives)+1);archives[key]=pack(key,pending)
(D/'regression/diagnostic-install-bindings.json').write_text(json.dumps(records,indent=2)+'\n');shutil.copy2(Path(__file__),D/'provenance'/Path(__file__).name)
report['archives'].update(archives);report['files']={str(p.relative_to(D)):sha(p)for p in D.rglob('*')if p.is_file()and p.name not in['candidate.json','README.md']};(D/'candidate.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('Bound',len(records),'diagnostic install trees;',len(blobs),'distinct additional binary payloads;',len(archives),'archives')
