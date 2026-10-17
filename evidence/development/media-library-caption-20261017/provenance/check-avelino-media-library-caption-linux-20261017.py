from pathlib import Path
import hashlib,json,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/media-library-caption-20261017';P=B/'media-library-caption-clean-replay-v1';assert not P.exists();P.mkdir()
files=sorted((R/'scripts').rglob('*.py'))+sorted((R/'tests/contracts').glob('test_media_library_*.py'))+[D/'candidate.json']
(P/'inputs.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files},indent=2)+'\n')
command=['docker','--context','colima-avelino-verify','run','--rm','--init','--ulimit','core=0','--name','avelino-media-caption-clean-replay-v1','-v',str(R)+':/work:ro','-v',str(P)+':/receipt:rw','-w','/work','-e','PYTHONDONTWRITEBYTECODE=1']
for name in ['tests/components','tests/contracts','scripts']:command+=['--mount','type=tmpfs,destination=/work/'+name+'/__pycache__']
command+=['avelino-toolchain:data-metrics-qt6.8.3','bash','-lc',"python3 -m venv /tmp/evidence-env && /tmp/evidence-env/bin/pip install -r tools/visual-requirements.txt && git config --global --add safe.directory /work && /tmp/evidence-env/bin/python -m unittest discover -s tests/contracts -p 'test_media_library_*' -v"]
start=time.monotonic()
with(P/'run.log').open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
(P/'result.json').write_text(json.dumps(dict(exitCode=result.returncode,seconds=time.monotonic()-start,command=command),indent=2)+'\n')
print('Clean Linux evidence replay',result.returncode);print((P/'run.log').read_text()[-2000:]);raise SystemExit(result.returncode)
