from pathlib import Path
import gzip,hashlib,io,json,shutil,subprocess,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/chart-geometry-20261017';OLD=R/'evidence/development/charts-20261017'
P=B/'charts-geometry-package-final-v1';Q=B/'charts-geometry-build-v5';U=B/'charts-geometry-runtime-v1';O=B/'charts-geometry-operator-v1';S=B/'charts-geometry-supplement-v1'
base='4184245ca3cfad425c7e3b268a1b4ec159bd8e29'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
expected={**{f'charts-geometry-build-v{i}':1 if i==1 else 0 for i in range(1,6)},'charts-geometry-focused-v1':0,'charts-geometry-package-v1':0,'charts-geometry-package-v2':0,'charts-geometry-package-final-v1':0,'charts-geometry-supplement-v1':0,'charts-geometry-runtime-v1':0,'charts-geometry-operator-v1':0,'charts-geometry-comparison-v1':1,'charts-geometry-supplement-comparison-v1':1}
for n,code in expected.items():assert read(B/n/'result.json')['exitCode']==code,n
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
for source,target in [(P/'captures','captures'),(P/'catalog-evidence','catalogs'),(B/'charts-geometry-comparison-v1/results','comparison'),(S/'captures','supplement'),(B/'charts-geometry-supplement-comparison-v1/results','supplement-comparison')]:shutil.copytree(source,D/target)
for n in ['inputs.json','environment.json','environment-seed.json','steps.json','result.json','0.log','1.log','2.log','run.log','run.py','check-installed.sh','check-installed-catalog.sh','collect-environment.py','strict.json']:copy(P/n,D/'package'/n)
for n in ['run.log','result.json','inputs.json']:copy(Q/n,D/'qt'/n)
for n in ['run.log','result.json']:copy(B/'charts-geometry-focused-v1'/n,D/'qt/focused'/n)
copy(Q/'build/Testing/Temporary/LastTest.log',D/'qt/LastTest.log')
ninja=(Q/'build/build.ninja').read_text().splitlines();index=next(i for i,l in enumerate(ninja) if 'chartrenderer.cpp.o:' in l)
(D/'qt/floating-point-build-rule.txt').write_text('\n'.join(ninja[index:index+12])+'\n')
assert '-ffp-contract=off' in (D/'qt/floating-point-build-rule.txt').read_text()
for n in ['inputs.json','result.json','run.log','replay.sh','environment.json']:copy(U/n,D/'runtime-proof'/n)
for p in (U/'display-evidence').rglob('*'):
 if p.is_file() and p.suffix!='.png':copy(p,D/'runtime'/p.relative_to(U/'display-evidence'))
for p in O.rglob('*'):
 if p.is_file() and 'install' not in p.relative_to(O).parts:copy(p,D/'operator'/p.relative_to(O))
for n in ['inputs.json','post-capture-dimension-kind-audit.json','result.json','run.log']:copy(S/n,D/'supplement-proof'/n)
# Preserve the executed capture helper, including its earlier validation order.
for p in (S/'driver/scripts').iterdir():
 if p.is_file():copy(p,D/'supplement-proof/driver'/p.name)
