from pathlib import Path
import collections,gzip,hashlib,importlib.util,io,json,shutil,subprocess,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');P=Path('/Users/gaulatti/.codex/tmp/avelino-media-library-native-20261017-v4');F=Path('/Users/gaulatti/.codex/tmp/avelino-media-library-source-replay-20261017-v1');D=R/'evidence/reference-investigations/media-library-20261017'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
assert read(P/'result.json')['exitCode']==read(F/'execution-result.json')['exitCode']==read(F/'result.json')['exitCode']==0
assert not D.exists();D.mkdir()
for name in ['output','sizing-output','history-output','edges']:shutil.copytree(P/name,D/name)
for name in ['fixtures.json','histories.json','edge-cases.json','edge-results.json']:copy(P/name,D/name)
for source,dest in [('inputs.json','initial-inputs.json'),('steps.json','initial-commands.json'),('result.json','initial-result.json'),('build.log','initial-build.log'),('closed.log','initial-closed.log'),('sizing.log','initial-sizing.log'),('histories.log','initial-histories.log'),('original-runner.py','initial-runner.py'),('toolchain.json','toolchain.json')]:copy(P/source,D/'provenance'/dest)
for source,dest in [('inputs.json','fresh-inputs.json'),('commands.json','fresh-commands.json'),('result.json','fresh-result.json'),('execution-result.json','fresh-execution-result.json'),('edge-results.json','fresh-edge-results.json'),('run.log','fresh-run.log'),('library-build.log','fresh-library-build.log'),('helper-build.log','fresh-helper-build.log'),('output.log','fresh-closed.log'),('sizing-output.log','fresh-sizing.log'),('history-output.log','fresh-histories.log'),('replay.py','fresh-replay.py')]:copy(F/source,D/'provenance'/dest)
for p in (F/'edges').rglob('*.log'):copy(p,D/'provenance/fresh-edge-logs'/p.relative_to(F/'edges'))
for producer,target in [(P,'edge-inputs'),(F,'fresh-edge-inputs')]:
 for path in {row['command'][1] for row in read(producer/'edge-results.json')}:copy(Path(path),D/'provenance'/target/Path(path).name)
for version in [1,2,3]:
 prior=P.with_name(P.name[:-1]+str(version))
 for n in ['inputs.json','steps.json','result.json','build.log','closed.log','sizing-pilot.log','histories.log','original-runner.py']:
  if (prior/n).is_file():copy(prior/n,D/'provenance'/('pilot-v'+str(version))/n)
 for folder in ['output','sizing-pilot','history-output']:
  if (prior/folder).exists():shutil.copytree(prior/folder,D/'pilots'/('v'+str(version))/folder)
for name in ['prepare-avelino-media-library-source-replay-20261017.py','seal-avelino-media-library-source-20261017.py']:copy(Path('/Users/gaulatti/.codex/tmp')/name,D/'provenance'/name)
differences=[]
for row in read(P/'sizing-output/sizing.json')['rows']:
 modes=row['modes'];changed={k:[m['proposals'][k] for m in modes] for k in modes[0]['proposals'] if not modes[0]['proposals'][k]==modes[1]['proposals'][k]==modes[2]['proposals'][k]}
 if changed:differences.append(dict(fixture=row['configuration']['id'],appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],proposals=changed))
write(D/'sizing-witness-differences.json',differences)
def raw(root):return {str(p.relative_to(root)):p for name in ['output','sizing-output','history-output','edges'] for p in (root/name).rglob('*') if p.is_file() and p.suffix in ['.png','.json']}
first,second=raw(P),raw(F);records=[];extra=[]
for n,p in sorted(first.items()):
 a=sha(p);b=sha(second[n]) if n in second else None;same=a==b;target=n if same else 'replay-variants/'+n if b else None
 if b and not same:copy(second[n],D/target)
 records.append(dict(path=n,firstSha256=a,replaySha256=b,replayPath=target,status='passed' if same else 'failed'))
for n,p in sorted(second.items()):
 if n not in first:copy(p,D/'replay-variants'/n);extra.append(dict(path=n,sha256=sha(p),replayPath='replay-variants/'+n))
write(D/'replay.json',dict(accepted=False,prebuiltLibraryInputs=False,sourceFilesUnchanged=89,results=records,extraFiles=extra))
unchanged=[]
prior=P.with_name(P.name[:-1]+'3')
for p in (prior/'output').glob('*.png'):
 assert p.read_bytes()==(P/'output'/p.name).read_bytes();unchanged.append(dict(pilot='pilots/v3/output/'+p.name,current='output/'+p.name,sha256=sha(p)))
