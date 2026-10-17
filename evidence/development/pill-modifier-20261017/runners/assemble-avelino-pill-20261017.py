from pathlib import Path
import gzip,hashlib,io,json,re,shutil,subprocess,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/pill-modifier-20261017'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
def archive(key,files):
 assert sum(p.stat().st_size for p in files.values())<60*1024*1024
 manifest={};path=D/(key+'.tar.gz')
 with path.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as gz,tarfile.open(fileobj=gz,mode='w') as stream:
  for name,p in sorted(files.items()):
   data=p.read_bytes();info=tarfile.TarInfo(name);info.size=len(data);info.mode=p.stat().st_mode&0o777;info.mtime=0;stream.addfile(info,io.BytesIO(data));manifest[name]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),mode=info.mode)
 write(D/(key+'-manifest.json'),manifest)
 return dict(archive=path.name,manifest=key+'-manifest.json',files=len(files))
# Make terminal results prerequisites, before creating any evidence output.
P=B/'pill-package-final-v4';Q=B/'pill-full-v4';U=B/'pill-runtime-v4';O=B/'pill-operator-v5'
for p in [P,Q,U,O]:assert json.loads((p/'result.json').read_text())['exitCode']==0,p
assert json.loads((B/'pill-comparison-v4/result.json').read_text())['exitCode']==1
assert D.exists() and (D/'captures/capture-results.json').exists() and (D/'comparison/comparison.json').exists()
assert not (D/'candidate.json').exists()
shutil.copytree(P/'catalog-evidence',D/'catalogs')
for name in ['inputs.json','environment.json','environment-seed.json','steps.json','result.json','0.log','1.log','2.log','run.log','run.py','check-installed.sh','check-installed-catalog.sh','collect-environment.py','strict.json']:
 copy(P/name,D/'package'/name)
shutil.copytree(U/'display-evidence',D/'runtime')
for name in ['inputs.json','result.json','run.log','replay.sh']:copy(U/name,D/'runtime-proof'/name)
for f in O.rglob('*'):
 if f.is_file() and 'install' not in f.relative_to(O).parts:copy(f,D/'operator'/f.relative_to(O))
for name in ['run.log','result.json']:copy(Q/name,D/'qt'/name)
copy(B/'pill-build-v14/build/Testing/Temporary/LastTest.log',D/'qt/LastTest.log')
copy(B/'pill-build-v14/inputs.json',D/'qt/producer-inputs.json')
read=lambda p:json.loads(p.read_text())
installed={str(p.relative_to(P/'install')):sha(p) for p in (P/'install').rglob('*') if p.is_file()};assert len(installed)==127
for p in [B/'pill-build-v15',B/'pill-package-v13',U,O]:assert {str(f.relative_to(p/'install')):sha(f) for f in (p/'install').rglob('*') if f.is_file()}==installed,p
consumer=sha(P/'consumer-build/InstalledConsumer');assert consumer==sha(U/'consumer-build/InstalledConsumer')
producer=read(B/'pill-build-v15/inputs.json')['sourceFiles'];critical={n:v for n,v in producer.items() if n.startswith(('src/','samples/','assets/','tokens/','cmake/')) or n in ['CMakeLists.txt','CMakePresets.json','tests/consumer/PillModifierCase.qml','tests/consumer/sharprectangle.h']}
assert all(sha(R/n)==v for n,v in critical.items())
consumer_files={str(f.relative_to(P/'consumer')):sha(f) for f in (P/'consumer').rglob('*') if f.is_file()}
assert all(sha(R/'tests/consumer'/n)==v for n,v in consumer_files.items())
binding=dict(installedFiles=installed,consumerSha256=consumer,producerSourceManifestSha256=sha(B/'pill-build-v15/inputs.json'),producerCriticalFiles=critical,consumerFiles=consumer_files,architecture='aarch64',qt='6.8.3')
# The fixture paint helper changed only the catalog executable. Preserve the
# earlier full suite on the byte-identical library and component test binary,
# and the final producer's three focused catalog/configuration checks.
full_install={str(f.relative_to(B/'pill-build-v14/install')):sha(f) for f in (B/'pill-build-v14/install').rglob('*') if f.is_file()}
common={n:v for n,v in full_install.items() if v==installed[n]}
assert len(common)==126 and set(full_install)-set(common)=={'bin/AvelinoCatalog'}
component='build/tests/components/AvelinoComponentTests'
assert sha(B/'pill-build-v14'/component)==sha(B/'pill-build-v15'/component)
F=B/'pill-focused-v2';assert read(F/'result.json')['exitCode']==0
for name in ['run.log','result.json']:copy(F/name,D/'qt/focused'/name)
write(D/'qt/artifact-binding.json',dict(fullSuiteProducer='pill-build-v14',finalProducer='pill-build-v15',focusedAttempt='pill-focused-v2',fullSuiteInstalledFiles=full_install,commonInstalledFiles=common,fullSuiteComponentExecutableSha256=sha(B/'pill-build-v14'/component),finalComponentExecutableSha256=sha(B/'pill-build-v15'/component)))
write(D/'package/artifact-binding.json',binding)
write(D/'operator/artifact-binding.json',dict(installedFiles=installed,catalogSha256=installed['bin/AvelinoCatalog']))
# Preserve the default strict mode's actual images, including any differences.
strict={}
for p in P.glob('strict-*.png'):
 target='light-text1-dpr1-'+p.name.removeprefix('strict-');q=D/'captures'/target
 if q.exists() and p.read_bytes()==q.read_bytes():strict[p.name]=dict(identicalCapture=target,sha256=sha(p))
 else:copy(p,D/'strict-captures'/p.name);strict[p.name]=dict(preserved='strict-captures/'+p.name,sha256=sha(p))
