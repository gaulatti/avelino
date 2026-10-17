from pathlib import Path
import gzip,hashlib,importlib.util,io,json,shutil,subprocess,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/app-tabs-20261017'
P=B/'app-tabs-matrix-package-v3';Q=B/'app-tabs-build-v9';U=B/'app-tabs-runtime-v2';O=B/'app-tabs-operator-v1';C=B/'app-tabs-readiness-v1';F=B/'app-tabs-full-v2'
base='685f7442cb87785aea6563c2817ea4f28845816e';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
expected={**{f'app-tabs-build-v{i}':0 for i in range(1,10)},'app-tabs-package-pilot-v1':99,'app-tabs-package-pilot-v2':0,'app-tabs-matrix-package-v1':1,'app-tabs-matrix-package-v2':0,'app-tabs-matrix-package-v3':0,'app-tabs-full-v1':8,'app-tabs-full-v2':0,'app-tabs-runtime-v1':1,'app-tabs-runtime-v2':0,'app-tabs-readiness-v1':0,'app-tabs-operator-v1':1,'app-tabs-disabled-diagnostic-v1':0,'app-tabs-disabled-repaint-v1':1}
for name,code in expected.items():assert read(B/name/'result.json')['exitCode']==code,(name,code)
assert not D.exists();D.mkdir()
def archive(key,files):
 assert sum(p.stat().st_size for p in files.values())<48*1024*1024,key
 manifest={};path=D/(key+'.tar.gz')
 with path.open('xb')as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0)as gz,tarfile.open(fileobj=gz,mode='w')as stream:
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
for source,target in [(P/'captures','captures'),(C/'catalog-evidence','catalogs')]:shutil.copytree(source,D/target)
copy(P/'comparison.json',D/'comparison.json');copy(B/'app-tabs-native-offset.json',D/'native-offset.json')
for name in ['inputs.json','steps.json','result.json','0.log','1.log','2.log','3.log','4.log','run.log','run.py','strict.json','gallery.png','gallery.png.json']:copy(P/name,D/'package'/name)
for name in ['run.log','result.json','inputs.json']:copy(Q/name,D/'qt'/name)
for name in ['run.log','result.json']:copy(F/name,D/'qt/full'/name)
copy(B/'app-tabs-build-v7/build/Testing/Temporary/LastTest.log',D/'qt/full/LastTest.log')
copy(B/'app-tabs-build-v8/build/Testing/Temporary/LastTest.log',D/'qt/catalog/LastTest.log')
for name in ['inputs.json','result.json','run.log','replay.sh','environment.json','collect-environment.py']:copy(U/name,D/'runtime-proof'/name)
for name in ['inputs.json','result.json','run.log','environment.json','check-installed.sh','check-installed-catalog.sh','collect-environment.py']:copy(C/name,D/'readiness'/name)
for p in (U/'display-evidence').rglob('*'):
 if p.is_file()and p.suffix!='.png':copy(p,D/'runtime'/p.relative_to(U/'display-evidence'))
for p in O.rglob('*'):
 if p.is_file()and 'install'not in p.relative_to(O).parts:copy(p,D/'operator'/p.relative_to(O))
installed={str(p.relative_to(P/'install')):sha(p)for p in(P/'install').rglob('*')if p.is_file()}
for p in [Q,U,O,C,B/'app-tabs-build-v7',B/'app-tabs-build-v8']:
 assert{str(f.relative_to(p/'install')):sha(f)for f in(p/'install').rglob('*')if f.is_file()}==installed,p
