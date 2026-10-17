from pathlib import Path
import hashlib,json,re,shutil
R=Path('/Users/gaulatti/source/gaulatti/avelino');D=R/'evidence/development/chart-geometry-20261017';P=R/'artifacts/resumed-avelino-20261016/charts-geometry-host-v1'
results=json.loads((P/'results.json').read_text());assert len(results)==60 and all(r['exitCode']==0 for r in results)
tests=[r for r in results if '-m' in r['command'] and 'unittest' in r['command']];assert len(tests)==1
log=(P/tests[0]['log']).read_text();count=int(re.search(r'Ran (\d+) tests',log).group(1));assert count==596 and '\nOK\n' in log
assert not (D/'host').exists();shutil.copytree(P,D/'host')
for n in ['check-avelino-chart-geometry-host-20261017.py','finalize-avelino-chart-geometry-host-20261017.py']:shutil.copy2(Path('/Users/gaulatti/.codex/tmp')/n,D/'provenance'/n)
receipt=R/'artifacts/resumed-avelino-20261016/charts-geometry-index-audit-v1.json';value=json.loads(receipt.read_text());assert value['exitCode']==0 and value['files']==10582
value['scope']='All 10582 initial sealed payloads matched their Git index blobs before adding the host-check logs. Final staged-tree audit is separate.'
(D/'host/index-audit-before-host-seal.json').write_text(json.dumps(value,indent=2)+'\n')
p=D/'candidate.json';report=json.loads(p.read_text());report['validation'].update(hostCommands=len(results),hostContractTests=count)
report['files']={str(f.relative_to(D)):hashlib.sha256(f.read_bytes()).hexdigest() for f in D.rglob('*') if f.is_file() and f.name not in ['README.md','candidate.json']};p.write_text(json.dumps(report,indent=2)+'\n')
print('Sealed',len(results),'passing host commands and',count,'contract tests')