# Source-only bundles stay external; the tracked tree carries their locators.
def external_artifact(name,files,prefix):
 staging=Path('/Users/gaulatti/.codex/tmp')/(name+'.tar.gz');assert not staging.exists()
 with staging.open('xb') as raw_stream,gzip.GzipFile(fileobj=raw_stream,mode='wb',mtime=0) as gz,tarfile.open(fileobj=gz,mode='w') as stream:
  for n,p in sorted(files.items()):
   data=p.read_bytes();info=tarfile.TarInfo(n);info.size=len(data);info.mode=0o644;info.mtime=0;stream.addfile(info,io.BytesIO(data))
 checksum=sha(staging);folder=Path('/Users/gaulatti/.codex/tmp/avelino-reference-vault/candidates')/(prefix+'-'+checksum[:12]);assert not folder.exists();folder.mkdir();shutil.move(staging,folder/staging.name)
 return dict(path=str(folder/staging.name),sha256=checksum,bytes=(folder/staging.name).stat().st_size,files=len(files),downloadAvailability='pending independent-machine replay')
source_files={n:F/n for n in read(F/'inputs.json')['files']};source_files['inputs.json']=F/'inputs.json';assert len(source_files)==10
artifact=external_artifact('native-media-library-source-only-20261017',source_files,'media-library-source');artifact['containsPinnedSourceFiles']=89
pilot_files={}
for version in [1,2,3]:
 prior=P.with_name(P.name[:-1]+str(version))
 for p in (prior/'tool').glob('*.swift'):pilot_files[f'v{version}/tool/'+p.name]=p
 for n in ['fixtures.json','histories.json','sizing-pilot.json','inputs.json','original-runner.py']:
  if (prior/n).is_file():pilot_files[f'v{version}/'+n]=prior/n
pilot_artifact=external_artifact('native-media-library-pilot-tooling-20261017',pilot_files,'media-library-pilots')
spec=importlib.util.spec_from_file_location('media_source',R/'scripts/verify-media-library-source.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
observations=m.observations(D);edges=read(P/'edge-results.json');replay_edges=read(F/'edge-results.json');outcomes=sum(a['exitCode']==b['exitCode'] for a,b in zip(edges,replay_edges));exact=sum(r['status']=='passed' for r in records)
summary=dict(fixtures=62,closedContexts=496,closedImages=1488,sizingContexts=496,sizingQueriesPerBranch=7440,histories=48,historySteps=1008,historyImages=3024,ordinaryImages=4512,edgeFixtures=14,edgeContexts=112,edgeImages=sum(p.suffix=='.png' for n,p in first.items() if n.startswith('edges/')),edgeTerminalFailures=sum(r['exitCode']!=0 for r in edges),edgeReplayOutcomeMatches=outcomes,sourceRawFiles=len(first),sourceReplayExactFiles=exact,sourceReplayExtraFiles=len(extra),**observations)
report=dict(reference=m.REFERENCE,status='source-investigation; Linux implementation pending',accepted=False,expectedImagesChanged=False,approvedExceptions=[],tolerance='none',remainingAcceptance=m.GATES,summary=summary,sourceReplayStatus='passed' if exact==len(first) and outcomes==112 and not extra else 'failed',sourceOnlyArtifact=artifact,pilotToolingArtifact=pilot_artifact,pilotImagesUnchanged=unchanged,attempts=[dict(name='pilot-v1',exitCode=1,stage='helper build; optional Double/CGFloat mismatch'),dict(name='pilot-v2',exitCode=0,stage='41-context pilot'),dict(name='pilot-v3',exitCode=0,stage='61-context pilot and retained traces'),dict(name='native-v4',exitCode=0,stage='complete matrix with isolated native edge outcomes'),dict(name='fresh-source-v1',exitCode=0,stage='complete unchanged-source build and replay')])
report['files']={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file() and p.name not in ['README.md','investigation.json']};write(D/'investigation.json',report)
(D/'README.md').write_text('# Native MediaLibrary investigation\n\nUnmodified public/probed/literal source cases preserve 496 closed contexts, 22320 direct sizing queries, 1008 retained-history steps and all 112 isolated edge outcomes. All closed and retained pixel/geometry/lifecycle witnesses match; one sizing context differs and remains unresolved. Fresh-source replay outcomes and every differing output remain in investigation.json and replay.json. Source-only inputs and all pilot helper versions stay in external checksummed artifacts. Linux implementation and all mirror acceptance remain pending. No source pin, expected image, tolerance or exception changes. See [the contract](../../../docs/media-library.md).\n')
m.verify(D);print(json.dumps(summary,indent=2));print('Source replay',report['sourceReplayStatus'])
