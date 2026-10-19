from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];b=p.parent;gate=b/'weston-popup-display-v1';inputs=json.loads((p/'inputs.json').read_text());ctx=['docker','--context','colima-avelino-verify'];steps=[]
while not (gate/'result.json').exists():
 state=subprocess.run(ctx+['inspect','avelino-weston-popup-display-v1-20261018','--format','{{json .State}}'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if state.returncode==0:assert json.loads(state.stdout)['Running'],'Display container terminal; wait for its producer receipt'
 (p/'phase.json').write_text(json.dumps(dict(phase='waiting for complete display producer',cacheMutated=False,observedContainerRunning=state.returncode==0,observedAt=time.time()),indent=2)+'\n')
 time.sleep(10)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for n,v in inputs['files'].items():assert sha(r/n)==v,n
assert subprocess.check_output(ctx+['image','inspect',inputs['image'],'--format','{{.Id}}'],text=True).strip()==inputs['imageId']
work=b/'file-input-qt-v21/fresh-build'
previous=json.loads((b/'navigation-cjk-qt-v5/inputs.json').read_text())['files']
for n,v in previous.items():assert sha(work/'source'/n)==v,'Unexpected compiler cache mutation: '+n
for cid in subprocess.check_output(ctx+['ps','--format','{{.ID}}'],text=True).split():
 directory=subprocess.check_output(ctx+['inspect',cid,'--format','{{.Config.WorkingDir}}'],text=True).strip();assert 'file-input-qt-v21/fresh-build'not in directory
for n in inputs['changedInputs']:
 dest=work/'source'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p/'source'/n,dest)
assert all(sha(work/'source'/n)==v for n,v in inputs['files'].items())
(p/'activated-inputs.json').write_text(json.dumps(dict(previousValidatedProducer='navigation-cjk-qt-v5',cacheBytesMatchSnapshot=True,files={n:inputs['files'][n]for n in inputs['changedInputs']},priorDisplayGateResult=json.loads((gate/'result.json').read_text())),indent=2)+'\n')
base=ctx+['run','--rm','--ulimit','core=0','-v',str(r)+':/work','-w','/work/'+str((work/'source').relative_to(r))]
for n in ['evidence','reference','scripts','tools','tokens','docs']:base+=['-v',str(r/n)+':/work/'+str((work/'source'/n).relative_to(r))+':ro']
base+=[inputs['image']]
def run(name,args):
 (p/'phase.json').write_text(json.dumps(dict(phase=name,cacheMutated=True,observedAt=time.time()),indent=2)+'\n');started=time.monotonic()
 with(p/(name+'.log')).open('w')as log:result=subprocess.run(base+args,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=base+args,exitCode=result.returncode,seconds=time.monotonic()-started));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode:
  (p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=result.returncode,failedStep=name),indent=2)+'\n');raise SystemExit(result.returncode)
run('activate-inputs',['python3','-c','from pathlib import Path;import json,sys;[Path(n).touch()for n in json.loads(sys.argv[1])]',json.dumps(inputs['changedInputs'])])
run('configure',['cmake','-S','.','-B','../build','-G','Ninja','-DCMAKE_BUILD_TYPE=Debug','-DBUILD_TESTING=ON','-DCMAKE_INSTALL_PREFIX=/work/'+str(p.relative_to(r))+'/install'])
run('build',['cmake','--build','../build','--parallel','2'])
run('install',['cmake','--install','../build'])
for dpr in [1,2]:run('literal-dpr'+str(dpr),['env','QT_QPA_PLATFORM=offscreen','QT_QUICK_BACKEND=software','QT_SCALE_FACTOR='+str(dpr),'/opt/qt/bin/qmltestrunner','-input','tests/components/tst_date_literal_hits.qml','-import','../build/qml'])
run('date-tests',['env','QT_QPA_PLATFORM=offscreen','QT_QUICK_BACKEND=software','ctest','--test-dir','../build','--output-on-failure','-R','^date-range-(owned-input(-dpr2)?|calendar-components)$'])
shutil.copy2(work/'build/Testing/Temporary/LastTest.log',p/'ctest-last-test.log')
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,focusedLiteralRows=32,dateCTestGroups=3,all55TestsRerun=False),indent=2)+'\n');(p/'phase.json').write_text(json.dumps(dict(phase='complete',cacheMutated=True),indent=2)+'\n')
