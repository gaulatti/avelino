from pathlib import Path
import json, os, subprocess, time
p=Path('/probe');os.environ.update(json.loads((p/'session-env.json').read_text()))
import pyatspi
from gi.repository import GLib
pid=json.loads((p/'client-pid.json').read_text())['pid'];context=GLib.MainContext.default()
def spin(seconds=.8):
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        for _ in range(200):
            if not context.pending():break
            context.iteration(False)
        time.sleep(.02)
def root():return next(a for a in pyatspi.Registry.getDesktop(0)if a.get_process_id()==pid)
def walk(obj):
    obj.clear_cache();yield obj
    for child in obj:
        if child is not None:yield from walk(child)
def find(name,role):return next(o for o in walk(root())if o.name==name and o.getRoleName()==role and o.getState().contains(pyatspi.STATE_SHOWING))
def press(name,role='push button'):
    interface=find(name,role).queryAction();assert interface.doAction(next(i for i in range(interface.nActions)if interface.getName(i)=='Press'));spin()
phases=[]
for cycle in range(3):
    press('Choose file…');find('Open','frame')
    press('one.txt','list item');assert find('one.txt','list item').getState().contains(pyatspi.STATE_SELECTED)
    name='open-selected-'+str(cycle)
    subprocess.run(['python3','/probe/dump.py',name+'.json'],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['import','-window','root','/probe/'+name+'.png'],check=True)
    press('Open')
    assert any(o.getRoleName()=='label' and o.name.startswith('Selected URLs:') and o.name.endswith('file:///probe/fixtures/one.txt')for o in walk(root()))
    name='result-'+str(cycle)
    subprocess.run(['python3','/probe/dump.py',name+'.json'],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['import','-window','root','/probe/'+name+'.png'],check=True)
    phases.append(dict(cycle=cycle,selected='one.txt',ownerUrl='file:///probe/fixtures/one.txt'))
    print('cycle',cycle,'passed',flush=True)
(p/'operator-result.json').write_text(json.dumps(dict(accepted=False,status='passed',cycles=phases,
    captureMethod='External compositor capture; no QQuickWindow grabWindow calls',physicalDisplay=False,hardwareAcceleration=False),indent=2)+'\n')
