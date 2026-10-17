from pathlib import Path
import json,subprocess,sys,time
r=Path(__file__).resolve().parent;n=int(sys.argv[1]);p=r/f'file-input-navigation-reader-v{n}';base=['docker','--context','colima-avelino-verify'];name=f'avelino-file-input-navigation-reader-{n}'
inputs=json.loads((p/'inputs.json').read_text())
command=base+['run','--detach','--name',name,'--ulimit','core=0','-v',str(p)+':/probe','-w','/probe',inputs['image'],'dbus-run-session','--','python3','/probe/session.py']
cid=subprocess.check_output(command,text=True).strip();(p/'session-command.json').write_text(json.dumps(dict(command=command,containerId=cid),indent=2)+'\n')
while not(p/'ready').exists():
 state=json.loads(subprocess.check_output(base+['inspect',cid],text=True))[0]['State']
 if not state['Running']:raise RuntimeError(state)
 time.sleep(.2)
print('Reader ready',n,cid,flush=True)
while not(p/'operator-start').exists():time.sleep(.1)
try:
 command=base+['exec',cid,'python3','/probe/exercise.py']
 with(p/'exercise.log').open('wb')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 (p/'exercise-result.json').write_text(json.dumps(dict(command=command,exitCode=result.returncode),indent=2)+'\n');print('Operator',n,result.returncode,flush=True)
 command=base+['exec',cid,'python3','/probe/collect.py']
 with(p/'collect.log').open('wb')as log:collected=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 (p/'collect-result.json').write_text(json.dumps(dict(command=command,exitCode=collected.returncode),indent=2)+'\n')
finally:
 if result.returncode:
  print('Operator failed; session kept live for diagnostics',flush=True)
  while not(p/'finish-diagnostics').exists():time.sleep(.2)
 (p/'finished').touch();command=base+['wait',cid];value=subprocess.check_output(command,text=True).strip()
 (p/'session-result.json').write_text(json.dumps(dict(command=command,exitCode=int(value)),indent=2)+'\n')
 (p/'session.log').write_bytes(subprocess.check_output(base+['logs',cid],stderr=subprocess.STDOUT))
assert result.returncode==collected.returncode==int(value)==0
