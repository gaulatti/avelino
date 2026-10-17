from pathlib import Path
import gzip,hashlib,importlib.util,io,json,shutil,subprocess,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/media-library-caption-20261017';OLD=R/'evidence/development/media-library-reflow-20261017'
P=B/'media-library-caption-package-final-v1';Q=B/'media-library-caption-build-v1';U=B/'media-library-caption-runtime-v1';O=B/'media-library-caption-operator-v1';F=B/'media-library-caption-full-v1'
base='1691bbff68b2cd6ac063f09f23aeb5afc0635b4d'
N=B/'media-library-caption-fonts-v1';I=B/'media-library-caption-pills-v1';T=B/'media-library-caption-formatted-runtime-v1';C=B/'media-library-caption-formatted-comparison-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
builds=['media-library-caption-trace-build-v1','media-library-caption-offset-build-v1','media-library-caption-glyph-trace-build-v1','media-library-caption-glyph-trace-build-v2','media-library-caption-build-v1']
packages=['media-library-caption-package-final-v1','media-library-caption-fonts-v1','media-library-caption-pills-v1']
diagnostic_outputs=['media-library-caption-trace-operator-v1','media-library-caption-glyph-trace-operator-v1','media-library-caption-session-v1','media-library-caption-offset-session-v1']
expected={**dict(zip(builds,[0,0,1,0,0])),**{name:0 for name in packages},'media-library-caption-regression-v1':0,'media-library-caption-regression-v2':2,'media-library-caption-full-v1':0,'media-library-caption-runtime-v1':0,'media-library-caption-formatted-runtime-v1':0,'media-library-caption-operator-v1':0,'media-library-caption-comparison-v1':1,'media-library-caption-trace-operator-v1':1,'media-library-caption-glyph-trace-operator-v1':1,'media-library-caption-session-v1':0,'media-library-caption-offset-session-v1':0,'media-library-caption-formatted-comparison-v1':0}
for name,code in expected.items():assert read(B/name/'result.json')['exitCode']==code,(name,read(B/name/'result.json'))
assert len(read(O/'result.json')['records'])==24
assert not D.exists();D.mkdir()
def archive(key,files):
 assert files and sum(p.stat().st_size for p in files.values())<48*1024*1024,key
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
for source,target in [(P/'captures','captures'),(P/'catalog-evidence','catalogs'),(B/'media-library-caption-comparison-v1/results','comparison')]:shutil.copytree(source,D/target)
for name in ['inputs.json','environment.json','environment-seed.json','steps.json','result.json','0.log','1.log','2.log','run.log','run.py','check-installed.sh','check-installed-catalog.sh','collect-environment.py','strict.json']:copy(P/name,D/'package'/name)
for name in ['run.log','result.json','inputs.json']:copy(Q/name,D/'qt'/name)
for name in ['run.log','result.json']:copy(F/name,D/'qt/full'/name)
copy(Q/'build/Testing/Temporary/LastTest.log',D/'qt/LastTest.log')
ninja=(Q/'build/build.ninja').read_text().splitlines();index=next(i for i,line in enumerate(ninja)if 'medialibrarybase.cpp.o:'in line)
(D/'qt/floating-point-build-rule.txt').write_text('\n'.join(ninja[index:index+12])+'\n');assert '-ffp-contract=off'in(D/'qt/floating-point-build-rule.txt').read_text()
for name in ['inputs.json','result.json','run.log','replay.sh','environment.json']:copy(U/name,D/'runtime-proof'/name)
for p in(U/'display-evidence').rglob('*'):
 if p.is_file()and p.suffix!='.png':copy(p,D/'runtime'/p.relative_to(U/'display-evidence'))
for p in O.rglob('*'):
 if p.is_file()and 'install'not in p.relative_to(O).parts:copy(p,D/'operator'/p.relative_to(O))
