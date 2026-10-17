from pathlib import Path
import json, os, signal, subprocess, time
p = Path('/probe')
os.environ.update(json.loads((p/'session-env.json').read_text()))
import pyatspi
pid = json.loads((p/'client-pid.json').read_text())['pid']
root = next(o for o in pyatspi.Registry.getDesktop(0) if o.get_process_id() == pid)
def walk(obj):
    yield obj
    for child in obj:
        if child is not None: yield from walk(child)
trigger = next(o for o in walk(root) if o.name == 'Choose file…' and o.getRoleName() == 'push button')
actions = trigger.queryAction()
for name in ['SetFocus', 'Press']:
    assert actions.doAction(next(i for i in range(actions.nActions) if actions.getName(i) == name))
    time.sleep(.8)
subprocess.run(['xdotool','key','Down','Down'],check=True)
time.sleep(3)
os.kill(json.loads((p/'orca-pid.json').read_text())['pid'], signal.SIGUSR1)
subprocess.run(['python3','/probe/dump.py','reader-one-selected.json'],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['import','-window','root','/probe/reader-one-selected.png'],check=True)
print('Reader row-selection diagnostic and stack retained')
