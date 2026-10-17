from pathlib import Path
import hashlib,json,re,shutil
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/media-library-reflow-20261017';H=B/'media-library-reflow-host-v1';L=B/'media-library-reflow-clean-replay-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
result=read(H/'result.json');rows=read(H/'results.json');assert result['exitCode']==0 and result['commands']==len(rows)and all(r['exitCode']==0 for r in rows)
inputs=read(H/'inputs.json');assert all(sha(R/name)==value for name,value in inputs.items())
assert read(L/'result.json')['exitCode']==0
assert all(sha(R/name)==value for name,value in read(L/'inputs.json').items())
contract=next(r for r in rows if'unittest'in r['command']);log=(H/contract['log']).read_text();assert re.search(r'Ran '+str(result['contractTests'])+r' tests in .*\n\nOK',log);assert 'ResourceWarning:'not in log
assert not(D/'host').exists();shutil.copytree(H,D/'host');shutil.copy2(D/'candidate.json',D/'host/candidate-input.json');shutil.copytree(L,D/'host/clean-linux')
for name in['check-avelino-media-library-reflow-host-20261017.py','seal-avelino-media-library-reflow-host-20261017.py','check-avelino-media-library-reflow-linux-20261017.py']:shutil.copy2(Path('/Users/gaulatti/.codex/tmp')/name,D/'provenance'/name)
p=D/'candidate.json';v=read(p);v['validation'].update(hostCommands=len(rows),hostContractTests=result['contractTests'],hostCandidateInput='host/candidate-input.json',hostResourceWarnings='none in current contract run',cleanLinuxEvidenceReplay=True)
profiles=[]
for path in sorted((D/'runtime').glob('media-library-*.json')):
 value=read(path);profiles.append(dict(profile=path.stem,platform=value['platform'],structuralChecks=value['structuralChecks'],restoredPixelMatches=value['retainedRestorePixelMatches'],restoreObservations=6,restoredRasterStatus=value['retainedRestoreRasterStatus'],failedRestores=[h['configuration']['id']for h in value['histories']if not h['steps'][13]['matchesInitialPixels']]))
assert len(profiles)==8 and all(r['structuralChecks']=='passed'and r['restoredPixelMatches']==6 for r in profiles)
v['virtualProfiles']=profiles
v['files']={str(f.relative_to(D)):sha(f)for f in D.rglob('*')if f.is_file()and f.name not in['candidate.json','README.md']};p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
print('Sealed host',result,'and clean Linux replay; virtual restores 48/48')