assert len(strict)==264;write(D/'package/strict-images.json',strict)
# Compare all earlier galleries to their already published immutable checkpoint.
previous=R/'evidence/development/surface-supplement-20261016/catalogs';rows=[]
for old in sorted(previous.glob('*.png')):
 new=D/'catalogs'/old.name;metadata=Path(str(old)+'.json');newmeta=Path(str(new)+'.json')
 rows.append(dict(path=old.name,pixelsIdentical=old.read_bytes()==new.read_bytes(),metadataIdentical=metadata.read_bytes()==newmeta.read_bytes(),previousSha256=sha(old),currentSha256=sha(new),previousMetadataSha256=sha(metadata),currentMetadataSha256=sha(newmeta)))
assert len(rows)==127 and all(r['pixelsIdentical'] and r['metadataIdentical'] for r in rows)
write(D/'regression/catalogs.json',dict(accepted=False,status='passed',previousCaptures=127,currentCaptures=131,records=rows))
# One reproducible Linux implementation snapshot, including the validation tools.
implementation={str(p.relative_to(R)):p for folder in ['src','samples','tests','scripts','assets','tokens','cmake','tools'] for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
for name in ['CMakeLists.txt','CMakePresets.json']:implementation[name]=R/name
archives={'implementation':archive('implementation',implementation)}
archives['installedPackage']=archive('installed-package',{**{'install/'+n:P/'install'/n for n in installed},'consumer-build/InstalledConsumer':P/'consumer-build/InstalledConsumer'})
# Every terminal attempt remains visible, including host precondition failures.
import importlib.util
spec=importlib.util.spec_from_file_location('pill_verifier',R/'scripts/verify-pill-modifier-candidate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
metadata_files={};attempts=[]
for name,expected in v.ATTEMPT_EXITS.items():
 p=B/name;result=read(p/'result.json');assert result.get('exitCode')==expected,(name,result)
 attempts.append(dict(name=name,exitCode=expected,status=result.get('status','terminal')))
 for f in p.iterdir():
  if f.is_file() and f.suffix in ['.json','.log','.py','.sh']:
   copy(f,D/'attempts'/name/f.name);metadata_files[name+'/'+f.name]=f
# Preserve all changed source bytes against the immutable pre-feature Git tree.
base='63525f25f306b193b89a3baaab77e7cd8976383e';tree={}
for row in subprocess.check_output(['git','ls-tree','-rz','--full-tree',base],cwd=R).split(b'\0'):
 if row:
  head,name=row.split(b'\t',1);tree[name.decode()]=head.decode().split()[2]
blob_paths={};base_files={};overlays={}
for i in range(1,16):
 name=f'pill-build-v{i}';source=B/name/'source';manifest=read(B/name/'inputs.json')['sourceFiles'];delta={}
 for path,checksum in manifest.items():
  p=source/path;data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==checksum,(name,path)
  gitsha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if tree.get(path)==gitsha:base_files[path]=dict(gitObject=gitsha,sha256=checksum)
  else:delta[path]=checksum;blob_paths.setdefault(checksum,p)
 overlays[name]=delta
write(D/'replay/base-files.json',dict(baseRevision=base,files=base_files))
write(D/'replay/source-overlays.json',dict(baseRevision=base,sourceManifest='attempts/<name>/inputs.json',attempts=overlays,blobMembers={n:'blobs/'+n for n in blob_paths},scope='Full frozen source manifests plus a verified immutable Git base and every changed source byte; source replay availability on another machine remains pending.'))
# Consumer snapshots and diagnostic outputs are content addressed. Identical
# bytes refer to a preserved canonical file instead of duplicating screenshots.
canonical={sha(p):'candidate/'+str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()}
implementation_hashes={sha(p):'implementation/'+n for n,p in implementation.items()}
locations=dict(implementation_hashes,**canonical);diagnostics={};consumer_snapshots={}
for p in (R/'evidence/reference-investigations/pill-modifier-20261016').rglob('*'):
 if p.is_file():locations.setdefault(sha(p),'reference/'+str(p.relative_to(R)))
def preserve(p):
 checksum=sha(p)
 if checksum not in locations:
  locations[checksum]='blobs/'+checksum;blob_paths.setdefault(checksum,p)
 return dict(sha256=checksum,location=locations[checksum])
for name in v.ATTEMPT_EXITS:
 p=B/name
 if (p/'consumer').exists():
  consumer_snapshots[name]={str(f.relative_to(p/'consumer')):preserve(f) for f in (p/'consumer').rglob('*') if f.is_file() and '__pycache__' not in f.parts}
 for folder in ['results','captures','display-evidence','references','driver','comparison','candidate-inputs']:
  if (p/folder).exists():
   for f in (p/folder).rglob('*'):
    if f.is_file():diagnostics[name+'/'+str(f.relative_to(p))]=preserve(f)
# Initial operator data lives directly in the attempt as well as in references.
for name in ['pill-operator-v1','pill-operator-v2','pill-operator-v3','pill-operator-v4']:
 p=B/name
 for f in p.iterdir():
  if f.is_file():diagnostics[name+'/'+f.name]=preserve(f)
write(D/'replay/diagnostic-files.json',diagnostics)
write(D/'replay/consumer-snapshots.json',consumer_snapshots)
metadata_files.update({'blobs/'+n:p for n,p in blob_paths.items()})
# Chunk archives below the unchanged Linux boundary guard's expansion limit.
chunk={};size=0;index=1
for name,p in sorted(metadata_files.items()):
 if chunk and size+p.stat().st_size>48*1024*1024:
  key=f'attempts-{index:02d}';archives[key]=archive(key,chunk);chunk={};size=0;index+=1
 chunk[name]=p;size+=p.stat().st_size
if chunk:
 key=f'attempts-{index:02d}';archives[key]=archive(key,chunk)
# Versioned external runners are Linux-only; native Apple capture tooling is excluded.
helper_names=['build-avelino-pill-compact-20261016.py','run-avelino-pill-package-20261016.py','capture-avelino-pill-20261016.py','compare-avelino-pill-20261017.py','collect-avelino-pill-environment-20261017.py','run-avelino-pill-final-package-20261016.py','run-avelino-pill-final-package-v2-20261017.py','run-avelino-pill-full-20261016.py','run-avelino-pill-full-v2-20261016.py','run-avelino-pill-full-v3-20261017.py','run-avelino-pill-focused-20261017.py','run-avelino-pill-runtime-20261017.py','run-avelino-pill-operator-20261017.py','run-avelino-pill-operator-v2-20261017.py','run-avelino-pill-operator-v3-20261017.py']
helper_names += [f'run-avelino-pill-runtime-probe{suffix}-20261017.py' for suffix in ['',*['-v'+str(i) for i in range(2,8)]]]
helper_names += ['run-avelino-pill-final-package-v3-20261017.py','run-avelino-pill-full-v4-20261017.py','run-avelino-pill-dpr2-focused-20261017.py','run-avelino-pill-dpr2-focused-v2-20261017.py','run-avelino-pill-operator-v4-20261017.py','run-avelino-pill-runtime-v2-20261017.py','run-avelino-pill-runtime-v3-20261017.py','run-avelino-pill-runtime-probe-v8-20261017.py','compare-avelino-pill-v2-20261017.py','compare-avelino-pill-v3-20261017.py']
helper_names += ['run-avelino-pill-final-package-v4-20261017.py','run-avelino-pill-focused-v2-20261017.py','run-avelino-pill-runtime-v4-20261017.py','run-avelino-pill-runtime-probe-v9-20261017.py','run-avelino-pill-operator-v5-20261017.py','compare-avelino-pill-v4-20261017.py']
helper_names += ['assemble-avelino-pill-20261017.py','validate-avelino-pill-20261017.py','seal-avelino-pill-host-20261017.py']
for name in helper_names:copy(Path('/Users/gaulatti/.codex/tmp')/name,D/'runners'/name)
comparison=read(D/'comparison/comparison.json');qt=(D/'qt/LastTest.log').read_text();counts=re.findall(r'Totals: (\d+) passed, 0 failed, 0 skipped, 0 blacklisted',qt);assert len(counts)>=2
report=dict(reference=v.REFERENCE,accepted=False,status='verification-pending',tolerance='none',approvedExceptions=[],expectedImagesChanged=False,remainingAcceptance=v.GATES,
 strictComparisonStatus=comparison['status'],strictComparison=comparison['summary'],archives=archives,attempts=attempts,
 validation=dict(fullQtTargets=29,focusedQtTargets=3,commonInstalledFiles=126,componentChecksDpr1=int(counts[0]),componentChecksDpr2=int(counts[1]),independentModes=32,catalogCaptures=131,legacyPngs=127,legacyMetadata=127,installedFiles=127,virtualProfiles=32,operatorControls=18,operatorClicks=22,operatorStates=23,publicScalePairs=444,strictDefaultExitCode=1,strictImageExitCode=1,physicalDisplay=False,hardwareAcceleration=False),
 toolchains=dict(producer='sha256:48d88f958d93310bf887e4318b27713b7ecbb8b9f6a7d276087e599c9b6383d8',package='sha256:7aeb42dabe57ff3e38392d95b92f7f54c43faef5723e90da088c9023bfcf2802'),
 notes=['The first two full suites preserve font warning failures; the first also preserves a palette loop. The third preserves the failed hidden-subtree inline-image test at DPR2; the corrected test observes actual window pixels.','The source scope and stock footer in single-profile diagnostic runners are inherited text; their exact loop overrides, filenames and expectedSessions=1 are authoritative.','The first operator failed in its host observer before any clicks and was explicitly stopped; its original record has no container exit code.','The full 29-target suite uses producer 14; its library installation and component test binary are byte-identical to producer 15. Producer 15 adds a fixture-only alpha-capable rectangle and passes all three affected catalog/configuration targets.','The explicit texture-dimensions experiment was rejected. The final candidate uses asynchronous GPU capsule paths, GUI-thread image resources, independent natural text measurement and source-measured sharp-rectangle paint snapping with an alpha-capable fixture texture.'])
report['files']={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file() and p.name not in ['candidate.json','README.md']};write(D/'candidate.json',report)
(D/'README.md').write_text('# Pill Linux candidate\n\nThe sealed implementation, installed package, full source input overlays, all attempts, complete native comparison, 32 virtual profiles and 23 XTest operator states are preserved here. This is candidate evidence; native fonts, symbols, full raster/format combinations, physical input and readers remain pending. No reference, tolerance or exception changes.\n')
print(json.dumps(dict(files=len(report['files']),attempts=len(attempts),archives=len(archives),comparison=report['strictComparison'],validation=report['validation']),indent=2))
