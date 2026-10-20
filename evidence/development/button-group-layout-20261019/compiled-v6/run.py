from pathlib import Path
import ctypes,hashlib,json,os,shutil,subprocess,time
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
BASE=P.parent
IMAGE='sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3'
DOCKER=['docker','--context','colima-avelino-verify']
OUTPUT=P/'output'; PACKAGE=OUTPUT/'package'
commands=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def run(n,c):
 write('phase.json',dict(phase=n,startedAt=time.time()))
 start=time.monotonic()
 with (P/(n+'.log')).open('x') as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT)
 commands.append(dict(name=n,command=c,exitCode=r.returncode,seconds=time.monotonic()-start));write('commands.json',commands)
 print(n,r.returncode,flush=True)
 assert r.returncode==0,(n,r.returncode)
def clone_tree(src,dst):
 clone=ctypes.CDLL(None,use_errno=True).clonefile;clone.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int]
 count=size=0;dst.mkdir()
 for parent,dirs,files in os.walk(src,followlinks=False):
  relative=Path(parent).relative_to(src)
  for n in dirs[:]:
   a,b=Path(parent)/n,dst/relative/n
   if a.is_symlink():b.symlink_to(os.readlink(a));dirs.remove(n)
   else:b.mkdir()
  for n in files:
   a,b=Path(parent)/n,dst/relative/n
   if a.is_symlink():b.symlink_to(os.readlink(a))
   else:
    if clone(os.fsencode(a),os.fsencode(b),0):raise OSError(ctypes.get_errno(),str(a))
    count+=1;size+=a.stat().st_size
 return dict(files=count,logicalBytes=size,method='APFS clonefile')
try:
 previous=BASE/'button-group-compiled-v3'
 prior_result=json.loads((previous/'result.json').read_text())
 assert prior_result['exitCode']==0 and prior_result['coreTestsPassed']
 prior=json.loads((previous/'inputs.json').read_text())
 final_inputs=json.loads((BASE/'button-group-compiled-v5/inputs.json').read_text())
 changed={n for n,h in final_inputs['sourceFiles'].items() if sha(ROOT/n)!=h}
 assert changed=={'samples/AvelinoCatalog/main.cpp'},changed
 failure=json.loads((BASE/'button-group-runtime-v1/result.json').read_text())
 assert failure['exitCode']==1
 assert 'Invalid isolated geometry or expected-empty contract' in (BASE/'button-group-runtime-v1/catalog-008.log').read_text()
 write('legacy-alias-change.json',json.loads((BASE/'button-group-compiled-v5/legacy-alias-change.json').read_text()))
 write('continuation.json',dict(previous='button-group-compiled-v5',failure='Catalog rejected valid source zero-sized group',changedFiles=sorted(changed),fullCoreProducer='button-group-compiled-v3',consumerSourceUnchanged=True))

 paths=[ROOT/'CMakeLists.txt']
 for name in ['src','tests','samples','reference']:
  paths.extend(p for p in (ROOT/name).rglob('*') if p.is_file())
 for name in ['footer','button-group']:
  paths.append(ROOT/f'evidence/reference-investigations/{name}-slots-20261019/captures.json')
 frozen={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}
 write('inputs.json',dict(sourceBase=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sourceFiles=frozen,imageId=IMAGE,completeFreshBuild=False,fullMirrorAccepted=False,driverSha256=sha(P/'run.py')))
 OUTPUT.mkdir();PACKAGE.mkdir();(OUTPUT/'artifacts').mkdir()
 reuse=clone_tree(BASE/'button-group-compiled-v5/output/build',OUTPUT/'build');write('build-reuse.json',reuse)
 compile=DOCKER+['run','--init','--rm','--ulimit','core=0','-v',str(ROOT)+':/work:ro','-v',str(OUTPUT/'build')+':/work/build','-v',str(PACKAGE)+':/package','-v',str(OUTPUT/'artifacts')+':/work/artifacts','-w','/work','-e','QML_IMPORT_PATH=/work/build/linux/qml',IMAGE]
 run('configure',compile+['cmake','-S','/work','-B','/work/build/linux','-G','Ninja','-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DBUILD_TESTING=ON'])
 run('build',compile+['cmake','--build','/work/build/linux','--parallel','2'])
 for dpr in [1,2]:
  run('button-group-preflight-dpr'+str(dpr),compile+['env','QT_QPA_PLATFORM=offscreen','QT_QUICK_BACKEND=software','QT_SCALE_FACTOR='+str(dpr),'/work/build/linux/tests/components/AvelinoComponentTests','-input','/work/tests/components/tst_button_group.qml','-import','/work/build/linux/qml'])
 changes=[n for n,h in frozen.items() if prior['sourceFiles'].get(n)!=h]
 assert set(changes)=={'samples/AvelinoCatalog/main.cpp','tests/consumer/ButtonGroupCase.qml'},changes
 write('core-inheritance.json',dict(producer='button-group-compiled-v3',resultSha256=sha(previous/'result.json'),logSha256=sha(previous/'core-tests.log'),sourceChangesSinceFullSuite=changes,sharedRowEngineUnchanged=True,catalogEmptyContractAdded=True,fullSuiteRepeated=False))
 for dark in [False,True]:
  for scale in [1,1.5]:
   for dpr in [1,2]:
    context=('dark' if dark else 'light')+'-text'+str(scale)+'-dpr'+str(dpr)
    args=['env','QT_QPA_PLATFORM=offscreen','QT_QUICK_BACKEND=software','QT_SCALE_FACTOR='+str(dpr),'/work/build/linux/samples/AvelinoCatalog/AvelinoCatalog','--fixture','reference-case','--case','button-group','--case-definitions','/work/evidence/reference-proposals/desktop-20261012/fixtures.json','--text-scale',str(scale),'--capture','/work/artifacts/'+context+'.png']
    if dark:args.append('--dark')
    run('legacy-catalog-'+context,compile+args)
 run('install',compile+['cmake','--install','/work/build/linux','--prefix','/package/install'])
 assert sha(PACKAGE/'install/lib/qml/Avelino/BleeckerButtonGroup.qml')==sha(ROOT/'src/Avelino/BleeckerButtonGroup.qml')
 clone_tree(ROOT/'tests/consumer',PACKAGE/'consumer')
 clone_tree(BASE/'button-group-compiled-v5/output/package/consumer-build',PACKAGE/'consumer-build')
 package=DOCKER+['run','--init','--rm','--ulimit','core=0','-v',str(PACKAGE)+':/package','-w','/package',IMAGE]
 run('fresh-consumer-configure',package+['cmake','-S','consumer','-B','consumer-build','-G','Ninja','-DCMAKE_PREFIX_PATH=/package/install;/opt/qt'])
 run('fresh-consumer-build',package+['cmake','--build','consumer-build','--parallel','2'])
 assert all(sha(ROOT/n)==h for n,h in frozen.items())
 write('result.json',dict(exitCode=0,completeFreshBuild=False,coreTestsPassed=True,fullCoreProducer="button-group-compiled-v3",fullCoreRepeated=False,legacyCatalogContexts=8,freshConsumerBuild=False,consumerBuildCacheReused=True,freshConsumerProducer="button-group-compiled-v5",sourceInputsUnchanged=True,accepted=False,fullMirrorAccepted=False))
 write('phase.json',dict(phase='complete',finishedAt=time.time()))
except BaseException as e:
 write('result.json',dict(exitCode=1,error=repr(e),accepted=False,fullMirrorAccepted=False));raise