installed={str(p.relative_to(P/'install')):sha(p)for p in(P/'install').rglob('*')if p.is_file()}
for p in [Q,U,O,N,I,T]:assert{str(f.relative_to(p/'install')):sha(f)for f in(p/'install').rglob('*')if f.is_file()}==installed,p
consumer=sha(P/'consumer-build/InstalledConsumer');assert consumer==sha(U/'consumer-build/InstalledConsumer')==sha(I/'consumer-build/InstalledConsumer')==sha(T/'consumer-build/InstalledConsumer')
consumer_files={str(p.relative_to(P/'consumer')):sha(p)for p in(P/'consumer').rglob('*')if p.is_file()};assert all(sha(R/'tests/consumer'/name)==checksum for name,checksum in consumer_files.items())
producer=read(Q/'inputs.json')['sourceFiles'];critical={name:value for name,value in producer.items()if name.startswith(('src/','samples/','assets/','tokens/','cmake/','tests/components/','tests/consumer/'))or name in['CMakeLists.txt','CMakePresets.json']};assert all(sha(R/name)==value for name,value in critical.items())
assert not any('__pycache__'in Path(name).parts or name.endswith('.pyc')for name in producer)
write(D/'package/artifact-binding.json',dict(installedFiles=installed,consumerSha256=consumer,consumerFiles=consumer_files,projectionSha256=sha(R/'tests/consumer/native-media-library-witnesses.json'),producerSourceManifestSha256=sha(Q/'inputs.json'),producerCriticalFiles=critical,architecture='aarch64',qt='6.8.3'))
archives=chunks('installed-package-',{'install/'+name:P/'install'/name for name in installed}|{'consumer-build/InstalledConsumer':P/'consumer-build/InstalledConsumer'})
archives.update(chunks('runtime-images-',{'runtime/'+str(p.relative_to(U/'display-evidence')):p for p in(U/'display-evidence').rglob('*.png')}))
records=[]
for p in sorted((D/'catalogs').glob('*.png')):
 before=OLD/'catalogs'/p.name;meta=Path(str(p)+'.json');oldmeta=Path(str(before)+'.json')
 record=dict(path=p.name,pixelsIdentical=sha(p)==sha(before),metadataIdentical=sha(meta)==sha(oldmeta),previousSha256=sha(before),currentSha256=sha(p),previousMetadataSha256=sha(oldmeta),currentMetadataSha256=sha(meta));assert record['pixelsIdentical']and record['metadataIdentical'],record;records.append(record)
assert len(records)==139
write(D/'regression/catalogs.json',dict(accepted=False,status='passed',previousCaptures=str(OLD/'catalogs'),currentCaptures=str(P/'catalog-evidence'),records=records))
old=read(OLD/'comparison/comparison.json');new=read(D/'comparison/comparison.json');previous={r['fixture']:r for r in old['results']};current={r['fixture']:r for r in new['results']};assert previous.keys()==current.keys()
regressions=[dict(fixture=name,observation=key)for name,before in previous.items()for key in['pixelStatus','nativeFrameStatus','nativeLifecycleStatus','stateStatus','retainedRasterStatus']if before[key]=='passed'and current[name][key]!='passed'];assert not regressions
write(D/'regression/native-pairs.json',dict(accepted=False,comparedPairs=len(current),previousComparisonSha256=sha(OLD/'comparison/comparison.json'),currentComparisonSha256=sha(D/'comparison/comparison.json'),regressions=regressions,previousSummary=old['summary'],currentSummary=new['summary']))
strict={}
for p in P.glob('strict-*.png'):
 name='light-text1-dpr1-'+p.name.removeprefix('strict-');strict[p.name]=dict(identicalCapture=name,sha256=sha(p),identical=p.read_bytes()==(D/'captures'/name).read_bytes())
assert len(strict)==201;write(D/'package/strict-images.json',strict)
attempts=[]
for name,code in expected.items():
 attempts.append(dict(name=name,exitCode=code,status='passed'if code==0 else'failed',scope='Actual terminal result; native differences remain pending; earlier retained raster failures are preserved as historical observations'))
 for f in(B/name).iterdir():
  if f.is_file()and f.suffix in['.json','.log','.py','.sh','.qml']:copy(f,D/'attempts'/name/f.name)
tree={}
for row in subprocess.check_output(['git','ls-tree','-rz','--full-tree',base],cwd=R).split(b'\0'):
 if row:head,name=row.split(b'\t',1);tree[name.decode()]=head.decode().split()[2]
base_files={};blobs={};overlays={};audited=set()
spec=importlib.util.spec_from_file_location('boundary',R/'scripts/check-linux-boundary.py');boundary=importlib.util.module_from_spec(spec);spec.loader.exec_module(boundary)
for name in builds:
 manifest=read(B/name/'inputs.json')['sourceFiles'];overlay={}
 for path,checksum in manifest.items():
  p=B/name/'source'/path;data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==checksum
  if(path,checksum)not in audited:
   assert not boundary.inspect_payload(path,data),(name,path);audited.add((path,checksum))
  gitsha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if tree.get(path)==gitsha:base_files[path]=dict(gitObject=gitsha,sha256=checksum)
  else:overlay[path]=checksum;blobs.setdefault(checksum,p)
 overlays[name]=overlay
