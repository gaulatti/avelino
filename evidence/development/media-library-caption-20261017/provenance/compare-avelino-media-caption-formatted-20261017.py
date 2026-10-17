from pathlib import Path
import hashlib,json,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';P=B/'media-library-caption-formatted-comparison-v1';assert not P.exists();P.mkdir();rows=[]
for kind,script in [('fonts','compare-font-modifier-captures.py'),('pills','compare-pill-modifier-captures.py')]:
 source=B/('media-library-caption-'+kind+'-v1')
 while not(source/'result.json').exists():time.sleep(1)
 assert json.loads((source/'result.json').read_text())['exitCode']==0
 command=['/private/tmp/avelino-resume-visuals-20261015/bin/python',str(R/'scripts'/script),str(source/'captures'),str(P/kind)];start=time.monotonic()
 with(P/(kind+'.log')).open('w')as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 rows.append(dict(kind=kind,command=command,exitCode=p.returncode,seconds=time.monotonic()-start));(P/'steps.json').write_text(json.dumps(rows,indent=2)+'\n');assert p.returncode in[0,1],(kind,p.returncode)
 print(kind,p.returncode,(P/(kind+'.log')).read_text()[-1300:],flush=True)
(P/'result.json').write_text(json.dumps(dict(exitCode=0,accepted=False,strictExitCodes={r['kind']:r['exitCode']for r in rows}),indent=2)+'\n')
