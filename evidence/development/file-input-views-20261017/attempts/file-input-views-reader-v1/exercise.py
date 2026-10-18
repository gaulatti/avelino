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

def selected_rows():
    return sorted(o.name for o in walk(app()) if o.getRoleName() in ['tree item','list item']
                  and o.getState().contains(pyatspi.STATE_SHOWING) and o.getState().contains(pyatspi.STATE_SELECTED))
def press_any(name):
    obj=find(name)
    assert action(obj,'Press'),name
    spin()
def choose_view(name,role):
    press_any('View Options')
    assert present(name),name
    press_any(name)
    wait_for(lambda:present('one.txt',role))
def focus_returned():
    start=time.monotonic()
    wait_for(lambda:present('Choose file…','push button') and find('Choose file…','push button').getState().contains(pyatspi.STATE_FOCUSED))
    (p/'focus-restoration-seconds.txt').open('a').write(str(time.monotonic()-start)+'\n')

assert not Path('/work/src/Avelino').exists() and not Path('/probe/src').exists() and not Path('/probe/consumer').exists()
wait_for(lambda:present('Choose file…','push button'))
assert not owner()
open_panel();dialog_named('Open')
assert location()=='/probe/fixtures'
assert action(find('one.txt','list item'),'Press');spin()
choose_view('List','tree item')
assert selected_rows()==['one.txt'] and not owner()
assert not find('Date Added','push button').getState().contains(pyatspi.STATE_ENABLED)
assert find('Date Added','push button').description=='Date Added is unavailable'
record('list-retains-column-selection',selected=selected_rows(),dateAdded='unavailable',modal=True)
folder=find('folder','tree item');assert folder.getState().contains(pyatspi.STATE_EXPANDABLE)
assert not folder.getState().contains(pyatspi.STATE_EXPANDED)
assert action(folder,'Toggle');spin()
assert present('child.txt','tree item') and find('folder','tree item').getState().contains(pyatspi.STATE_EXPANDED)
record('list-accessible-disclosure',expanded=True,location=location())
assert action(find('child.txt','tree item'),'Press');spin()
subprocess.run(['xdotool','keydown','ctrl'],check=True);spin(.15)
try:
    assert action(find('one.txt','tree item'),'Press');spin()
finally:
    subprocess.run(['xdotool','keyup','ctrl'],check=True);spin()
assert selected_rows()==['child.txt','one.txt']
record('list-cross-level-selection',selected=selected_rows())
press('Name');assert selected_rows()==['child.txt','one.txt']
assert find('Name','push button').description=='Descending'
record('list-sort-preserves-identities',selected=selected_rows(),nameOrder='descending')
choose_view('Icons','list item')
assert selected_rows()==['one.txt'] and location()=='/probe/fixtures' and not owner()
record('icons-prunes-hidden-child',selected=selected_rows())
assert action(find('folder','list item'),'Press');spin()
assert selected_rows()==['folder'] and enabled('Open') and location()=='/probe/fixtures'
press('Open');assert location()=='/probe/fixtures/folder' and not enabled('Open') and not owner()
record('icons-folder-open-navigates',location=location(),ownerResult=False)
press('Back');assert location()=='/probe/fixtures' and selected_rows()==[] and not enabled('Open')
record('history-clears-view-selection',location=location())
choose_view('List','tree item')
assert present('child.txt','tree item')
# Restore alphabetic order before the measured parent -> child keyboard route.
press('Name');assert find('Name','push button').description=='Ascending'
assert action(find('folder','tree item'),'Press');spin();key('Left')
assert not present('child.txt','tree item')
record('list-left-collapses',selected=selected_rows())
key('Right');assert present('child.txt','tree item')
key('Down');assert selected_rows()==['child.txt']
record('list-keyboard-selects-child',selected=selected_rows())
key('Return');wait_for(lambda:bool(owner()))
assert not present('Open','frame') and 'folder/child.txt' in owner()
focus_returned();accepted_owner=owner()
record('child-owner-result',owner=accepted_owner)
key('space');dialog_named('Open')
assert location()=='/probe/fixtures' and present('child.txt','tree item') and selected_rows()==[]
assert not enabled('Back') and not enabled('Forward') and not enabled('Open')
record('reopen-retains-list-and-disclosure',location=location(),selected=[])
enter_location('/probe/fixtures/missing')
wait_for(lambda:'No such file or directory'in announcement_messages())
assert not enabled('Open')
record('invalid-location-announced',location=location())
press('Back');assert location()=='/probe/fixtures' and present('child.txt','tree item')
assert not present('No such file or directory','label')
record('list-history-recovers-location',location=location())
press('New Folder');dialog_named('New Folder')
assert text_value(within_dialog('New folder name','text'))=='untitled folder 2'
type_value('one.txt')
wait_for(lambda:not create_enabled() and 'This name is already taken.'in announcement_messages())
record('nested-folder-error-announced',modal=True)
key('Escape');assert not present('New Folder','dialog') and owner()==accepted_owner
key('ctrl+shift+n');dialog_named('New Folder')
type_value('Created by views reader');key('Return')
wait_for(lambda:not present('New Folder','dialog'))
created='/probe/fixtures/Created by views reader'
assert Path(created).is_dir() and location()==created and not enabled('Open') and owner()==accepted_owner
record('list-new-folder-creates-and-navigates',location=location(),owner=owner())
press('Back');assert location()=='/probe/fixtures' and present('child.txt','tree item') and selected_rows()==[]
record('list-history-after-creation',location=location())
close_panel();assert owner()==accepted_owner
record('final-cancel-preserves-owner',owner=owner())
events=announcements();assert len(events)==2 and all(e['detail1']==2 for e in events),events
(q/'result.json').write_text(json.dumps(dict(accepted=False,status='passed',profile=profile,phases=phases,
    announcementEvents=events,modalStateExposed=True,libraryProjectSourcesMounted=False,physicalInput=False,
    physicalListening=False,nativeAccessibilityAcceptance='pending',nativeReaderComparison='pending'),indent=2)+'\n')
