from pathlib import Path
import json, os, subprocess

p = Path('/probe')
os.environ.update(json.loads((p / 'session-env.json').read_text()))
assert not (p / 'orca-pid.json').exists(), 'Retain an existing reader session'
command = ['orca', '--replace', '--user-prefs=/probe/orca-prefs-v1',
           '--disable=braille', '--enable=speech', '--debug-file=/probe/orca-debug-v1.log']
with (p / 'orca-stdout-v1.log').open('wb') as log:
    reader = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
(p / 'orca-pid.json').write_text(json.dumps(dict(pid=reader.pid, command=command), indent=2) + '\n')
print(reader.pid)
