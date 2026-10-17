import hashlib,json,pathlib,subprocess,time
R=pathlib.Path('/Users/gaulatti/source/gaulatti/avelino');D=R/'artifacts/resumed-avelino-20261016/pill-host-v1';D.mkdir()
PY='/private/tmp/avelino-resume-visuals-20261015/bin/python'
commands=[]
for line in (R/'.github/workflows/references.yml').read_text().splitlines():
 if line.startswith('      - run: python3 scripts/'):
  args=line.split('run: python3 ',1)[1].split()
  if args[0]!='scripts/check-linux-boundary.py':commands.append([PY,*args])
commands += [[PY,'-m','unittest','discover','-s','tests/contracts','-v'],['bash','-n','scripts/check-installed.sh','scripts/check-installed-catalog.sh','scripts/check-linux.sh','scripts/check-display-sessions.sh'],['ruby','-e',"require 'yaml'; ARGV.each { |p| YAML.load_file(p) }; puts 'workflow YAML parsed'",'.github/workflows/linux.yml','.github/workflows/references.yml']]
paths=set(subprocess.check_output(['git','diff','--name-only'],cwd=R,text=True).splitlines())
paths.update(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=R,text=True).splitlines())
paths={n for n in paths if not n.startswith('evidence/development/pill-modifier-20261017/') and (R/n).is_file()}
(D/'inputs.json').write_text(json.dumps({n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in sorted(paths)},indent=2)+'\n')
results=[]
for i,command in enumerate(commands):
 start=time.monotonic()
 with (D/f'{i}.log').open('w') as log: result=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 row={'command':command,'exitCode':result.returncode,'seconds':time.monotonic()-start,'log':f'{i}.log'};results.append(row)
 (D/'results.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps({'step':i,'exitCode':result.returncode,'seconds':round(row['seconds'],2),'command':command[1:]}),flush=True)
print(json.dumps({'commands':len(results),'failed':sum(r['exitCode']!=0 for r in results)}))
raise SystemExit(any(r['exitCode'] for r in results))