write(D/'provenance/source-path-audit.json',dict(exitCode=0,pathsAndPayloads=len(audited),scope='Every distinct frozen producer path and payload inspected with the Linux boundary rules, before content-addressed archival.'))
write(D/'replay/base-files.json',dict(baseRevision=base,files=base_files))
write(D/'replay/source-overlays.json',dict(baseRevision=base,attempts=overlays,blobMembers={name:'blobs/'+name for name in blobs},scope='Complete frozen producer source manifests, immutable Git base and every changed source byte. Independent-machine replay remains pending.'))
package_inputs={}
for name in packages:
 manifest=read(B/name/'inputs.json');package_inputs[name]=manifest
 for path,checksum in manifest.items():
  p=B/name/path;assert sha(p)==checksum;blobs.setdefault(checksum,p)
write(D/'replay/package-inputs.json',package_inputs)
archives.update(chunks('source-blobs-',{'blobs/'+checksum:p for checksum,p in blobs.items()}))
canonical={sha(p):'candidate/'+str(p.relative_to(D))for p in D.rglob('*')if p.is_file()};diagnostics={};outputmap={}
for name in diagnostic_outputs:
 for f in (B/name).rglob('*'):
  if f.is_file()and 'install'not in f.relative_to(B/name).parts:
   checksum=sha(f);location=canonical.get(checksum)
   if location is None:diagnostics.setdefault(checksum,f);location='diagnostics/'+checksum
   outputmap[str(f.relative_to(B))]=dict(sha256=checksum,location=location)
