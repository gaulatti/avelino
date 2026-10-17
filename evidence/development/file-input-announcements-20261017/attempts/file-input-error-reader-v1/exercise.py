"""Operate the installed catalog through AT-SPI and XTest, retaining raw trees."""
from pathlib import Path
import json, os, subprocess, time, traceback

p = Path('/probe')
os.environ.update(json.loads((p / 'session-env.json').read_text()))
import pyatspi
from gi.repository import GLib

q = p / 'operator-errors-v1'
q.mkdir(exist_ok=False)
pid = json.loads((p / 'client-pid.json').read_text())['pid']
context = GLib.MainContext.default()
phases = []
def spin(seconds=.35):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        for _ in range(200):
            if not context.pending(): break
            context.iteration(False)
        time.sleep(.02)
def app():
    return next(o for o in pyatspi.Registry.getDesktop(0) if o.get_process_id() == pid)
def walk(obj):
    obj.clear_cache()
    yield obj
    for child in obj:
        if child is not None: yield from walk(child)
def find(name, role=None):
    return next(o for o in walk(app()) if o.getState().contains(pyatspi.STATE_SHOWING) and o.name == name and (role is None or o.getRoleName() == role))
def present(name, role=None):
    try: find(name, role); return True
    except StopIteration: return False
def action(obj, name):
    interface = obj.queryAction()
    return interface.doAction(next(i for i in range(interface.nActions) if interface.getName(i) == name))
def press(name, role='push button'):
    assert action(find(name, role), 'Press'), (name, 'Press rejected')
    spin()
def key(*keys):
    subprocess.run(['xdotool', 'key', '--clearmodifiers', *keys], check=True)
    spin()
def enabled(name): return find(name, 'push button').getState().contains(pyatspi.STATE_ENABLED)
def selected(): return sorted(o.name for o in walk(app()) if o.getRoleName() == 'list item' and o.getState().contains(pyatspi.STATE_SHOWING) and o.getState().contains(pyatspi.STATE_SELECTED))
def open_panel():
    press('Choose file…')
    assert present('Open', 'frame')
def close_panel():
    press('Cancel')
    assert not present('Open', 'frame')
    assert find('Choose file…', 'push button').getState().contains(pyatspi.STATE_FOCUSED)
def owner():
    return next((o.name for o in walk(app()) if o.getRoleName() == 'label' and o.name.startswith('Selected URLs:')), '')
def tree(obj):
    row = dict(name=obj.name, role=obj.getRoleName(), description=obj.description,
               states=[str(s) for s in obj.getState().getStates()])
    try:
        bounds = obj.queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
        row['bounds'] = [bounds.x, bounds.y, bounds.width, bounds.height]
    except NotImplementedError: pass
    try:
        actions = obj.queryAction()
        row['actions'] = [actions.getName(i) for i in range(actions.nActions)]
    except NotImplementedError: pass
    row['children'] = [tree(child) for child in obj if child is not None]
    return row
def record(name, **observations):
    spin(.6)
    row = dict(phase=name, time=time.time(), observations=observations, readerLogBytes=(p/'orca-debug.log').stat().st_size)
    (q/(name+'.json')).write_text(json.dumps(dict(accepted=False, targetPid=pid, tree=tree(app()), **row), indent=2)+'\n')
    subprocess.run(['import', '-window', 'root', str(q/(name+'.png'))], check=True)
    phases.append(row)
    (q/'operator-report.json').write_text(json.dumps(dict(accepted=False, status='running', phases=phases), indent=2)+'\n')
    print(name, flush=True)


def announcements():
    return [json.loads(line) for line in (p/'events.jsonl').read_text().splitlines() if '"event": "object:announcement"' in line]
def wait_for(predicate):
    end=time.monotonic()+10
    while not predicate():
        if time.monotonic()>end:raise AssertionError('Expected AT-SPI/Orca observation did not arrive')
        spin(.1)
def enter_location(value):
    key('ctrl+l')
    subprocess.run(['xdotool','type','--clearmodifiers','--',value],check=True)
    key('Return')
open_panel()
assert announcements()==[]
start=(p/'orca-debug.log').stat().st_size
enter_location('/probe/fixtures/missing')
wait_for(lambda:len(announcements())==1)
first=announcements()[0]
assert first['message']=='No such file or directory' and first['detail1']==2,first
wait_for(lambda:"SPEECH OUTPUT: 'No such file or directory" in (p/'orca-debug.log').read_bytes()[start:].decode())
assert not enabled('Open') and present('No such file or directory','label')
record('invalid-location-announced',event=first)
enter_location('/probe/fixtures')
assert not present('No such file or directory','label')
assert len(announcements())==1
record('location-recovered')
enter_location('/probe/fixtures/missing-again')
wait_for(lambda:len(announcements())==2)
assert all(e['message']=='No such file or directory' and e['detail1']==2 for e in announcements())
record('second-error-announced',events=announcements())
key('Escape')
assert not present('Open','frame')
spin(.5);assert len(announcements())==2
record('cancelled-no-extra-announcement')
(q/'result.json').write_text(json.dumps(dict(accepted=False,status='passed',announcementEvents=announcements(),phases=phases,reader='Orca 46.1',audioOutput='ALSA null device',physicalListening=False,nativeReaderComparison='pending'),indent=2)+'\n')
