from pathlib import Path
import hashlib,json,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';H=B/'charts-host-v1';assert not H.exists();H.mkdir()
commands=[r['command'] for r in json.loads((B/'charts-source-host-v1/results.json').read_text())]
index=next(i for i,c in enumerate(commands) if 'unittest' in c)
commands[index:index]=[['/private/tmp/avelino-resume-visuals-20261015/bin/python','scripts/generate-chart-witnesses.py','--check'],['/private/tmp/avelino-resume-visuals-20261015/bin/python','scripts/verify-chart-candidate.py']]
assert len(commands)==56
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[p for folder in ['src','samples','tests','scripts','docs','cmake','.github/workflows','assets','tokens','tools'] for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
files += [R/n for n in ['CMakeLists.txt','CMakePresets.json','README.md','AGENTS.md']]
inputs={str(p.relative_to(R)):sha(p) for p in files};(H/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n');rows=[]
for i,c in enumerate(commands):
 start=time.monotonic();name=f'{i:02d}.log'
 with (H/name).open('w') as log:r=subprocess.run(c,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 rows.append(dict(command=c,exitCode=r.returncode,seconds=time.monotonic()-start,log=name));(H/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(i,r.returncode,c,flush=True)
assert all(sha(R/n)==v for n,v in inputs.items()),'Host inputs changed during verification'
print('Host chart checks:',sum(r['exitCode']==0 for r in rows),'/',len(rows))
raise SystemExit(1 if any(r['exitCode'] for r in rows) else 0)
