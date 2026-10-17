from pathlib import Path
import gzip,hashlib,io,json,shutil,subprocess,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/media-library-20261017';OLD=R/'evidence/development/chart-geometry-20261017'
P=B/'media-library-package-final-v3';Q=B/'media-library-build-v10';U=B/'media-library-runtime-v3';O=B/'media-library-operator-v2'
base='616abb40affb769029f80144a2f0807c79679f44'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
expected={**{f'media-library-build-v{i}':{1:1,2:134,3:9}.get(i,0) for i in range(1,11)},'media-library-package-v1':0,'media-library-package-v2':0,'media-library-package-final-v1':0,'media-library-package-final-v2':0,'media-library-package-final-v3':0,'media-library-full-v1':8,'media-library-full-v2':0,'media-library-runtime-v1':1,'media-library-runtime-v2':1,'media-library-runtime-v3':0,'media-library-operator-v2':1,'media-library-comparison-v1':1,**{f'media-library-probe-v{i}':{1:134,2:1}.get(i,0) for i in range(1,5)}}
for name,code in expected.items():assert read(B/name/'result.json')['exitCode']==code,(name,read(B/name/'result.json'))
assert len(read(O/'result.json')['records'])==24
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
for source,target in [(P/'captures','captures'),(P/'catalog-evidence','catalogs'),(B/'media-library-comparison-v1/results','comparison')]:shutil.copytree(source,D/target)
for name in ['inputs.json','environment.json','environment-seed.json','steps.json','result.json','0.log','1.log','2.log','run.log','run.py','check-installed.sh','check-installed-catalog.sh','collect-environment.py','strict.json']:copy(P/name,D/'package'/name)
for name in ['run.log','result.json','inputs.json']:copy(Q/name,D/'qt'/name)
for name in ['run.log','result.json']:copy(B/'media-library-full-v2'/name,D/'qt/full'/name)
copy(B/'media-library-build-v9/build/Testing/Temporary/LastTest.log',D/'qt/LastTest.log')
ninja=(Q/'build/build.ninja').read_text().splitlines();index=next(i for i,line in enumerate(ninja) if 'medialibrarybase.cpp.o:' in line)
(D/'qt/floating-point-build-rule.txt').write_text('\n'.join(ninja[index:index+12])+'\n');assert '-ffp-contract=off' in (D/'qt/floating-point-build-rule.txt').read_text()
for name in ['inputs.json','result.json','run.log','replay.sh','environment.json']:copy(U/name,D/'runtime-proof'/name)
for p in (U/'display-evidence').rglob('*'):
 if p.is_file() and p.suffix!='.png':copy(p,D/'runtime'/p.relative_to(U/'display-evidence'))
for p in O.rglob('*'):
 if p.is_file() and 'install' not in p.relative_to(O).parts:copy(p,D/'operator'/p.relative_to(O))
installed={str(p.relative_to(P/'install')):sha(p) for p in (P/'install').rglob('*') if p.is_file()}
for p in [Q,U,O,B/'media-library-build-v9']:assert {str(f.relative_to(p/'install')):sha(f) for f in (p/'install').rglob('*') if f.is_file()}==installed,p
consumer=sha(P/'consumer-build/InstalledConsumer');assert consumer==sha(U/'consumer-build/InstalledConsumer')
consumer_files={str(p.relative_to(P/'consumer')):sha(p) for p in (P/'consumer').rglob('*') if p.is_file()};assert all(sha(R/'tests/consumer'/name)==checksum for name,checksum in consumer_files.items())
producer=read(Q/'inputs.json')['sourceFiles'];critical={name:value for name,value in producer.items() if name.startswith(('src/','samples/','assets/','tokens/','cmake/','tests/components/','tests/consumer/')) or name in ['CMakeLists.txt','CMakePresets.json']};assert all(sha(R/name)==value for name,value in critical.items())
write(D/'package/artifact-binding.json',dict(installedFiles=installed,consumerSha256=consumer,consumerFiles=consumer_files,projectionSha256=sha(R/'tests/consumer/native-media-library-witnesses.json'),producerSourceManifestSha256=sha(Q/'inputs.json'),producerCriticalFiles=critical,architecture='aarch64',qt='6.8.3'))
archives=chunks('installed-package-',{'install/'+name:P/'install'/name for name in installed}|{'consumer-build/InstalledConsumer':P/'consumer-build/InstalledConsumer'})
archives.update(chunks('runtime-images-',{'runtime/'+str(p.relative_to(U/'display-evidence')):p for p in (U/'display-evidence').rglob('*.png')}))
prior_runtime=B/'media-library-runtime-v1/display-evidence'
for p in prior_runtime.rglob('*'):
 if p.is_file() and p.suffix!='.png':copy(p,D/'attempts/media-library-runtime-v1/display-evidence'/p.relative_to(prior_runtime))
