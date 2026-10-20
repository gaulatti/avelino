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
