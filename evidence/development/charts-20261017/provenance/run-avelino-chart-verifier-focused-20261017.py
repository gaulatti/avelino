from pathlib import Path
import hashlib,json,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');P=R/'artifacts/resumed-avelino-20261016/charts-host-focused-v1';assert not P.exists();P.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(P/'inputs.json').write_text(json.dumps({n:sha(R/n) for n in ['scripts/verify-chart-candidate.py','tests/contracts/test_chart_candidate.py','evidence/development/charts-20261017/candidate.json']},indent=2)+'\n')
commands=[['/private/tmp/avelino-resume-visuals-20261015/bin/python','-Werror::ResourceWarning','-m','unittest','discover','-s','tests/contracts','-p','test_chart_candidate.py','-v'],['/private/tmp/avelino-resume-visuals-20261015/bin/python','-Werror::ResourceWarning','scripts/verify-chart-candidate.py']];rows=[]
for i,c in enumerate(commands):
 start=time.monotonic();name=f'{i}.log'
 with (P/name).open('w') as log:r=subprocess.run(c,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 output=(P/name).read_text();clean='ResourceWarning' not in output and 'Exception ignored' not in output
 rows.append(dict(command=c,exitCode=r.returncode,resourceWarningsAbsent=clean,seconds=time.monotonic()-start,log=name));(P/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(i,r.returncode,'resource-clean:',clean,flush=True)
 assert r.returncode==0 and clean,(c,output[-3000:])
print('Verifier: 16 focused contracts and a full evidence replay, with resource warnings treated as errors')
