from pathlib import Path
p=Path('/Users/gaulatti/.codex/tmp/run-avelino-media-library-reflow-operator-20261017.py');s=p.read_text()
s=s.replace('media-library-reflow-operator-v1','app-tabs-operator-v1').replace('media-library-reflow-build-v5','app-tabs-build-v8').replace('media-library','app-tabs').replace('MediaLibrary','AppTabs').replace('Avelino media library','Avelino app tabs')
start=s.index('items=[dict(');end=s.index("(p/'phases.json').write_text",start)
s=s[:start]+'''tabs=[dict(value=v,label=l,systemImage=i,**({'badge':'7'}if v=='b'else{}))for v,l,i in [('a','Home','house'),('b','Inbox','tray'),('c','Settings','gearshape')]]
configuration=dict(id='default',tabs=tabs,selection='a',valueKind='string',width=300,height=None,rtl=False,disabled=False,parentFont=False,parentRed=False,owner='echo')
phases=[];dark=False;scale=1;selection='a';pending=None
reversed_tabs=list(reversed(tabs));badges=[dict(t,badge='100')for t in reversed_tabs]
updates=[('initial',None,{},None),('inbox','tab-b',{},'b'),('observe','owner-observe',dict(owner='observe'),None),('observe-home','tab-a',{},'a'),('delayed','owner-delayed',dict(owner='delayed'),None),('delayed-settings','tab-c',{},'c'),('flush','flush',{},None),('redirect','owner-redirect',dict(owner='redirect'),None),('redirect-inbox','tab-b',{},'b'),('external','external',{},None),('echo','owner-echo',dict(owner='echo'),None),('echo-inbox','tab-b',{},'b'),('reverse','reorder',dict(tabs=reversed_tabs),None),('badges','badges',dict(tabs=badges),None),('narrow','width',dict(width=30),None),('rtl','rtl',dict(rtl=True),None),('dark','theme',{},None),('scaled','scale',{},None),('disabled','disabled',dict(disabled=True),None),('disabled-home','tab-a',{},'a'),('enabled','disabled',dict(disabled=False),None),('empty','empty',dict(tabs=[]),None),('restore','empty',dict(tabs=tabs),None),('width150','width',dict(width=150),None),('width300','width',dict(width=300),None),('ltr','rtl',dict(rtl=False),None),('light','theme',{},None),('scale-restored','scale',{},None)]
for name,control,update,requested in updates:
 oldscale=scale;configuration.update(update)
 if control=='theme':dark=not dark
 if control=='scale':scale=1.5 if scale==1 else 1
 if requested is not None and not configuration['disabled']:
  if configuration['owner']=='echo':selection=requested
  elif configuration['owner']=='delayed':pending=requested
  elif configuration['owner']=='redirect':selection=configuration['tabs'][0]['value']
 if control=='flush'and pending is not None:selection=pending;pending=None
 if control=='external':selection='c'
 definition=dict(configuration,id='operator-'+name,fixture='app-tabs-operator-'+name,api='BleeckerAppTabBar',source='fe8a1d462fbd793d883fb92086a16aa2947e32c9',tabWidth=configuration['width'],tabHeight=configuration['height'],width=640,height=400,selection=selection)
 phases.append(dict(name=name,control=control,scaleBefore=oldscale,dark=dark,textScale=scale,selection=selection,pending=pending,definition=copy.deepcopy(definition)))
'''+s[end:]
s=s.replace("captionRows=[(24,['slot-'+s for s in ['fill','fixed','text','button']]+['data','reorder','empty']),(80,['size','minimum','scroll','rtl','theme','scale','disabled'])]","captionRows=[(24,['owner-'+s for s in ['echo','observe','delayed','redirect']]+['flush','external','reorder','empty']),(80,['width','badges','disabled','rtl','theme','scale'])]")
s=s.replace("for row in phases:\n  click=None","for index,row in enumerate(phases):\n  click=None")
s=s.replace("   target=controls[row['scaleBefore']][row['control']];click=",'''   if row['control'].startswith('tab-'):
    previous=phases[index-1];value=row['control'][4:];i=next(i for i,t in enumerate(previous['definition']['tabs'])if t['value']==value)
    meta=json.loads((p/'references'/(previous['name']+'.png.json')).read_text());frame=meta['appTabFrame']['button-'+str(i)]
    target=dict(x=frame['x'],y=frame['y']+180,width=frame['width'],height=frame['height'])
   else:target=controls[row['scaleBefore']][row['control']]
   click=''')
s=s.replace('crop((24,200,664,600))','crop((0,180,640,580))').replace('viewport=[24,200,640,400]','viewport=[0,180,640,400]')
Path('/Users/gaulatti/.codex/tmp/run-avelino-app-tabs-operator-20261017.py').write_text(s)
print('Prepared 28-phase gallery operator driver')
