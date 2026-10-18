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
subprocess.run(['xdotool','keydown','ctrl'],check=True);spin(.15)
try:
    assert action(find('one.txt','table cell'),'Press');spin()
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
press('Back');assert location()=='/probe/fixtures' and present('child.txt','table cell') and selected_rows()==[]
record('list-history-after-creation',location=location())
close_panel();assert owner()==accepted_owner
record('final-cancel-preserves-owner',owner=owner())
events=announcements();assert len(events)==2 and all(e['detail1']==2 for e in events),events
(q/'result.json').write_text(json.dumps(dict(accepted=False,status='passed',profile=profile,phases=phases,
    announcementEvents=events,modalStateExposed=True,libraryProjectSourcesMounted=False,physicalInput=False,
    physicalListening=False,nativeAccessibilityAcceptance='pending',nativeReaderComparison='pending'),indent=2)+'\n')
