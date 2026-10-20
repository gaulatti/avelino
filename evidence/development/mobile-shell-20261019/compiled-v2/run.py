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
 paths=[ROOT/'CMakeLists.txt']
 for name in ['src','tests','samples','reference']:
  paths.extend(p for p in (ROOT/name).rglob('*') if p.is_file())
 frozen={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}
 write('inputs.json',dict(sourceBase=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sourceFiles=frozen,imageId=IMAGE,completeFreshBuild=False,accepted=False))
 for name in ['src/Avelino/CMakeLists.txt','src/Avelino/proposalrow.h','src/Avelino/shellslot.h','src/Avelino/shellslot.cpp','src/Avelino/BleeckerMobileAppShell.qml','src/Avelino/DesktopSectionPicker.qml']:
  target=P/'implementation-inputs'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 OUTPUT.mkdir();PACKAGE.mkdir()
 write('build-reuse.json',clone_tree(BASE/'mobile-shell-library-v1/output/build',OUTPUT/'build'))
 compile=DOCKER+['run','--init','--rm','--ulimit','core=0','-v',str(ROOT)+':/work:ro','-v',str(OUTPUT/'build')+':/work/build','-v',str(PACKAGE)+':/package','-w','/work','-e','QML_IMPORT_PATH=/work/build/linux/qml',IMAGE]
 run('configure',compile+['cmake','-S','/work','-B','/work/build/linux','-G','Ninja','-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DBUILD_TESTING=ON'])
 run('build',compile+['cmake','--build','/work/build/linux','--parallel','2'])
 for dpr in [1,2]:
  run('mobile-shell-preflight-dpr'+str(dpr),compile+['env','QT_QPA_PLATFORM=offscreen','QT_QUICK_BACKEND=software','QT_SCALE_FACTOR='+str(dpr),'/work/build/linux/tests/components/AvelinoComponentTests','-input','/work/tests/components/tst_mobile_shell.qml','-import','/work/build/linux/qml'])
 run('core-tests',compile+['ctest','--test-dir','/work/build/linux','--output-on-failure'])
 run('install',compile+['cmake','--install','/work/build/linux','--prefix','/package/install'])
 clone_tree(ROOT/'tests/consumer',PACKAGE/'consumer')
 package=DOCKER+['run','--init','--rm','--ulimit','core=0','-v',str(PACKAGE)+':/package','-w','/package',IMAGE]
 run('fresh-consumer-configure',package+['cmake','-S','consumer','-B','consumer-build','-G','Ninja','-DCMAKE_PREFIX_PATH=/package/install;/opt/qt'])
 run('fresh-consumer-build',package+['cmake','--build','consumer-build','--parallel','2'])
 assert all(sha(ROOT/n)==h for n,h in frozen.items())
 write('result.json',dict(exitCode=0,completeFreshBuild=False,fullCoreTestsPassed=True,freshConsumerBuild=True,sourceInputsUnchanged=True,accepted=False,fullMirrorAccepted=False))
 write('phase.json',dict(phase='complete',finishedAt=time.time()))
except BaseException as e:
 write('result.json',dict(exitCode=1,error=repr(e),accepted=False));raise