archives.update(chunks('prior-runtime-images-',{'prior-runtime/'+str(p.relative_to(prior_runtime)):p for p in prior_runtime.rglob('*.png')}))
second_runtime=B/'media-library-runtime-v2/display-evidence'
for p in second_runtime.rglob('*'):
 if p.is_file() and p.suffix!='.png':copy(p,D/'attempts/media-library-runtime-v2/display-evidence'/p.relative_to(second_runtime))
archives.update(chunks('second-runtime-images-',{'second-runtime/'+str(p.relative_to(second_runtime)):p for p in second_runtime.rglob('*.png')}))
records=[]
for p in sorted((D/'catalogs').glob('*.png')):
 if p.name.startswith('media-library-'):continue
 before=OLD/'catalogs'/p.name;meta=Path(str(p)+'.json');oldmeta=Path(str(before)+'.json')
 record=dict(path=p.name,pixelsIdentical=sha(p)==sha(before),metadataIdentical=sha(meta)==sha(oldmeta),previousSha256=sha(before),currentSha256=sha(p),previousMetadataSha256=sha(oldmeta),currentMetadataSha256=sha(meta));assert record['pixelsIdentical'] and record['metadataIdentical'],record;records.append(record)
assert len(records)==135
write(D/'regression/catalogs.json',dict(accepted=False,status='passed',previousCaptures=str(OLD/'catalogs'),currentCaptures=str(P/'catalog-evidence'),records=records))
strict={}
for p in P.glob('strict-*.png'):
 name='light-text1-dpr1-'+p.name.removeprefix('strict-');strict[p.name]=dict(identicalCapture=name,sha256=sha(p),identical=p.read_bytes()==(D/'captures'/name).read_bytes())
assert len(strict)==201;write(D/'package/strict-images.json',strict)
attempts=[]
for name,code in expected.items():
 attempts.append(dict(name=name,exitCode=code,status='passed' if code==0 else 'failed',scope='Actual terminal result; native comparison and retained raster failures remain pending'))
 for f in (B/name).iterdir():
  if f.is_file() and f.suffix in ['.json','.log','.py','.sh','.qml']:copy(f,D/'attempts'/name/f.name)
# The first operator attempt stopped at its first exact-pixel difference.
for f in (B/'media-library-operator-v1').rglob('*'):
 if f.is_file() and 'install' not in f.relative_to(B/'media-library-operator-v1').parts:copy(f,D/'attempts/media-library-operator-v1'/f.relative_to(B/'media-library-operator-v1'))
attempts.append(dict(name='media-library-operator-v1',exitCode=1,status='failed',scope='Stopped at width336; actual strict mismatch and earlier observations retained'))
tree={}
for row in subprocess.check_output(['git','ls-tree','-rz','--full-tree',base],cwd=R).split(b'\0'):
 if row:head,name=row.split(b'\t',1);tree[name.decode()]=head.decode().split()[2]
base_files={};blobs={};overlays={}
for i in range(1,11):
 name=f'media-library-build-v{i}';manifest=read(B/name/'inputs.json')['sourceFiles'];overlay={}
 for path,checksum in manifest.items():
  p=B/name/'source'/path;data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==checksum
  gitsha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if tree.get(path)==gitsha:base_files[path]=dict(gitObject=gitsha,sha256=checksum)
  else:overlay[path]=checksum;blobs.setdefault(checksum,p)
 overlays[name]=overlay
write(D/'replay/base-files.json',dict(baseRevision=base,files=base_files))
write(D/'replay/source-overlays.json',dict(baseRevision=base,attempts=overlays,blobMembers={name:'blobs/'+name for name in blobs},scope='Complete frozen producer source manifests, immutable Git base and every changed source byte. Independent-machine replay remains pending.'))
package_inputs={}
for name in ['media-library-package-v1','media-library-package-v2','media-library-package-final-v1','media-library-package-final-v2','media-library-package-final-v3']:
 manifest=read(B/name/'inputs.json');package_inputs[name]=manifest
 for path,checksum in manifest.items():
  p=B/name/path;assert sha(p)==checksum
  blobs.setdefault(checksum,p)
write(D/'replay/package-inputs.json',package_inputs)
archives.update(chunks('source-blobs-',{'blobs/'+checksum:p for checksum,p in blobs.items()}))
canonical={sha(p):'candidate/'+str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()};diagnostics={};outputmap={}
for name in ['media-library-package-v1','media-library-package-v2']:
 for f in (B/name/'results').rglob('*'):
  if f.is_file():
   checksum=sha(f);location=canonical.get(checksum)
   if location is None:diagnostics.setdefault(checksum,f);location='diagnostics/'+checksum
   outputmap[str(f.relative_to(B))]=dict(sha256=checksum,location=location)
