from pathlib import Path
import subprocess,json,time,hashlib,sys
P=Path(__file__).resolve().parent
ROOT=Path('/Users/gaulatti/source/gaulatti/avelino')
OUT=ROOT/'artifacts/resumed-avelino-20261016/admin-source-colour-compiled-v1/output'
IMAGE='sha256:40ab3fe5897ee697937db7429956381f67d4f9d9c7acb98130ebfddaa751e3f7'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
files=sorted([ROOT/'CMakeLists.txt',ROOT/'CMakePresets.json']+[p for folder in ['src','samples','assets','tokens','tests','scripts','cmake','tools','evidence/geometry'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts])
inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert head==sys.argv[1]
assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT)
write('inputs.json',dict(sourceRevision=head,sourceFiles=inputs,imageId=IMAGE,buildReuse='APFS clone of divider compiled build; original build and package preserved unchanged',accepted=False))
base=['docker','--context','colima-avelino-verify','run','--init','--rm','--ulimit','core=0','-v',str(ROOT)+':/work:ro','-v',str(OUT/'build')+':/work/build','-v',str(OUT/'artifacts')+':/work/artifacts','-v',str(OUT/'package')+':/package','-w','/work','-e','QML_IMPORT_PATH=/work/build/linux/qml',IMAGE]
commands=[]
def run(name,args):
 write('phase.json',dict(phase=name,startedAt=time.time()));started=time.monotonic()
 with (P/(name+'.log')).open('x') as log:r=subprocess.run(base+args,stdout=log,stderr=subprocess.STDOUT)
 commands.append(dict(name=name,command=base+args,exitCode=r.returncode,seconds=time.monotonic()-started));write('commands.json',commands)
 print(name,r.returncode,flush=True);assert r.returncode==0,(name,r.returncode)
try:
 run('configure',['cmake','--preset','linux'])
 run('build',['cmake','--build','--preset','linux','--parallel','2'])
 for dpr in [1,2]:
  for api in ['admin','mobile']:
   run(f'{api}-dpr{dpr}',['env','QT_QPA_PLATFORM=offscreen','QT_QUICK_BACKEND=software','QT_SCALE_FACTOR='+str(dpr),'/work/build/linux/tests/components/AvelinoComponentTests','-input',f'/work/tests/components/tst_{api}_shell.qml','-import','/work/build/linux/qml'])
 run('install',['cmake','--install','/work/build/linux','--prefix','/package/install'])
 run('consumer-configure',['cmake','-S','/work/tests/consumer','-B','/package/consumer-build','-G','Ninja','-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DCMAKE_PREFIX_PATH=/package/install;/opt/qt'])
 run('consumer-build',['cmake','--build','/package/consumer-build','--parallel','2'])
 assert all(sha(ROOT/n)==h for n,h in inputs.items())
 write('result.json',dict(exitCode=0,sourceRevision=head,sourceInputsUnchanged=True,incrementalCoreBuild=True,freshConsumerBuild=True,focusedAdminAndMobileTests=True,installedConsumerExecuted=False,accepted=False))
 write('phase.json',dict(phase='compiled',finishedAt=time.time()))
except BaseException as e:
 write('result.json',dict(exitCode=1,error=repr(e),accepted=False));raise
