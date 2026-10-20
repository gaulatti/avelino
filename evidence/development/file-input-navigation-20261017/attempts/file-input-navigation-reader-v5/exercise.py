"""Operate the installed catalog through AT-SPI and XTest, retaining raw trees."""
from pathlib import Path
import json, os, subprocess, time, traceback

p = Path('/probe')
os.environ.update(json.loads((p / 'session-env.json').read_text()))
import pyatspi
from gi.repository import GLib

q = p / 'operator-controls-v1'
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
    desktop=pyatspi.Registry.getDesktop(0)
    desktop.clear_cache()
    return next(o for o in desktop if o is not None and o.get_process_id() == pid)
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
    start=time.monotonic()
    try:
        wait_for(lambda:present('Choose file…','push button') and find('Choose file…','push button').getState().contains(pyatspi.STATE_FOCUSED))
    except Exception:
        record('close-focus-missing',focus=[dict(name=o.name,role=o.getRoleName())for o in walk(app())if o.getState().contains(pyatspi.STATE_FOCUSED)])
        raise
    (p/'focus-restoration-seconds.txt').open('a').write(str(time.monotonic()-start)+'\n')
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

profile=json.loads((p/'profile.json').read_text())
def dialog_named(name):
    matches=[o for o in walk(app()) if o.getState().contains(pyatspi.STATE_SHOWING) and o.name==name and o.getRoleName()=='dialog']
    assert len(matches)==1,(name,len(matches))
    obj=matches[0]
    assert obj.getState().contains(pyatspi.STATE_MODAL),(name,'modal state missing')
    return obj

def within_dialog(name,role):
    return next(o for o in walk(dialog_named('New Folder')) if o.getState().contains(pyatspi.STATE_SHOWING) and o.name==name and o.getRoleName()==role)
def create_enabled():return within_dialog('Create','push button').getState().contains(pyatspi.STATE_ENABLED)
def text_value(obj):return obj.queryText().getText(0,-1)
def location():return text_value(find('Folder location','text'))
def type_value(value):
    key('ctrl+a')
    subprocess.run(['xdotool','type','--clearmodifiers','--',value],check=True);spin()
def announcement_messages():return [e['message']for e in announcements()]

wait_for(lambda:present('Choose file…','push button'))
assert not owner()
open_panel();dialog_named('Open')
assert location()=='/probe/fixtures' and not enabled('Back') and not enabled('Forward')
press('New Folder');modal=dialog_named('New Folder')
assert text_value(within_dialog('New folder name','text'))=='untitled folder 2' and create_enabled()
record('new-folder-default-modal',defaultName='untitled folder 2',modal=True)
type_value('one.txt')
wait_for(lambda:not create_enabled() and 'This name is already taken.'in announcement_messages())
assert present('This name is already taken.','label')
record('duplicate-name-disabled',announcements=announcements())
key('ctrl+a');key('BackSpace');assert not create_enabled()
record('empty-name-disabled')
key('Escape');assert not present('New Folder','dialog');dialog_named('Open')
assert not (p/'fixtures/untitled folder 2').exists() and not owner()
record('nested-escape-no-mutation')
key('ctrl+shift+n');dialog_named('New Folder')
assert text_value(within_dialog('New folder name','text'))=='untitled folder 2'
type_value('Created by reader');assert create_enabled();key('Return')
wait_for(lambda:not present('New Folder','dialog'))
created='/probe/fixtures/Created by reader'
assert Path(created).is_dir() and location()==created and not enabled('Open') and not owner()
record('created-and-navigated',location=location(),ownerResult=False)
press('Back');assert location()=='/probe/fixtures' and enabled('Forward')
record('history-back',location=location())
press('Forward');assert location()==created and not enabled('Forward')
record('history-forward',location=location())
enter_location('/probe/fixtures/missing')
wait_for(lambda:'No such file or directory'in announcement_messages())
assert not enabled('New Folder') and not enabled('Open')
record('invalid-location-announced',location=location())
press('Back');assert location()==created and enabled('New Folder')
assert not present('No such file or directory','label') and not owner()
record('history-recovers-location-error',location=location())
close_panel();assert not owner()
record('cancel-no-owner-result')
key('space');dialog_named('Open');assert location()==created and not enabled('Back') and not enabled('Forward')
record('reopen-retained-folder-fresh-history',location=location())
close_panel();assert not owner()
record('final-cancel-no-owner-result')
events=announcements();assert len(events)==2 and all(e['detail1']==2 for e in events),events
(q/'result.json').write_text(json.dumps(dict(accepted=False,status='passed',profile=profile,phases=phases,announcementEvents=events,modalStateExposed=True,physicalInput=False,physicalListening=False,nativeAccessibilityAcceptance='pending',nativeReaderComparison='pending'),indent=2)+'\n')
