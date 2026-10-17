from pathlib import Path
import json,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');P=R/'artifacts/resumed-avelino-20261016/charts-geometry-host-v1';assert not P.exists();P.mkdir()
python='/private/tmp/avelino-resume-visuals-20261015/bin/python'
commands=[]
for line in (R/'.github/workflows/references.yml').read_text().splitlines():
 prefix='      - run: python3 '
 if line.startswith(prefix):commands.append([python,*line[len(prefix):].split()])
commands += [['bash','-n','scripts/check-linux.sh'],['ruby','-ryaml','-e','ARGV.each { |p| YAML.load_file(p) }','.github/workflows/linux.yml','.github/workflows/references.yml']]
results=[]
for i,command in enumerate(commands):
 start=time.monotonic()
 with (P/(str(i)+'.log')).open('w') as log:r=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 results.append(dict(command=command,exitCode=r.returncode,seconds=time.monotonic()-start,log=str(i)+'.log'));(P/'results.json').write_text(json.dumps(results,indent=2)+'\n')
 print(i,r.returncode,' '.join(command[1:]),flush=True)
 if r.returncode:print((P/(str(i)+'.log')).read_text()[-6000:]);raise SystemExit(r.returncode)
print('Passed',len(results),'host commands')
