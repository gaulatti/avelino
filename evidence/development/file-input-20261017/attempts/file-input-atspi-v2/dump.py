from pathlib import Path
import json,os,sys
p=Path('/probe');os.environ.update(json.loads((p/'session-env.json').read_text()))
import pyatspi
pid=json.loads((p/'client-pid.json').read_text())['pid'];desktop=pyatspi.Registry.getDesktop(0)
apps=[];selected=None
for app in desktop:
 try:info=dict(name=app.name,pid=app.get_process_id());apps.append(info)
 except Exception as error:apps.append(dict(error=repr(error)));continue
 if info['pid']==pid:selected=app
seen=0
def walk(obj,depth=0):
 global seen
 seen+=1
 if seen>500 or depth>12:return dict(truncated=True)
 row=dict(name=obj.name,role=obj.getRoleName(),description=obj.description,states=[str(s)for s in obj.getState().getStates()])
 try:r=obj.queryComponent().getExtents(pyatspi.DESKTOP_COORDS);row['bounds']=[r.x,r.y,r.width,r.height]
 except Exception as error:row['boundsError']=repr(error)
 try:a=obj.queryAction();row['actions']=[a.getName(i)for i in range(a.nActions)]
 except NotImplementedError:pass
 row['children']=[walk(child,depth+1)for child in obj if child is not None]
 return row
result=dict(accepted=False,applications=apps,targetPid=pid,tree=walk(selected)if selected is not None else None)
if len(sys.argv)>1:(p/sys.argv[1]).write_text(json.dumps(result,indent=2)+chr(10))
print(json.dumps(result,indent=2))