installed={str(p.relative_to(P/'install')):sha(p) for p in (P/'install').rglob('*') if p.is_file()};old=read(OLD/'package/artifact-binding.json')
assert len(installed)==133
for p in [Q,U,O,S]:assert {str(f.relative_to(p/'install')):sha(f) for f in (p/'install').rglob('*') if f.is_file()}==installed,p
consumer=sha(P/'consumer-build/InstalledConsumer');assert consumer==sha(U/'consumer-build/InstalledConsumer')==old['consumerSha256']
consumer_files={str(p.relative_to(P/'consumer')):sha(p) for p in (P/'consumer').rglob('*') if p.is_file()};assert consumer_files==old['consumerFiles']
producer=read(Q/'inputs.json')['sourceFiles'];critical={n:v for n,v in producer.items() if n.startswith(('src/','samples/','assets/','tokens/','cmake/')) or n in ['CMakeLists.txt','CMakePresets.json']};assert all(sha(R/n)==v for n,v in critical.items())
write(D/'package/artifact-binding.json',dict(installedFiles=installed,consumerSha256=consumer,consumerFiles=consumer_files,producerSourceManifestSha256=sha(Q/'inputs.json'),producerCriticalFiles=critical,architecture='aarch64',qt='6.8.3'))
delta={n:P/'install'/n for n,v in installed.items() if old['installedFiles'][n]!=v};assert list(delta)==['lib/qml/Avelino/libAvelino.so']
archives={'installedDelta':archive('installed-delta',{'install/'+n:p for n,p in delta.items()})}
archives.update(chunks('runtime-images-',{'runtime/'+str(p.relative_to(U/'display-evidence')):p for p in (U/'display-evidence').rglob('*.png')}))
records=[]
for p in sorted((D/'catalogs').glob('*.png')):
 if p.name.startswith('charts-'):continue
 before=OLD/'catalogs'/p.name;meta=Path(str(p)+'.json');oldmeta=Path(str(before)+'.json')
 record=dict(path=p.name,pixelsIdentical=sha(p)==sha(before),metadataIdentical=sha(meta)==sha(oldmeta),previousSha256=sha(before),currentSha256=sha(p),previousMetadataSha256=sha(oldmeta),currentMetadataSha256=sha(meta));assert record['pixelsIdentical'] and record['metadataIdentical'];records.append(record)
assert len(records)==131
write(D/'regression/catalogs.json',dict(accepted=False,status='passed',previousCaptures=str(OLD/'catalogs'),currentCaptures=str(P/'catalog-evidence'),records=records))
strict={}
for p in P.glob('strict-*.png'):
 n='light-text1-dpr1-'+p.name.removeprefix('strict-');assert p.read_bytes()==(D/'captures'/n).read_bytes();strict[p.name]=dict(identicalCapture=n,sha256=sha(p))
assert len(strict)==218;write(D/'package/strict-images.json',strict)
attempts=[]
for n,code in expected.items():
 attempts.append(dict(name=n,exitCode=code,scope='First geometry test failure retained' if n=='charts-geometry-build-v1' else 'Strict native comparison retains actual failing exit' if code else 'Terminal result preserved'))
 for f in (B/n).iterdir():
  if f.is_file() and f.suffix in ['.json','.log','.py','.sh']:copy(f,D/'attempts'/n/f.name)
tree={}
for row in subprocess.check_output(['git','ls-tree','-rz','--full-tree',base],cwd=R).split(b'\0'):
 if row:head,n=row.split(b'\t',1);tree[n.decode()]=head.decode().split()[2]
base_files={};blobs={};overlays={}
for i in range(1,6):
 n=f'charts-geometry-build-v{i}';manifest=read(B/n/'inputs.json')['sourceFiles'];overlay={}
 for path,checksum in manifest.items():
  p=B/n/'source'/path;data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==checksum
  gitsha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if tree.get(path)==gitsha:base_files[path]=dict(gitObject=gitsha,sha256=checksum)
  else:overlay[path]=checksum;blobs.setdefault(checksum,p)
 overlays[n]=overlay
write(D/'replay/base-files.json',dict(baseRevision=base,files=base_files))
write(D/'replay/source-overlays.json',dict(baseRevision=base,attempts=overlays,blobMembers={n:'blobs/'+n for n in blobs},scope='Full frozen producer manifests, immutable Git base and every changed source byte. Independent-machine replay remains pending.'))
archives.update(chunks('source-blobs-',{'blobs/'+checksum:p for checksum,p in blobs.items()}))
# Early installed-consumer outputs are kept by content address; repeated bytes
# refer to canonical files, so failed and superseded attempts remain auditable.
canonical={sha(p):'candidate/'+str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()};diagnostics={};outputmap={}
for i in [1,2]:
 p=B/f'charts-geometry-package-v{i}'
 for f in (p/'results').rglob('*'):
  if f.is_file():
   checksum=sha(f);location=canonical.get(checksum)
   if location is None:diagnostics.setdefault(checksum,f);location='diagnostics/'+checksum
   outputmap[str(f.relative_to(B))]=dict(sha256=checksum,location=location)