write(D/'replay/diagnostic-outputs.json',outputmap);archives.update(chunks('diagnostic-outputs-',{'diagnostics/'+checksum:p for checksum,p in diagnostics.items()}))
images=json.loads(subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect','avelino-toolchain:data-metrics-qt6.8.3','avelino-toolchain:clipping-qt6.8.3'],text=True))
write(D/'provenance/toolchain-images.json',[{key:value[key] for key in ['Id','RepoTags','Architecture','Os','Created']} for value in images])
for name in ['build-avelino-media-library-20261017.py','run-avelino-media-library-package-20261017.py','run-avelino-media-library-final-package-20261017.py','run-avelino-media-library-full-20261017.py','run-avelino-media-library-runtime-20261017.py','run-avelino-media-library-runtime-v2-20261017.py','run-avelino-media-library-runtime-v3-20261017.py','run-avelino-media-library-final-package-v3-20261017.py','run-avelino-media-library-operator-20261017.py','collect-avelino-charts-environment-20261017.py','seal-avelino-media-library-candidate-20261017.py','compare-avelino-media-library-20261017.py']:copy(Path('/Users/gaulatti/.codex/tmp')/name,D/'provenance'/name)
operator=read(O/'result.json');summary=read(D/'comparison/comparison.json')['summary']
write(D/'qt/full/module-binding.json',dict(fullSuiteProducer='media-library-build-v9',finalProducer='media-library-build-v10',installedFilesIdentical=installed,scope='Only installed-consumer diagnostic/report code changed after the full module suite; every installed module/catalog byte is identical.'))
report=dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',baseRevision=base,accepted=False,status='verification-pending',tolerance='none',approvedExceptions=[],expectedImagesChanged=False,remainingAcceptance=['nativeGeometryAndRaster','retainedCallerRasterStability','nativeSizingAndWitnessDifference','nativeLazyViewportTiming','nativeGenericIDContexts','nativeInputTiming','physicalDisplaysInput','readers','independentMachineReferenceReplay'],strictComparison=summary,strictComparisonStatus='failed',validation=dict(componentChecksDpr1=11,componentChecksDpr2=11,fullQtTargets=33,malformedConfigurations=13,isolatedCatalogInputs=76,installedFiles=len(installed),independentModes=34,catalogCaptures=139,legacyPngs=135,legacyMetadata=135,virtualProfiles=8,operatorControls=14,operatorClicks=23,operatorStates=24,operatorExactStates=sum(r['passed'] for r in operator['records']),operatorStatus=operator['status'],strictDefaultExitCode=1,strictImageExitCode=1,fatalProcesses=8,physicalDisplay=False,hardwareAcceleration=False),archives=archives,attempts=attempts,diagnostics=dict(painterWarnings='Preserved raw Qt QPainter inactive-device warnings; their origin is unresolved and raster acceptance remains pending',directSizing='All 7440 public responses and both witness branches retained; no Linux direct-proposal observations',virtualRestore='Wayland software standard/scaled window grabs differ after restoring width-337 fill tiles; all frames preserved'))
report['files']={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file() and p.name not in ['candidate.json','README.md']};write(D/'candidate.json',report)
(D/'README.md').write_text('# MediaLibrary Linux candidate\n\nThe candidate keeps all 1608 native pixel/frame/lifecycle pairs, eight isolated fatal outcomes and 7440 public sizing responses. Direct sizing remains unobserved. Every strict failure is preserved. The native pin, expected images, tolerance and exception list are unchanged.\n\nThe current module passes 11 focused checks at DPR 1 and 2, 33 full Qt targets, 13 malformed configurations, 76 isolated catalog inputs and 34 installed package modes. All 135 earlier catalog images and complete metadata remain byte-identical. Eight virtual X11/Wayland profiles use software rendering; they do not establish physical display/input or hardware acceleration acceptance.\n\nActual XTest gallery input exercises 14 controls through 24 states. Five retained RTL caption states differ from fresh isolated candidates; these remain failed. Native fractional/text geometry, lazy height estimates, direct sizing, generic native identity contexts, raster, input timing, physical displays, readers and independent-machine replay remain pending. Raw Qt painter warnings remain visible. See candidate.json and [the grid contract](../../../docs/media-library.md).\n')
print('Sealed',len(report['files']),'files',len(archives),'archives',summary,report['validation'])