consumer=sha(P/'consumer-build/InstalledConsumer');assert consumer==sha(U/'consumer-build/InstalledConsumer')==sha(C/'consumer-build/InstalledConsumer')
consumer_files={str(p.relative_to(P/'consumer')):sha(p)for p in(P/'consumer').rglob('*')if p.is_file()};assert all(sha(R/'tests/consumer'/n)==s for n,s in consumer_files.items())
producer=read(Q/'inputs.json')['sourceFiles'];critical={n:s for n,s in producer.items()if n.startswith(('src/','samples/','assets/','tokens/','cmake/','tests/components/','tests/consumer/'))or n in['CMakeLists.txt','CMakePresets.json']};assert all(sha(R/n)==s for n,s in critical.items())
write(D/'package/artifact-binding.json',dict(installedFiles=installed,consumerSha256=consumer,consumerFiles=consumer_files,projectionSha256=sha(R/'tests/consumer/native-app-tabs-witnesses.json'),iconMetricsSha256=sha(R/'tests/consumer/native-app-tab-icon-metrics.json'),producerSourceManifestSha256=sha(Q/'inputs.json'),producerCriticalFiles=critical,architecture='aarch64',qt='6.8.3'))
write(D/'qt/full/module-binding.json',dict(fullSuiteProducer='app-tabs-build-v7',finalProducer='app-tabs-build-v9',installedFilesIdentical=installed,scope='All 34 original targets used v7. The additional catalog target passed separately on v8. Installed module and catalog bytes are identical across v7, v8 and v9; later changes affect test registration and consumer report metadata.'))
archives=chunks('installed-package-',{'install/'+n:P/'install'/n for n in installed}|{'consumer-build/InstalledConsumer':P/'consumer-build/InstalledConsumer'})
archives.update(chunks('runtime-images-',{'runtime/'+str(p.relative_to(U/'display-evidence')):p for p in(U/'display-evidence').rglob('*.png')}))
records=[];old=R/'evidence/development/media-library-caption-20261017/catalogs'
for p in sorted(old.glob('*.png')):
 meta=Path(str(p)+'.json');current=D/'catalogs'/p.name;currentmeta=Path(str(current)+'.json')
 record=dict(path=p.name,pixelsIdentical=sha(p)==sha(current),metadataIdentical=sha(meta)==sha(currentmeta),previousSha256=sha(p),currentSha256=sha(current),previousMetadataSha256=sha(meta),currentMetadataSha256=sha(currentmeta));assert record['pixelsIdentical']and record['metadataIdentical'];records.append(record)
assert len(records)==139;write(D/'regression/catalogs.json',dict(status='passed',accepted=False,baseline='evidence/development/media-library-caption-20261017/catalogs',records=records))
strict={}
for p in P.glob('strict-*.png'):
 name='light-text1-dpr1-'+p.name.removeprefix('strict-');strict[p.name]=dict(identicalCapture=name,sha256=sha(p),identical=p.read_bytes()==(D/'captures'/name).read_bytes());assert strict[p.name]['identical']
assert len(strict)==151;write(D/'package/strict-images.json',strict)
# Every attempt receipt and complete input manifest is kept, including failed metadata/compiler probes.
attempts=[]
for name,code in expected.items():
 attempts.append(dict(name=name,exitCode=code,status='passed'if code==0 else'failed'))
 for f in(B/name).iterdir():
  if f.is_file()and f.suffix in['.json','.log','.py','.sh','.qml']:copy(f,D/'attempts'/name/f.name)
# Reconstruct complete producer sources using immutable Git files and unique changed bytes.
tree={}
for row in subprocess.check_output(['git','ls-tree','-rz','--full-tree',base],cwd=R).split(b'\0'):
 if row:head,name=row.split(b'\t',1);tree[name.decode()]=head.decode().split()[2]
base_files={};blobs={};overlays={}
for i in range(1,10):
 name=f'app-tabs-build-v{i}';manifest=read(B/name/'inputs.json')['sourceFiles'];overlay={}
 for path,checksum in manifest.items():
  p=B/name/'source'/path;data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==checksum
  gitsha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if tree.get(path)==gitsha:base_files[path]=dict(gitObject=gitsha,sha256=checksum)
  else:overlay[path]=checksum;blobs.setdefault(checksum,p)
 overlays[name]=overlay
write(D/'replay/base-files.json',dict(baseRevision=base,files=base_files));write(D/'replay/source-overlays.json',dict(baseRevision=base,attempts=overlays,blobMembers={n:'blobs/'+n for n in blobs}))
package_inputs={}
for name in expected:
 if name.startswith(('app-tabs-build-','app-tabs-full-','app-tabs-operator-','app-tabs-disabled-')):continue
 raw=read(B/name/'inputs.json');manifest=raw.get('files',raw);package_inputs[name]=manifest
 for path,checksum in manifest.items():
  p=B/name/path;assert sha(p)==checksum,(name,path);blobs.setdefault(checksum,p)
write(D/'replay/package-inputs.json',package_inputs)
archives.update(chunks('source-blobs-',{'blobs/'+checksum:p for checksum,p in blobs.items()}))
# Preserve all output attempts through content-addressed deduplication, without rewriting raw logs.
canonical={sha(p):'candidate/'+str(p.relative_to(D))for p in D.rglob('*')if p.is_file()};diagnostics={};outputmap={}
for name in expected:
 if name.startswith(('app-tabs-build-','app-tabs-full-')):continue
 for f in(B/name).rglob('*'):
  rel=f.relative_to(B/name)
  if not f.is_file()or rel.parts[0]in['install','consumer','consumer-build','driver','source','build','qt-artifacts']:continue
  checksum=sha(f);location=canonical.get(checksum)
  if location is None:diagnostics.setdefault(checksum,f);location='diagnostics/'+checksum
  outputmap[name+'/'+str(rel)]=dict(sha256=checksum,location=location)
