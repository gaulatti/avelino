from pathlib import Path
import json, subprocess, sys, time
number=sys.argv[1]
p=Path(__file__).resolve().parent/('file-input-go-to-reader-v'+number)
name='avelino-file-input-go-to-reader-'+number
prefix=['docker','--context','colima-avelino-verify']
command=prefix+['run','--detach','--name',name,'--ulimit','core=0','-v',str(p)+':/probe','-w','/probe','avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3','dbus-run-session','--','python3','/probe/session.py']
r=subprocess.run(command,text=True,capture_output=True)
(p/'session-launch.json').write_text(json.dumps(dict(command=command,code=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n')
assert r.returncode==0,r.stderr
container=r.stdout.strip()
(p/'session-command.json').write_text(json.dumps(dict(command=command,containerId=container),indent=2)+'\n')
print('started',name,container,flush=True)
try:
 deadline=time.monotonic()+30
 while not(p/'ready').exists():
  status=subprocess.check_output(prefix+['inspect','-f','{{.State.Status}}',container],text=True).strip()
  assert status=='running' and time.monotonic()<deadline,('Session not ready',status)
  time.sleep(.2)
 exercise=prefix+['exec',name,'python3','/probe/exercise.py']
 (p/'exercise-command.json').write_text(json.dumps(exercise,indent=2)+'\n')
 with(p/'exercise.log').open('w')as stream:result=subprocess.run(exercise,stdout=stream,stderr=subprocess.STDOUT)
 (p/'exercise-result.json').write_text(json.dumps(dict(code=result.returncode,completedAt=time.time()),indent=2)+'\n')
 print('exercise',name,result.returncode,flush=True)
finally:
 collect=subprocess.run(prefix+['exec',name,'python3','/probe/collect.py'],capture_output=True,text=True)
 (p/'collect-result.json').write_text(json.dumps(dict(code=collect.returncode,stdout=collect.stdout,stderr=collect.stderr),indent=2)+'\n')
 (p/'finished').touch()
 with(p/'docker-wait.log').open('w')as log:wait=subprocess.run(prefix+['wait',container],text=True,stdout=log,stderr=subprocess.STDOUT)
 logs=subprocess.run(prefix+['logs',container],text=True,capture_output=True)
 (p/'session-stdout.log').write_text(logs.stdout)
 (p/'session-stderr.log').write_text(logs.stderr)
 exit_value=(p/'docker-wait.log').read_text().strip()
 (p/'session-result.json').write_text(json.dumps(dict(waitCode=wait.returncode,containerExit=exit_value,completedAt=time.time()),indent=2)+'\n')
 print('terminal',name,'wait',wait.returncode,'container',exit_value,'collect',collect.returncode,flush=True)
assert result.returncode==0 and collect.returncode==0 and wait.returncode==0 and exit_value=='0'
