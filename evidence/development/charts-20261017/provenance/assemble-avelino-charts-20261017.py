from pathlib import Path
import gzip,hashlib,io,json,shutil,subprocess,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/charts-20261017'
P=B/'charts-package-final-v1';Q=B/'charts-full-v1';U=B/'charts-runtime-v1';O=B/'charts-operator-v1';C=B/'charts-comparison-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def write(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for p,code in [(P,0),(Q,0),(U,0),(O,0),(C,1)]:assert read(p/'result.json')['exitCode']==code,p
assert not D.exists();D.mkdir()
def archive(key,files):
 assert sum(p.stat().st_size for p in files.values())<48*1024*1024,key
 manifest={};path=D/(key+'.tar.gz')
 with path.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as gz,tarfile.open(fileobj=gz,mode='w') as stream:
  for name,p in sorted(files.items()):
   data=p.read_bytes();info=tarfile.TarInfo(name);info.size=len(data);info.mode=p.stat().st_mode&0o777;info.mtime=0;stream.addfile(info,io.BytesIO(data));manifest[name]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),mode=info.mode)
 write(D/(key+'-manifest.json'),manifest);return dict(archive=path.name,manifest=key+'-manifest.json',files=len(files))
def chunks(prefix,files):
 result={};current={};size=0
 for name,p in sorted(files.items()):
  if size+p.stat().st_size>=48*1024*1024:
   key=prefix+str(len(result)+1);result[key]=archive(key,current);current={};size=0
  current[name]=p;size+=p.stat().st_size
 if current:key=prefix+str(len(result)+1);result[key]=archive(key,current)
 return result
shutil.copytree(P/'captures',D/'captures');shutil.copytree(P/'catalog-evidence',D/'catalogs');shutil.copytree(C/'results',D/'comparison')
for name in ['inputs.json','environment.json','environment-seed.json','steps.json','result.json','0.log','1.log','2.log','run.log','run.py','check-installed.sh','check-installed-catalog.sh','collect-environment.py','strict.json']:
 copy(P/name,D/'package'/name)
for name in ['run.log','result.json']:copy(Q/name,D/'qt'/name)
copy(B/'charts-build-v5/build/Testing/Temporary/LastTest.log',D/'qt/LastTest.log')
copy(B/'charts-build-v5/inputs.json',D/'qt/producer-inputs.json')
for name in ['inputs.json','result.json','run.log','replay.sh']:copy(U/name,D/'runtime-proof'/name)
for p in (U/'display-evidence').rglob('*'):
 if p.is_file() and p.suffix!='.png':copy(p,D/'runtime'/p.relative_to(U/'display-evidence'))
for p in O.rglob('*'):
 if p.is_file() and 'install' not in p.relative_to(O).parts:copy(p,D/'operator'/p.relative_to(O))
copy(B/'charts-catalog-regression.json',D/'regression/catalogs.json')
for name in ['charts-transform-analysis-v1.json','charts-transform-analysis-v2.json','charts-dpr-layout-analysis.json']:copy(B/name,D/'geometry-analysis'/name)
images=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect','avelino-toolchain:data-metrics-qt6.8.3','avelino-toolchain:clipping-qt6.8.3'],text=True)
write(D/'provenance/toolchain-images.json',[{k:v[k] for k in ['Id','RepoTags','Architecture','Os','Created']} for v in json.loads(images)])
for name in ['build-avelino-charts-20261017.py','run-avelino-charts-package-20261017.py','run-avelino-charts-final-package-20261017.py','run-avelino-charts-full-20261017.py','run-avelino-charts-runtime-20261017.py','run-avelino-charts-operator-20261017.py','compare-avelino-charts-20261017.py']:copy(Path('/Users/gaulatti/.codex/tmp')/name,D/'provenance'/name)
installed={str(p.relative_to(P/'install')):sha(p) for p in (P/'install').rglob('*') if p.is_file()};assert len(installed)==133
for p in [B/'charts-build-v5',U,O]:assert {str(f.relative_to(p/'install')):sha(f) for f in (p/'install').rglob('*') if f.is_file()}==installed,p
consumer=sha(P/'consumer-build/InstalledConsumer');assert consumer==sha(U/'consumer-build/InstalledConsumer')
producer=read(B/'charts-build-v5/inputs.json')['sourceFiles'];critical={n:v for n,v in producer.items() if n.startswith(('src/','samples/','assets/','tokens/','cmake/')) or n in ['CMakeLists.txt','CMakePresets.json']}
assert all(sha(R/n)==v for n,v in critical.items())
consumer_files={str(p.relative_to(P/'consumer')):sha(p) for p in (P/'consumer').rglob('*') if p.is_file()};assert all(sha(R/'tests/consumer'/n)==v for n,v in consumer_files.items())
write(D/'package/artifact-binding.json',dict(installedFiles=installed,consumerSha256=consumer,producerSourceManifestSha256=sha(B/'charts-build-v5/inputs.json'),producerCriticalFiles=critical,consumerFiles=consumer_files,architecture='aarch64',qt='6.8.3'))
strict={}
for p in P.glob('strict-*.png'):
 name='light-text1-dpr1-'+p.name.removeprefix('strict-');q=D/'captures'/name
 assert p.read_bytes()==q.read_bytes(),p;strict[p.name]=dict(identicalCapture=name,sha256=sha(p))