write(D/'replay/diagnostic-outputs.json',outputmap);archives.update(chunks('diagnostic-outputs-',{'diagnostics/'+checksum:p for checksum,p in diagnostics.items()}))
images=json.loads(subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect','avelino-toolchain:data-metrics-qt6.8.3','avelino-toolchain:clipping-qt6.8.3'],text=True));write(D/'provenance/toolchain-images.json',[{k:v[k]for k in['Id','RepoTags','Architecture','Os','Created']}for v in images])
for pattern in ['build-avelino-app-tabs-*.py','run-avelino-app-tabs-*.py','prepare-avelino-app-tabs-*.py','seal-avelino-app-tabs-*.py']:
 for p in Path('/Users/gaulatti/.codex/tmp').glob(pattern):
  if p.name not in ['seal-avelino-app-tabs-source-20261017.py','prepare-avelino-app-tabs-source-replay-20261017.py']:copy(p,D/'provenance'/p.name)
operator=read(O/'result.json');summary=read(P/'comparison.json')['summary']
report=dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',baseRevision=base,accepted=False,status='verification-pending',tolerance='none',approvedExceptions=[],expectedImagesChanged=False,remainingAcceptance=['nativeGeometryRasterAndLabelFitting','retainedCallerRasterStability','nativeSizing','nativeGenericIdentity','nativeKeyboardAndInputTiming','nativeAccessibility','physicalDisplaysInput','readers','independentMachineReplay'],strictComparison=summary,strictComparisonStatus='failed',validation=dict(componentChecksDpr1=17,componentChecksDpr2=17,fullQtTargets=34,additionalCatalogTargets=1,malformedConfigurations=18,isolatedCatalogInputs=43,isolatedCatalogRefusals=26,installedFiles=len(installed),independentModes=35,catalogCaptures=143,legacyPngs=139,legacyMetadata=139,virtualProfiles=8,operatorControls=14,operatorClicks=27,operatorStates=28,operatorExactStates=sum(r['passed']for r in operator['records']),operatorStatus=operator['status'],strictDefaultExitCode=1,strictImageExitCode=1,physicalDisplay=False,hardwareAcceleration=False),archives=archives,attempts=attempts,diagnostics=dict(retainedDisabled='Two retained disabled gallery states differ from fresh isolated candidates by 109 pixels with maximum per-channel difference one; all failures retained without tolerance.',failedRuntimeMetadata='runtime-v1 failed because the report omitted dimensions and its seed environment was stale. runtime-v2 collects fresh metadata inside the actual package container.',nativeOffset='Opaque sunset bounding boxes translate exactly in RTL; whole opaque masks do not translate byte-exactly.'))
report['files']={str(p.relative_to(D)):sha(p)for p in D.rglob('*')if p.is_file()and p.name not in['candidate.json','README.md']};write(D/'candidate.json',report)
(D/'README.md').write_text('# AppTabBar Linux candidate\n\nAll 1,208 native/candidate pairs remain in strict comparison: 1,208 state observations and 940 frame sets agree; 56 empty-state images match exactly. All 48 retained restore images reproduce their initial candidate pixels. All 5,160 public sizing responses are retained, with Linux direct sizing still unobserved.\n\nThe module passes 17 focused checks at DPR 1 and 2, 34 full Qt targets, one additional catalog target, 18 malformed configurations, 43 isolated catalog definitions and 26 refusals. All 35 installed modes and 143 catalog captures run from the installed package. All 139 prior PNGs and full metadata remain unchanged. Eight virtual X11/Wayland profiles use software rendering and do not establish physical displays, hardware acceleration or reader acceptance.\n\nActual XTest gallery input exercises 14 controls through 28 states. Two retained disabled states differ from fresh candidates; their exact failures and repaint diagnostics remain preserved. Native labels, symbols, raster, broader identities, sizing, timing, accessibility, physical displays, readers and independent-machine replay remain pending. Expected images, pins, tolerances and exceptions are unchanged. See [the contract](../../../docs/app-tabs.md) and candidate.json.\n')
print('Sealed',len(report['files']),'files',len(archives),'archives',summary,report['validation'])
