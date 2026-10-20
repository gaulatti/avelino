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
    focus=subprocess.run(['xdotool','getwindowfocus','getwindowname'],capture_output=True,text=True)
    transport=dict(keys=list(keys),focusStatus=focus.returncode,focusName=focus.stdout.strip(),focusError=focus.stderr.strip(),time=time.time())
    with (p/'native-key-transport.jsonl').open('a')as log:log.write(json.dumps(transport)+'\n')
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

try:
    def selected_rows():
        result=[]
        for obj in walk(app()):
            if not(obj.getState().contains(pyatspi.STATE_SHOWING) and obj.getState().contains(pyatspi.STATE_SELECTED)):continue
            if obj.getRoleName()=='list item':result.append(obj.name)
            elif obj.getRoleName()=='table cell' and obj.queryTableCell().position[-1]==0:result.append(obj.name)
        return sorted(result)
    
    base_tree=tree
    def tree(obj):
        row=base_tree(obj)
        row['attributes']=obj.getAttributes()
        try:
            table=obj.queryTable();row['table']=dict(rows=table.nRows,columns=table.nColumns)
        except NotImplementedError:pass
        try:
            cell=obj.queryTableCell();row['tableCell']=dict(position=list(cell.position),rowSpan=cell.rowSpan,columnSpan=cell.columnSpan,headers=[h.name for h in cell.columnHeaderCells])
        except NotImplementedError:pass
        try:row['selectedChildren']=obj.querySelection().nSelectedChildren
        except NotImplementedError:pass
        return row
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
    press_any('Where:');wait_for(lambda:present('fixtures','menu item'))
    record('location-current-menu',selected=selected_rows(),location=location())
    press('fixtures','menu item')
    assert selected_rows()==['one.txt'] and location()=='/probe/fixtures' and not enabled('Back') and not owner()
    record('location-current-preserves-selection',selected=selected_rows(),location=location())
    press_any('Where:');wait_for(lambda:present('fixtures','menu item'))
    assert action(find('fixtures','menu item'),'SetFocus');spin()
    key('Down');assert find('probe','menu item').getState().contains(pyatspi.STATE_FOCUSED)
    key('Up');assert find('fixtures','menu item').getState().contains(pyatspi.STATE_FOCUSED)
    key('Return');assert not present('fixtures','menu item') and selected_rows()==['one.txt'] and not enabled('Back') and not owner()
    record('location-native-keyboard-current',selected=selected_rows(),method='AT-SPI SetFocus and native XTest Down/Up/Return')

    press_any('Where:');wait_for(lambda:present('probe','menu item'));press('probe','menu item')
    assert location()=='/probe' and selected_rows()==[] and enabled('Back') and not owner()
    record('location-ancestor-clears-selection',selected=selected_rows(),location=location())
    press('Back');assert location()=='/probe/fixtures' and selected_rows()==[]
    assert action(find('one.txt','list item'),'Press');spin()
    press_any('Where:');wait_for(lambda:present('fixtures','menu item'));key('Escape')
    assert not present('fixtures','menu item') and present('Open','frame') and selected_rows()==['one.txt'] and not owner()
    record('location-menu-escape-keeps-chooser',selected=selected_rows(),location=location())
    choose_view('List','table cell')
    assert selected_rows()==['one.txt'] and not owner()
    assert not find('Date Added','push button').getState().contains(pyatspi.STATE_ENABLED)
    assert find('Date Added','push button').description=='Date Added is unavailable'
    record('list-retains-column-selection',selected=selected_rows(),dateAdded='unavailable',modal=True)
    folder=find('folder','table cell');assert folder.getState().contains(pyatspi.STATE_EXPANDABLE)
    assert folder.getState().contains(pyatspi.STATE_FOCUSABLE)
    table=find('Files in /probe/fixtures','tree').queryTable();assert table.nColumns==4 and table.nRows==5
    cell=find('one.txt','table cell').queryTableCell();assert cell.position[-1]==0 and cell.table.name=='Files in /probe/fixtures'
    assert [h.name for h in cell.columnHeaderCells]==['Name']
    assert not folder.getState().contains(pyatspi.STATE_EXPANDED)
    assert action(folder,'Toggle');spin()
    assert present('child.txt','table cell') and find('folder','table cell').getState().contains(pyatspi.STATE_EXPANDED)
    record('list-accessible-disclosure',expanded=True,location=location())
    assert action(find('child.txt','table cell'),'Press');spin()
    # AT-SPI Selection is the assistive API for adding a row; Action.Press
    # does not supply keyboard event modifiers. The failed mixed XTest/Press
    # attempts remain recorded separately.
    cell=find('one.txt','table cell')
    view=find('Files in /probe/fixtures','tree')
    index=cell.getIndexInParent()
    assert view.querySelection().selectChild(index);spin()
    assert selected_rows()==['child.txt','one.txt']
    record('list-cross-level-selection',selected=selected_rows(),method='AT-SPI Selection.selectChild')
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
    choose_view('List','table cell')
    assert present('child.txt','table cell')
    # Restore alphabetic order before the measured parent -> child keyboard route.
    press('Name');assert find('Name','push button').description=='Ascending'
    assert action(find('folder','table cell'),'Press');spin();key('Left')
    assert not present('child.txt','table cell')
    record('list-left-collapses',selected=selected_rows())
    key('Right');assert present('child.txt','table cell')
    key('Down');assert selected_rows()==['child.txt']
    record('list-keyboard-selects-child',selected=selected_rows())
    key('Return');wait_for(lambda:bool(owner()))
    assert not present('Open','frame') and 'folder/child.txt' in owner()
    focus_returned();accepted_owner=owner()
    record('child-owner-result',owner=accepted_owner)
    key('space');dialog_named('Open')
    assert location()=='/probe/fixtures' and present('child.txt','table cell') and selected_rows()==[]
    assert not enabled('Back') and not enabled('Forward') and not enabled('Open')
    record('reopen-retains-list-and-disclosure',location=location(),selected=[])
    enter_location('/probe/fixtures/missing')
    wait_for(lambda:'No such file or directory'in announcement_messages())
    assert not enabled('Open')
    record('invalid-location-announced',location=location())
    press('Back');assert location()=='/probe/fixtures' and present('child.txt','table cell')
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
    press_any('Where:');wait_for(lambda:present('fixtures','menu item'))
    recent=[obj for obj in walk(app())if obj.getState().contains(pyatspi.STATE_SHOWING) and obj.name=='fixtures' and obj.getRoleName()=='menu item']
    assert len(recent)==2,len(recent)
    record('location-recent-menu-after-reopen',location=location(),matchingFolderItems=len(recent),owner=owner())
    assert action(recent[-1],'Press');spin()
    assert location()=='/probe/fixtures' and selected_rows()==[] and owner()==accepted_owner
    record('location-recent-navigates-without-owner',location=location(),owner=owner())
    press('Back');assert location()==created and owner()==accepted_owner
    press('Forward');assert location()=='/probe/fixtures' and present('child.txt','table cell') and selected_rows()==[]
    record('list-history-after-creation',location=location())
    press_any('Where:');wait_for(lambda:present('fixtures','menu item'))
    with (p/'other-client.log').open('wb')as log:
        other=subprocess.Popen(['install/bin/AvelinoCatalog','--fixture','file-input','--file-input-folder','/probe/fixtures'],stdout=log,stderr=subprocess.STDOUT)
    try:
        wait_for(lambda:not present('fixtures','menu item'))
        assert present('Open','frame') and owner()==accepted_owner
        record('location-deactivation-closes-menu',owner=owner(),otherPid=other.pid)
    finally:
        other.terminate();other.wait(timeout=5)
    close_panel();assert owner()==accepted_owner
    record('final-cancel-preserves-owner',owner=owner())
    events=announcements();assert len(events)==2 and all(e['detail1']==2 for e in events),events
    (q/'result.json').write_text(json.dumps(dict(accepted=False,status='passed',profile=profile,phases=phases,
        announcementEvents=events,modalStateExposed=True,libraryProjectSourcesMounted=False,physicalInput=False,
        physicalListening=False,nativeAccessibilityAcceptance='pending',nativeReaderComparison='pending'),indent=2)+'\n')
except Exception:
    record('operator-failure',error=traceback.format_exc())
    raise
