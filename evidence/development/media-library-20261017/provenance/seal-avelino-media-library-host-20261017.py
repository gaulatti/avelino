from pathlib import Path
import hashlib,json,re,shutil
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/media-library-20261017';H=B/'media-library-host-v1';Y=B/'media-library-yaml-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=json.loads((H/'result.json').read_text());rows=json.loads((H/'results.json').read_text());assert result['exitCode']==0 and result['commands']==len(rows) and all(r['exitCode']==0 for r in rows)
inputs=json.loads((H/'inputs.json').read_text());assert all(sha(R/name)==value for name,value in inputs.items())
assert json.loads((Y/'result.json').read_text())['exitCode']==0
contract=next(r for r in rows if 'unittest' in r['command']);text=(H/contract['log']).read_text();assert re.search(r'Ran '+str(result['contractTests'])+r' tests in .*\n\nOK',text);assert 'ResourceWarning:' not in text
assert not (D/'host').exists();shutil.copytree(H,D/'host');shutil.copy2(D/'candidate.json',D/'host/candidate-input.json');shutil.copytree(Y,D/'host/yaml');shutil.copytree(B/'media-library-path-audit-v1',D/'host/source-paths')
for name in ['check-avelino-media-library-host-20261017.py','seal-avelino-media-library-host-20261017.py']:shutil.copy2(Path('/Users/gaulatti/.codex/tmp')/name,D/'provenance'/name)
p=D/'candidate.json';v=json.loads(p.read_text());v['validation'].update(hostCommands=len(rows)+1,hostContractTests=result['contractTests'],hostCandidateInput='host/candidate-input.json',hostResourceWarnings='none in current contract run')
v['validation']['contentAddressedSourcePaths']=26989
v['diagnostics']['environmentScopeLabel']='The reused collector retains a chart-specific scope label. Current installed-file and consumer hashes identify this media package; environment-seed.json remains historical only.'
profiles=[]
for path in sorted((D/'runtime').glob('media-library-*.json')):
 value=json.loads(path.read_text());profiles.append(dict(profile=path.stem,platform=value['platform'],structuralChecks=value['structuralChecks'],restoredPixelMatches=value['retainedRestorePixelMatches'],restoreObservations=6,restoredRasterStatus=value['retainedRestoreRasterStatus'],failedRestores=[h['configuration']['id']for h in value['histories']if not h['steps'][13]['matchesInitialPixels']]))
assert len(profiles)==8 and all(r['structuralChecks']=='passed' for r in profiles)
v['virtualProfiles']=profiles;v['validation'].update(virtualRestoreObservations=48,virtualRestorePixelMatches=sum(r['restoredPixelMatches']for r in profiles))
v['files']={str(f.relative_to(D)):sha(f)for f in D.rglob('*')if f.is_file() and f.name not in ['candidate.json','README.md']};p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
print('Sealed host verification',result,'plus Linux/References YAML check; virtual restores',v['validation']['virtualRestorePixelMatches'],'/48')