write(D/'replay/diagnostic-outputs.json',outputmap);archives.update(chunks('diagnostic-outputs-',{'diagnostics/'+checksum:p for checksum,p in diagnostics.items()}))
images=json.loads(subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect','avelino-toolchain:data-metrics-qt6.8.3','avelino-toolchain:clipping-qt6.8.3'],text=True))
write(D/'provenance/toolchain-images.json',[{key:value[key]for key in['Id','RepoTags','Architecture','Os','Created']}for value in images])
for name in ['build-avelino-media-library-20261017.py','build-avelino-media-caption-trace-20261017.py','build-avelino-media-caption-offset-20261017.py','build-avelino-media-caption-glyph-trace-20261017.py','build-avelino-media-caption-glyph-trace-v2-20261017.py','run-avelino-media-caption-trace-operator-20261017.py','run-avelino-media-caption-glyph-trace-operator-20261017.py','probe-avelino-media-caption-session-20261017.py','probe-avelino-media-caption-offset-session-20261017.py','run-avelino-media-caption-final-package-20261017.py','run-avelino-media-caption-full-20261017.py','run-avelino-media-caption-runtime-20261017.py','run-avelino-media-caption-formatted-runtime-20261017.py','run-avelino-media-caption-operator-20261017.py','run-avelino-media-caption-fonts-20261017.py','run-avelino-media-caption-pills-20261017.py','compare-avelino-media-caption-20261017.py','compare-avelino-media-caption-formatted-20261017.py','collect-avelino-media-library-environment-20261017.py','seal-avelino-media-library-caption-20261017.py']:
 p=Path('/Users/gaulatti/.codex/tmp')/name
 assert p.exists(),name
 copy(p,D/'provenance'/name)
write(D/'provenance/qt-source.json',dict(qt='6.8.3',sources=['https://raw.githubusercontent.com/qt/qtdeclarative/v6.8.3/src/quick/items/qquicktext.cpp','https://raw.githubusercontent.com/qt/qtdeclarative/v6.8.3/src/quick/items/qquicktext_p_p.h','https://raw.githubusercontent.com/qt/qtdeclarative/v6.8.3/src/quick/items/qquickwindow.cpp','https://raw.githubusercontent.com/qt/qtdeclarative/v6.8.3/src/quick/scenegraph/qsgthreadedrenderloop.cpp','https://raw.githubusercontent.com/qt/qtdeclarative/v6.8.3/src/quick/scenegraph/adaptations/software/qsgsoftwarerenderloop.cpp','https://raw.githubusercontent.com/qt/qtdeclarative/v6.8.3/src/quick/scenegraph/adaptations/software/qsgsoftwareglyphnode.cpp'],scope='Exact-version layout and renderer investigation. Private probes stay diagnostic; the product correction uses public Text.forceLayout. No Qt source is copied into the tree.'))
for name in ['inputs.json','result.json','run.log','replay.sh','environment.json']:copy(T/name,D/'formatted-runtime-proof'/name)
for f in(T/'display-evidence').rglob('*'):
 if f.is_file()and f.suffix!='.png':copy(f,D/'formatted-runtime'/f.relative_to(T/'display-evidence'))
archives.update(chunks('formatted-runtime-images-',{'formatted-runtime/'+str(f.relative_to(T/'display-evidence')):f for f in(T/'display-evidence').rglob('*.png')}))
copy(C/'regression.json',D/'formatted/native-regression.json')
auxiliary={}
for kind,folder in [('font',N),('pill',I)]:
 for f in(folder/'captures').rglob('*'):
  if f.is_file():auxiliary[kind+'-captures/'+str(f.relative_to(folder/'captures'))]=f
for kind,folder in [('font',C/'fonts'),('pill',C/'pills')]:
 copy(folder/'comparison.json',D/'formatted'/(kind+'-comparison.json'))
 for f in folder.rglob('*'):
  if f.is_file():auxiliary[kind+'-comparison/'+str(f.relative_to(folder))]=f
archives.update(chunks('formatted-observations-',auxiliary))
# The first regression falsely passed with the fresh caller still covering the
# retained caller. The second separates window grabs and exposes two failures.
write(D/'regression/diagnostic-scope.json',dict(accepted=False,overlappingCaptureAttempt='media-library-caption-regression-v1',separatedCaptureAttempt='media-library-caption-regression-v2',separatedFailures=['Tile 2 right aligned at 222','Tile 5 centered at 222'],freshSessionCaptures=48,freshOffsetCaptures=48,sourceAndBuildAbsentAtOperator=True))
operator=read(O/'result.json');summary=new['summary']
write(D/'qt/full/module-binding.json',dict(fullSuiteProducer=Q.name,finalProducer=Q.name,installedFilesIdentical=installed,scope='Full suite, final package, virtual runtime and operator use the same frozen producer and identical installed bytes.'))
report=dict(reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',baseRevision=base,previousCandidateSha256=sha(OLD/'candidate.json'),accepted=False,status='verification-pending',tolerance='none',approvedExceptions=[],expectedImagesChanged=False,remainingAcceptance=['nativeGeometryAndRaster','retainedCallerRasterStability','nativeSizingAndWitnessDifference','nativeLazyViewportTiming','nativeGenericIDContexts','nativeInputTiming','physicalDisplaysInput','readers','independentMachineReferenceReplay'],strictComparison=summary,strictComparisonStatus='failed',validation=dict(componentChecksDpr1=15,componentChecksDpr2=15,formattedTextChecksDpr1=16,formattedTextChecksDpr2=16,fullQtTargets=33,malformedConfigurations=13,isolatedCatalogInputs=76,installedFiles=len(installed),independentModes=34,catalogCaptures=139,legacyPngs=139,legacyMetadata=139,virtualProfiles=8,formattedVirtualProfiles=16,formattedFontCases=1656,formattedPillCases=2112,operatorControls=14,operatorClicks=23,operatorStates=24,operatorExactStates=sum(r['passed']for r in operator['records']),operatorStatus=operator['status'],strictDefaultExitCode=1,strictImageExitCode=1,fatalProcesses=8,virtualRestoreObservations=48,virtualRestorePixelMatches=48,physicalDisplay=False,hardwareAcceleration=False),archives=archives,attempts=attempts,diagnostics=dict(painterWarnings='No QPainter::begin warnings in current eight capture contexts; earlier diagnostic warnings are preserved',directSizing='All 7440 public responses and both witness branches retained; no Linux direct-proposal observations',retainedRaster='All 48 virtual media restore observations and all 24 actual XTest gallery states match. Native and complete mirror acceptance remain pending.'))
report['formattedComparisons']={kind:read(D/'formatted'/(kind+'-comparison.json'))['summary']for kind in['font','pill']}
report['formattedPreviousSha256']={kind:sha(R/path/'comparison/comparison.json')for kind,path in[('font','evidence/development/font-modifier'),('pill','evidence/development/pill-modifier-20261017')]}
report['files']={str(p.relative_to(D)):sha(p)for p in D.rglob('*')if p.is_file()and p.name not in['candidate.json','README.md']};write(D/'candidate.json',report)
(D/'README.md').write_text('# Formatted text reflow correction\n\nAll 24 actual XTest gallery states now match fresh callers. The old module reproduces two pixel failures in the separated-capture regression; the correction passes all 14 text/alignment rows at DPR 1 and 2. Qt 6.8.3 retains a fractional line layout on width growth, so the formatted wrapper now calls the public forceLayout method at the current width. Failed helper and capture attempts remain preserved.\n\nAll 1608 native media comparisons remain strict: 1008 complete matches, 1168 pixel matches, 1288 frame matches and all 1608 lifecycle matches. No earlier passing observation regressed. All 139 earlier catalog images and metadata remain identical. Full Qt, installed package and virtual media/font/pill profiles are recorded separately from physical display, hardware acceleration, input and reader acceptance.\n\nThe complete 1656 font and 2112 pill corpora are captured and compared with unchanged native sources. Every mismatch remains visible. Pins, expected images, tolerances and exceptions are unchanged; direct sizing and complete mirror acceptance remain pending. See [the grid contract](../../../docs/media-library.md).\n')
print('Sealed',len(report['files']),'files',len(archives),'archives',summary,report['validation'])
