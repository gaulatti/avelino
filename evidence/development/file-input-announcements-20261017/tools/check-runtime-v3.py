from pathlib import Path
import json,subprocess,time
r=Path(__file__).resolve().parent
producer=r/'file-input-qt-v21'
while not(producer/'result.json').exists():time.sleep(.5)
assert json.loads((producer/'result.json').read_text())['exitCode']==0
assert json.loads((r/'file-input-announcement-package-v3/result.json').read_text())['exitCode']==0
base=['docker','--context','colima-avelino-verify']
for n in [5,4]:
 p=r/f'file-input-error-reader-v{n}'
 name=f'avelino-file-input-errors-final-{n}'
 command=base+['run','--detach','--name',name,'--ulimit','core=0','-v',str(p)+':/probe','-w','/probe','avelino-toolchain:recovered-a11y-20261017-qt6.8.3','dbus-run-session','--','python3','/probe/session.py']
 cid=subprocess.check_output(command,text=True).strip()
 (p/'session-command.json').write_text(json.dumps(dict(command=command,containerId=cid),indent=2)+'\n')
 print('Reader session started',n,cid,flush=True)
 while not(p/'ready').exists():
  state=json.loads(subprocess.check_output(base+['inspect',cid],text=True))[0]['State']
  if not state['Running']:raise RuntimeError(state)
  time.sleep(.2)
 try:
  command=base+['exec',cid,'python3','/probe/exercise.py']
  with(p/'exercise.log').open('wb')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  (p/'exercise-result.json').write_text(json.dumps(dict(command=command,exitCode=result.returncode),indent=2)+'\n')
  print('Reader exercise',n,result.returncode,flush=True)
  command=base+['exec',cid,'python3','/probe/collect.py']
  with(p/'collect.log').open('wb')as log:collected=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  (p/'collect-result.json').write_text(json.dumps(dict(command=command,exitCode=collected.returncode),indent=2)+'\n')
 finally:
  (p/'finished').touch()
  command=base+['wait',cid]
  result_wait=subprocess.check_output(command,text=True).strip()
  (p/'session-result.json').write_text(json.dumps(dict(command=command,exitCode=int(result_wait)),indent=2)+'\n')
  (p/'session.log').write_bytes(subprocess.check_output(base+['logs',cid],stderr=subprocess.STDOUT))
 assert result.returncode==0 and collected.returncode==0 and result_wait=='0'
print('Final producer, eight package contexts and both actual reader sessions passed',flush=True)
