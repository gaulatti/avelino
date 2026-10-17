from pathlib import Path
import hashlib,json,re,shlex,subprocess,time
R=Path('/Users/gaulatti/source/gaulatti/avelino');B=R/'artifacts/resumed-avelino-20261016';D=R/'evidence/development/media-library-caption-20261017';H=B/'media-library-caption-host-v1';assert not H.exists();H.mkdir()
while not (D/'candidate.json').exists():time.sleep(.25)
python='/private/tmp/avelino-resume-visuals-20261015/bin/python';commands=[]
for line in (R/'.github/workflows/references.yml').read_text().splitlines():
 if line.startswith('      - run: python3 '):
  c=shlex.split(line.split('run: ',1)[1])
  if c[1:4]==['-m','pip','install'] or c[1]=='scripts/check-linux-boundary.py':continue
  commands.append([python,*c[1:]])
commands += [['bash','-n',*map(str,[R/'scripts'/n for n in ['check-installed.sh','check-installed-catalog.sh','check-linux.sh','check-display-sessions.sh']])],['ruby','-e',"require 'yaml'; ARGV.each { |path| YAML.load_file(path) }",str(R/'.github/workflows/references.yml'),str(R/'.github/workflows/linux.yml')]]
paths=[p for directory in ['scripts','tests/contracts','.github/workflows'] for p in (R/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[R/'docs/parity-inventory.json',R/'README.md',R/'docs/media-library.md',R/'docs/font-modifier.md',R/'docs/pill-modifier.md',D/'candidate.json']
(H/'inputs.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},indent=2)+'\n');rows=[]
for i,c in enumerate(commands):
 t=time.monotonic()
 with (H/f'{i}.log').open('w') as log:r=subprocess.run(c,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 row=dict(command=c,exitCode=r.returncode,seconds=time.monotonic()-t,log=f'{i}.log');rows.append(row)
 (H/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(i,r.returncode,' '.join(c[1:]),flush=True)
 if r.returncode:print((H/f'{i}.log').read_text()[-4000:]);raise SystemExit(r.returncode)
contract=next(r for r in rows if 'unittest' in r['command']);matches=re.search(r'Ran (\d+) tests in .*\n\nOK',(H/contract['log']).read_text());assert matches
(H/'result.json').write_text(json.dumps(dict(exitCode=0,commands=len(rows),contractTests=int(matches[1])),indent=2)+'\n')
print('Host verification passed',len(rows),matches[1])