write(D/'replay/diagnostic-outputs.json',outputmap);archives.update(chunks('diagnostic-outputs-',{'diagnostics/'+checksum:p for checksum,p in diagnostics.items()}))
images=json.loads(subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect','avelino-toolchain:data-metrics-qt6.8.3','avelino-toolchain:clipping-qt6.8.3'],text=True))
write(D/'provenance/toolchain-images.json',[{k:v[k] for k in ['Id','RepoTags','Architecture','Os','Created']} for v in images])
for n in ['build-avelino-charts-20261017.py','check-avelino-chart-geometry-focused-20261017.py','run-avelino-charts-package-20261017.py','run-avelino-chart-geometry-final-package-20261017.py','run-avelino-chart-geometry-supplement-20261017.py','run-avelino-chart-geometry-runtime-20261017.py','run-avelino-chart-geometry-operator-20261017.py','compare-avelino-chart-geometry-20261017.py','collect-avelino-charts-environment-20261017.py','seal-avelino-chart-geometry-candidate-20261017.py']:copy(Path('/Users/gaulatti/.codex/tmp')/n,D/'provenance'/n)
report=dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',baseRevision=base,accepted=False,status='verification-pending',tolerance='none',approvedExceptions=[],expectedImagesChanged=False,remainingAcceptance=['nativeGeometryAndRaster','nativeSystemFonts','nativeFractionalFontLayout','nativeNonfiniteInputDeterminism','nativeInputTiming','intrinsicProposals','physicalDisplaysInput','readers','independentMachineReferenceReplay'],canonicalComparison=read(D/'comparison/comparison.json')['summary'],supplementalComparison=read(D/'supplement-comparison/comparison.json')['summary'],validation=dict(componentChecksDpr1=15,componentChecksDpr2=15,focusedCatalogTargets=2,isolatedCatalogInputs=170,invalidInputs=8,installedFiles=133,unchangedInstalledFiles=132,independentModes=33,catalogCaptures=135,legacyPngs=131,legacyMetadata=131,virtualProfiles=8,operatorControls=14,operatorClicks=24,operatorStates=25,physicalDisplay=False,hardwareAcceleration=False),historicalFullQtSuite=dict(revision=base,targets=31,currentModuleTestedByThatRun=False),archives=archives,attempts=attempts)
report['files']={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file() and p.name not in ['candidate.json','README.md']};write(D/'candidate.json',report)
(D/'README.md').write_text('# Chart geometry correction\n\nThe installed Qt candidate preserves 1,744 canonical and 125 supplemental strict pairs, eight virtual display profiles and 25 actual X11 gallery states. All 1,469 observed source frames match; 691 observed metric sets match. Only 40 empty canonical charts match every pixel. No nonempty canonical chart or supplemental chart is accepted.\n\nThe current module passed 15 chart component checks at each DPR 1 and 2, two focused catalog targets, 33 independent package modes and 135 gallery captures. All 131 previous non-chart images and complete metadata are byte-identical. The earlier 31-target full suite belongs to revision 4184245 and is not claimed for the changed module. Earlier attempts and actual failing strict exits remain frozen.\n\nNative system fonts, adaptive axes, fractional font layout, raster, nonfinite initialization, intrinsic proposals, input timing, physical displays/input, readers and independent-machine source replay remain pending. The native supplemental corpus uses requested display scales with actual AppKit backing scale 2; it is not physical fractional-display acceptance. No source pin, expected image, tolerance or approved exception changes. See candidate.json and [the chart contract](../../../docs/charts.md).\n')
print('Sealed',len(report['files']),'files,',len(archives),'archives',report['canonicalComparison'],report['supplementalComparison'])
