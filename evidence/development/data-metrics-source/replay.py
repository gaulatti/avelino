from pathlib import Path
import hashlib,json,shutil,subprocess,tarfile
root=Path('../avelino-reference-vault/candidates/data-metrics-20261015-87d6fa9f').resolve()
def command(*args):return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT).strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads(Path('evidence/reference-investigations/sidebar-brand-20261015/tooling-provenance.json').read_text())
env={**old['environment'],'capturePreparationRevision':command('git','rev-parse','HEAD'),'os':command('sw_vers'),'xcode':command('xcodebuild','-version'),'compiler':command('xcrun','swiftc','--version'),'sdk':command('xcrun','--sdk','macosx','--show-sdk-version'),'buildMethod':'Helper rebuilt against preserved source-verified pinned module/object; no fresh full source build'}
(root/'toolchain.json').write_text(json.dumps(env,indent=2,sort_keys=True)+'\n');shutil.copy2('artifacts/data-metrics/native-capture.log',root/'capture.log')
inputs=sorted([p for p in (root/'cached-reference').rglob('*') if p.is_file()]+[root/'tool/Sources/NativeCapture/main.swift',root/'tool/build-capture.py',root/'tool/run-capture.py',root/'toolchain.json'])
files={str(p.relative_to(root)):sha(p) for p in inputs};assert len(files)==36
(root/'replay-inputs.json').write_text(json.dumps(files,indent=2,sort_keys=True)+'\n')
archive=root/'native-data-metrics-replay.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz') as t:
 for p in inputs+[root/'replay-inputs.json']:t.add(p,arcname=str(p.relative_to(root)),recursive=False)
replay=root/'clean-replay';replay.mkdir()
with tarfile.open(archive) as t:t.extractall(replay,filter='data')
for name,digest in files.items():assert sha(replay/name)==digest,name
with (replay/'build.log').open('w') as log:subprocess.run(['python3',str(replay/'tool/build-capture.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
with (replay/'run.log').open('w') as log:subprocess.run(['python3',str(replay/'tool/run-capture.py'),str(replay)],stdout=log,stderr=subprocess.STDOUT,check=True)
rows=[]
outputs=sorted([p for p in (root/'captures').rglob('*') if p.is_file()]+[p for folder in root.glob('locale-*') for p in folder.rglob('*') if p.is_file()]+[root/'capture.log'])
for a in outputs:
 name=str(a.relative_to(root));b=replay/name;logical=name.removeprefix('captures/')
 rows.append({'path':logical,'sha256':sha(a),'replaySha256':sha(b),'byteIdentical':a.read_bytes()==b.read_bytes()})
report={'inputHashesVerified':len(files),'filesCompared':len(rows),'byteIdenticalFiles':sum(r['byteIdentical'] for r in rows),'changedFiles':[r['path'] for r in rows if not r['byteIdentical']],'method':'clean external archive extraction; every input hash verified; helper rebuilt; full source PNG/geometry/formatter output and seven process-local locale probes compared byte for byte','sourceOutputMapping':'primary captures flattened from captures/; locale-*/ and capture.log retain their relative output paths','results':rows}
(root/'clean-replay.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print({k:v for k,v in report.items() if k!='results'});assert len(rows)==3160 and not report['changedFiles']