assert len(strict)==218;write(D/'package/strict-images.json',strict)
implementation={str(p.relative_to(R)):p for folder in ['src','samples','tests','scripts','assets','tokens','cmake','tools'] for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
for name in ['CMakeLists.txt','CMakePresets.json']:implementation[name]=R/name
archives={'implementation':archive('implementation',implementation),'installedPackage':archive('installed-package',{**{'install/'+n:P/'install'/n for n in installed},'consumer-build/InstalledConsumer':P/'consumer-build/InstalledConsumer'})}
archives.update(chunks('runtime-images-',{'runtime/'+str(p.relative_to(U/'display-evidence')):p for p in (U/'display-evidence').rglob('*.png')}))
expected={**{f'charts-build-v{i}':0 for i in range(1,6)},**{f'charts-package-v{i}':0 for i in range(1,4)},'charts-package-final-v1':0,'charts-full-v1':0,'charts-runtime-v1':0,'charts-operator-v1':0,'charts-comparison-v1':1}
attempts=[]
for name,code in expected.items():
 p=B/name;assert read(p/'result.json')['exitCode']==code;attempts.append(dict(name=name,exitCode=code,quality='DPR binding warnings preserved; corrected by later attempts' if name=='charts-package-v1' else 'terminal result preserved'))
 for f in p.iterdir():
  if f.is_file() and f.suffix in ['.json','.log','.py','.sh']:copy(f,D/'attempts'/name/f.name)
# Reconstruct every frozen producer source from immutable Git objects plus all
# changed source bytes. Apple sources never enter these Linux snapshots.
base='ba2e98e9f96dc7e89fa3569447454532c410d443';tree={}
for row in subprocess.check_output(['git','ls-tree','-rz','--full-tree',base],cwd=R).split(b'\0'):
 if row:head,name=row.split(b'\t',1);tree[name.decode()]=head.decode().split()[2]
base_files={};blobs={};overlays={}
for i in range(1,6):
 name=f'charts-build-v{i}';manifest=read(B/name/'inputs.json')['sourceFiles'];delta={}
 for path,checksum in manifest.items():
  p=B/name/'source'/path;data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==checksum
  gitsha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if tree.get(path)==gitsha:base_files[path]=dict(gitObject=gitsha,sha256=checksum)
  else:delta[path]=checksum;blobs.setdefault(checksum,p)
 overlays[name]=delta
write(D/'replay/base-files.json',dict(baseRevision=base,files=base_files))
write(D/'replay/source-overlays.json',dict(baseRevision=base,attempts=overlays,blobMembers={n:'blobs/'+n for n in blobs},scope='Full frozen manifests, immutable Git base and every changed source byte. Independent-machine replay remains pending.'))
for i in range(1,4):
 p=B/f'charts-package-v{i}'
 for f in (p/'consumer').rglob('*'):
  if f.is_file():blobs.setdefault(sha(f),f)
archives.update(chunks('source-blobs-',{'blobs/'+checksum:p for checksum,p in blobs.items()}))
# Keep the early capture outputs too; identical bytes refer to canonical files.
canonical={sha(p):'candidate/'+str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()};diagnostics={};outputmap={}
for i in range(1,4):
 p=B/f'charts-package-v{i}'
 for f in (p/'results').rglob('*'):
  if f.is_file():
   checksum=sha(f);location=canonical.get(checksum)
   if location is None:diagnostics.setdefault(checksum,f);location='diagnostics/'+checksum
   outputmap[str(f.relative_to(B))]=dict(sha256=checksum,location=location)
write(D/'replay/diagnostic-outputs.json',outputmap);archives.update(chunks('diagnostic-outputs-',{'diagnostics/'+checksum:p for checksum,p in diagnostics.items()}))
summary=read(D/'comparison/comparison.json')['summary']
report=dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',accepted=False,status='verification-pending',tolerance='none',approvedExceptions=[],expectedImagesChanged=False,remainingAcceptance=['nativeGeometryAndRaster','nativeSystemFonts','nativeNonfiniteInputDeterminism','nativeInputTiming','physicalDisplaysInput','readers','independentMachineReferenceReplay'],strictComparisonStatus='failed',strictComparison=summary,
 validation=dict(fullQtTargets=31,independentModes=33,catalogCaptures=135,legacyPngs=131,legacyMetadata=131,installedFiles=133,virtualProfiles=40,chartVirtualProfiles=8,operatorControls=14,operatorClicks=24,operatorStates=25,strictDefaultExitCode=1,strictImageExitCode=1,physicalDisplay=False,hardwareAcceleration=False),archives=archives,attempts=attempts)
report['files']={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file() and p.name not in ['candidate.json','README.md']};write(D/'candidate.json',report)
(D/'README.md').write_text('# Linux chart candidate\n\nAll five public chart families, all 1,744 native/candidate pairs, eight chart virtual profiles and 25 actual X11 gallery states remain independently reviewable. Package/runtime checks pass; strict geometry/raster differences and native NaN-bar initialization remain open. See candidate.json and [the chart contract](../../../docs/charts.md) for acceptance limits. Earlier warning-producing attempts, their exact inputs and all output bytes remain preserved. No expected image, source pin, tolerance or exception is changed.\n')
print('Assembled chart candidate:',summary)
