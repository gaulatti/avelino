from pathlib import Path
import gzip,hashlib,io,json,shutil,tarfile
R=Path('/Users/gaulatti/source/gaulatti/avelino');D=R/'evidence/development/charts-20261017';B=R/'artifacts/resumed-avelino-20261016';H=B/'charts-host-v1'
rows=json.loads((H/'results.json').read_text());assert len(rows)==56 and all(r['exitCode']==0 for r in rows)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=json.loads((H/'inputs.json').read_text());assert all(sha(R/n)==v for n,v in inputs.items())
p=R/'scripts/verify-chart-candidate.py';old=p.read_text();a='finally:process.stdin.close();process.wait()';assert old.count(a)==1
provenance=D/'provenance';shutil.copy2(p,provenance/'verify-chart-candidate-before-pipe-close.py')
p.write_text(old.replace(a,'finally:process.stdin.close();process.wait();process.stdout.close()'))
shutil.copy2(p,provenance/'verify-chart-candidate-pipe-closed.py')
# The complete earlier validation snapshot remains inspectable. Refresh only
# the verifier member in the current implementation archive; compiled producer,
# installed module, consumer and native/candidate outputs are unchanged.
report=json.loads((D/'candidate.json').read_text());record=report['archives']['implementation'];prior='implementation-before-pipe-close'
shutil.copy2(D/record['archive'],D/(prior+'.tar.gz'));shutil.copy2(D/record['manifest'],D/(prior+'-manifest.json'))
report['archives']['implementationBeforePipeClose']=dict(archive=prior+'.tar.gz',manifest=prior+'-manifest.json',files=record['files'])
files={}
with tarfile.open(D/(prior+'.tar.gz')) as stream:
 for member in stream.getmembers():files[member.name]=(stream.extractfile(member).read(),member.mode)
files['scripts/verify-chart-candidate.py']=(p.read_bytes(),p.stat().st_mode&0o777);manifest={}
with (D/record['archive']).open('wb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as gz,tarfile.open(fileobj=gz,mode='w') as stream:
 for name,(data,mode) in sorted(files.items()):
  info=tarfile.TarInfo(name);info.size=len(data);info.mode=mode;info.mtime=0;stream.addfile(info,io.BytesIO(data));manifest[name]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),mode=mode)
(D/record['manifest']).write_text(json.dumps(manifest,indent=2)+'\n')
(provenance/'verifier-pipe-closure.json').write_text(json.dumps(dict(scope='Validation helper only: close the completed git cat-file output pipe. Original full-contract warning and exact helper source/archive remain preserved; compiled product, public QML, native expectations and all candidate captures are unchanged.',previousSha256=hashlib.sha256(old.encode()).hexdigest(),currentSha256=sha(p),originalHostInputs='host/inputs.json',focusedValidation='host/focused/results.json'),indent=2)+'\n')
for name in ['charts-inverse-transform-analysis-v1.json','charts-inverse-transform-analysis-v2.json']:shutil.copy2(B/name,D/'geometry-analysis'/name)
for name in ['assemble-avelino-charts-20261017.py','update-avelino-charts-ledger-20261017.py','run-avelino-charts-host-20261017.py']:shutil.copy2(Path('/Users/gaulatti/.codex/tmp')/name,provenance/name)
report['files']={str(p.relative_to(D)):sha(p) for p in D.rglob('*') if p.is_file() and p.name not in ['candidate.json','README.md']};(D/'candidate.json').write_text(json.dumps(report,indent=2)+'\n')
print('Closed the verifier Git output pipe; preserved the original helper and its full-validation snapshot')
