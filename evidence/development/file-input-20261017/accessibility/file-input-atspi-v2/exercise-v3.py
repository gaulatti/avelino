"""Operate the installed catalog through AT-SPI and XTest, retaining raw trees."""
from pathlib import Path
import json, os, subprocess, time, traceback

p = Path('/probe')
os.environ.update(json.loads((p / 'session-env.json').read_text()))
import pyatspi
from gi.repository import GLib

q = p / 'operator-v3'
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

try:
    key('Escape')
    record('operator-initial')
    for name, allowed in [('Text', {'one.txt','two.txt'}), ('Images', {'photo.png'}),
            ('Folders', {'Folder'}), ('Text + images', {'one.txt','two.txt','photo.png'}),
            ('Folders + text', {'Folder','one.txt','two.txt'}),
            ('All files', {'one.txt','two.txt','photo.png'}), ('Empty types', set()), ('Undeclared', set())]:
        press(name); open_panel()
        rows = [o for o in walk(app()) if o.getRoleName() == 'list item' and o.getState().contains(pyatspi.STATE_SHOWING)]
        actual = {o.name for o in rows if o.getState().contains(pyatspi.STATE_SELECTABLE)}
        assert actual == allowed, (name, actual, allowed)
        assert find('Files in /probe/fixtures','list').getState().contains(pyatspi.STATE_FOCUSABLE)
        for filename in ['one.txt','photo.png']:
            press(filename, 'list item')
            assert enabled('Open') == bool(allowed.intersection(selected())), (name,filename,selected())
        record('types-'+name.lower().replace(' + ', '-and-').replace(' ','-'), eligible=sorted(actual), selection=selected())
        close_panel()
    press('Text');open_panel();press('one.txt','list item')
    row=find('two.txt','list item').queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
    subprocess.run(['xdotool','keydown','Control_L'],check=True)
    try: subprocess.run(['xdotool','mousemove','--sync',str(row.x+row.width//2),str(row.y+row.height//2),'click','1'],check=True)
    finally: subprocess.run(['xdotool','keyup','Control_L'],check=True)
    spin();assert selected()==['one.txt','two.txt'],selected()
    record('multiple-selected', selection=selected())
    press('Open');assert not present('Open','frame')
    assert owner()=='Selected URLs: file:///probe/fixtures/one.txt, file:///probe/fixtures/two.txt',owner()
    record('multiple-result', owner=owner())
    before=owner();open_panel();close_panel();assert owner()==before
    record('cancel-preserves-result',owner=owner())
    open_panel();key('Escape');assert not present('Open','frame') and owner()==before
    assert find('Choose file…','push button').getState().contains(pyatspi.STATE_FOCUSED)
    key('space');assert present('Open','frame')
    record('keyboard-reopened')
    key('Down');key('Down');assert selected()==['one.txt'],selected()
    record('keyboard-one-selected',selection=selected())
    key('Return');assert not present('Open','frame')
    assert owner().endswith('file:///probe/fixtures/one.txt'),owner()
    record('keyboard-result',owner=owner())
    press('Change title');assert present('Import documents','push button')
    record('title-changed')
    press('Change title');assert present('Choose file…','push button')
    press('Disabled');assert not enabled('Choose file…')
    press('Choose file…');assert not present('Open','frame')
    record('disabled-trigger')
    press('Disabled');assert enabled('Choose file…')
    press('RTL');record('rtl-trigger');press('RTL')
    press('Theme');record('dark-trigger');press('Theme')
    press('Text scale');record('scaled-trigger');press('Text scale')
    press('Remove in callback');open_panel();press('one.txt','list item');press('Open')
    assert not present('Open','frame') and not present('Choose file…','push button')
    assert owner().endswith('file:///probe/fixtures/one.txt')
    record('owner-removed',owner=owner())
    press('Remount');assert present('Choose file…','push button')
    record('owner-remounted')
    (q/'operator-report.json').write_text(json.dumps(dict(accepted=False,status='passed',phases=phases,
        nativePanelAcceptance='pending',physicalDisplay=False,physicalReaderAcceptance='pending'),indent=2)+'\n')
except Exception as error:
    traceback.print_exc()
    (q/'operator-failure.json').write_text(json.dumps(dict(accepted=False,status='failed',error=repr(error),phases=phases),indent=2)+'\n')
    raise
