from pathlib import Path
import json, os, subprocess, time

p = Path('/probe')
os.environ.update(json.loads((p / 'session-env.json').read_text()))
import pyatspi

pid = json.loads((p / 'client-pid.json').read_text())['pid']
app = next(a for a in pyatspi.Registry.getDesktop(0) if a.get_process_id() == pid)
def flatten(obj):
    yield obj
    for child in obj:
        if child is not None:
            yield from flatten(child)
trigger = next(o for o in flatten(app) if o.name == 'Choose file…' and o.getRoleName() == 'push button')
action = trigger.queryAction()
assert action.doAction(next(i for i in range(action.nActions) if action.getName(i) == 'SetFocus'))
time.sleep(.8)
assert trigger.getState().contains(pyatspi.STATE_FOCUSED)
assert action.doAction(next(i for i in range(action.nActions) if action.getName(i) == 'Press'))
time.sleep(.8)
subprocess.run(['python3', '/probe/dump.py', 'opened-v1.json'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['import', '-window', 'root', '/probe/opened-v1.png'], check=True)
print('AT-SPI trigger focused and pressed; open tree and screenshot retained')
