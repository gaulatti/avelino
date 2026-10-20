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
 OUTPUT.mkdir();PACKAGE.mkdir()
 write('inputs.json',dict(sourceBase=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sourceFiles={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'src').rglob('*')) if p.is_file()},imageId=IMAGE,completeFreshBuild=False,accepted=False))
 write('build-reuse.json',clone_tree(BASE/'button-group-compiled-v6/output/build',OUTPUT/'build'))
 compile=DOCKER+['run','--init','--rm','--ulimit','core=0','-v',str(ROOT)+':/work:ro','-v',str(OUTPUT/'build')+':/work/build','-v',str(PACKAGE)+':/package','-w','/work','-e','QML_IMPORT_PATH=/work/build/linux/qml',IMAGE]
 run('configure',compile+['cmake','-S','/work','-B','/work/build/linux','-G','Ninja','-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DBUILD_TESTING=ON'])
 run('library-build',compile+['cmake','--build','/work/build/linux','--target','Avelino','--parallel','2'])
 write('result.json',dict(exitCode=0,libraryCompiled=True,allCoreTestsRun=False,packageConsumerVerified=False,accepted=False))
except BaseException as e:
 write('result.json',dict(exitCode=1,error=repr(e),accepted=False));raise
