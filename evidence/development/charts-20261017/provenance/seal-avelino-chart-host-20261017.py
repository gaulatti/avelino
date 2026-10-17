from pathlib import Path
import hashlib,json,re,shutil
R=Path('/Users/gaulatti/source/gaulatti/avelino');D=R/'evidence/development/charts-20261017';B=R/'artifacts/resumed-avelino-20261016';H=B/'charts-host-v1';F=B/'charts-host-focused-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((H/'results.json').read_text());focused=json.loads((F/'results.json').read_text());assert len(rows)==56 and all(r['exitCode']==0 for r in rows);assert len(focused)==2 and all(r['exitCode']==0 and r['resourceWarningsAbsent'] for r in focused)
assert re.search(r'Ran 568 tests in .*\n\nOK',(H/'53.log').read_text());assert re.search(r'Ran 16 tests in .*\n\nOK',(F/'0.log').read_text())
inputs=json.loads((H/'inputs.json').read_text());verifier='scripts/verify-chart-candidate.py'
assert all(sha(R/n)==v for n,v in inputs.items() if n!=verifier)
assert inputs[verifier]==sha(D/'provenance/verify-chart-candidate-before-pipe-close.py')
assert json.loads((F/'inputs.json').read_text())[verifier]==sha(R/verifier)==sha(D/'provenance/verify-chart-candidate-pipe-closed.py')
assert not (D/'host').exists();shutil.copytree(H,D/'host');shutil.copy2(H/'results.json',D/'host/original-results.json');shutil.copytree(F,D/'host/focused');shutil.copy2(D/'candidate.json',D/'host/focused/candidate-input.json')
assert json.loads((F/'inputs.json').read_text())['evidence/development/charts-20261017/candidate.json']==sha(D/'host/focused/candidate-input.json')
for row in focused:rows.append(dict(row,log='focused/'+row['log']))
(D/'host/results.json').write_text(json.dumps(rows,indent=2)+'\n')
for name in ['fix-avelino-chart-verifier-pipe-20261017.py','run-avelino-chart-verifier-focused-20261017.py','seal-avelino-chart-host-20261017.py']:shutil.copy2(Path('/Users/gaulatti/.codex/tmp')/name,D/'provenance'/name)
p=D/'candidate.json';v=json.loads(p.read_text());v['validation'].update(hostCommands=len(rows),hostContractTests=568,focusedHostContractTests=16,verifierResourceWarnings='initial full-suite pipe warning preserved; corrected helper and focused checks clean',fullSuiteVerifier='provenance/verify-chart-candidate-before-pipe-close.py',currentVerifier='provenance/verify-chart-candidate-pipe-closed.py')
v['files']={str(f.relative_to(D)):sha(f) for f in D.rglob('*') if f.is_file() and f.name not in ['candidate.json','README.md']};p.write_text(json.dumps(v,indent=2)+'\n')
print('Sealed 56 full host commands / 568 contracts, plus 16 focused contracts and a clean full replay after the verifier pipe fix')
