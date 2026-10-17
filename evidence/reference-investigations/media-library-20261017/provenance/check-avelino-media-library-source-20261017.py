from pathlib import Path
import hashlib,importlib.util,json,re,shutil,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');F=Path('/Users/gaulatti/.codex/tmp/avelino-media-library-source-replay-20261017-v1');D=R/'evidence/reference-investigations/media-library-20261017';B=R/'artifacts/resumed-avelino-20261016';P=B/'media-library-source-host-v1'
while not (F/'execution-result.json').exists():time.sleep(.5)
assert json.loads((F/'execution-result.json').read_text())['exitCode']==0
assert not P.exists();P.mkdir()
with (P/'seal.log').open('w') as log:r=subprocess.run(['python3','/Users/gaulatti/.codex/tmp/seal-avelino-media-library-source-20261017.py'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
print('Seal',r.returncode,flush=True)
if r.returncode:print((P/'seal.log').read_text()[-6000:]);raise SystemExit(r.returncode)
python='/private/tmp/avelino-resume-visuals-20261015/bin/python'
commands=[[python,'-m','unittest','discover','-s','tests/contracts','-p','test_media_library_source.py','-v'],[python,'scripts/verify-references.py'],[python,'scripts/discover-reference.py','--check'],[python,'scripts/verify-proposals.py'],['ruby','-ryaml','-e','ARGV.each { |p| YAML.load_file(p) }','.github/workflows/references.yml'],[python,'-m','py_compile','scripts/verify-media-library-source.py','tests/contracts/test_media_library_source.py']]
rows=[]
for i,command in enumerate(commands):
 start=time.monotonic()
 with (P/(str(i)+'.log')).open('w') as log:r=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 rows.append(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start,log=str(i)+'.log'));(P/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(i,r.returncode,flush=True)
 if r.returncode:print((P/(str(i)+'.log')).read_text()[-6000:]);raise SystemExit(r.returncode)
assert int(re.search(r'Ran (\d+) tests',(P/'0.log').read_text()).group(1))==16
for p in P.iterdir():shutil.copy2(p,D/'provenance/host'/p.name) if (D/'provenance/host').exists() else None
(D/'provenance/host').mkdir(exist_ok=True)
for p in P.iterdir():shutil.copy2(p,D/'provenance/host'/p.name)
shutil.copy2(Path(__file__),D/'provenance'/Path(__file__).name)
report=json.loads((D/'investigation.json').read_text());report['hostVerification']=dict(commands=6,contractTests=16,exitCode=0,scope='Source integrity and repository reference checks only; no Linux implementation or runtime acceptance.')
report['files']={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in D.rglob('*') if p.is_file() and p.name not in ['README.md','investigation.json']};(D/'investigation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
spec=importlib.util.spec_from_file_location('media_final',R/'scripts/verify-media-library-source.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_report(report)
for name,checksum in report['files'].items():assert m.digest(D/name)==checksum,name
authored=['.github/workflows/references.yml','README.md','docs/parity-inventory.json','docs/media-library.md','scripts/verify-media-library-source.py','tests/contracts/test_media_library_source.py']
subprocess.run(['git','add','--',*authored],cwd=R,check=True)
frozen=[str(p.relative_to(R)) for p in D.rglob('*') if p.is_file()]
subprocess.run(['git','add','-f','--pathspec-from-file=-','--pathspec-file-nul'],cwd=R,input=b'\0'.join(n.encode() for n in frozen)+b'\0',check=True)
staged=[n.decode() for n in subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=R).split(b'\0') if n];index={}
for record in subprocess.check_output(['git','ls-files','--stage','-z'],cwd=R).split(b'\0'):
 if record:info,name=record.split(b'\t',1);index[name.decode()]=info.decode().split()
for name in staged:
 assert name in authored or name.startswith('evidence/reference-investigations/media-library-20261017/'),name
 value=(R/name).read_bytes();assert index[name][1:]==[hashlib.sha1(b'blob '+str(len(value)).encode()+b'\0'+value).hexdigest(),'0'],name
raw=[n for n in staged if n.startswith('evidence/reference-investigations/media-library-20261017/') and n.endswith('.log')]
subprocess.run(['git','diff','--cached','--check','--','.']+[':(exclude)'+n for n in raw],cwd=R,check=True)
with (P/'boundary.log').open('w') as log:subprocess.run(['python3','scripts/check-linux-boundary.py'],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
assert not subprocess.check_output(['git','diff','--name-only'],cwd=R).strip()
result=dict(exitCode=0,hostCommands=6,contractTests=16,stagedFiles=len(staged),frozenFiles=len(frozen),indexPayloadsExact=True,linuxBoundary='passed',authoredWhitespace='passed',rawLogWhitespaceExclusions=len(raw));(P/'precommit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
