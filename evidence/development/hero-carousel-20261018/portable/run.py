from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];capsule=r/'evidence/development/hero-carousel-20261018';steps=[]
image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3'
image_id=subprocess.check_output(['docker','--context','colima-avelino-verify','image','inspect',image,'--format','{{.Id}}'],text=True).strip();assert image_id=='sha256:2fdc6216ef3446ebd904a1999d3e0c909c7b667e844149ad2830d68d069e77f8'
def run(name,command):
 start=time.monotonic()
 with(p/(name+'.log')).open('wb')as out:result=subprocess.run(command,stdout=out,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True);assert result.returncode==0,name
run('reconstruct',['python3',str(capsule/'tools/reconstruct.py'),str(p/'restore'),'--runtime-only'])
runtime=p/'restore/runtime'
for gallery in [False,True]:
 for dark in [False,True]:
  for scale in [1,1.5]:
   for dpr in [1,2]:
    name=('gallery-'if gallery else'')+f'{"dark"if dark else"light"}-text{scale:g}-dpr{dpr}'
    args=['./consumer-build/InstalledConsumer','--hero-carousel','--hero-carousel-gallery'if gallery else'--hero-carousel-observe','--text-scale',str(scale),'--hero-carousel-report','/consumer-check/output/'+name]+(['--dark']if dark else[])
    startup="from pathlib import Path; import os; assert not Path('/work/src/Avelino').exists(); assert not Path('/consumer-check/consumer').exists(); assert not Path('/consumer-check/source').exists(); assert not Path('/consumer-check/consumer-build/CMakeCache.txt').exists(); os.execv('./consumer-build/InstalledConsumer',"+repr(args)+")"
    cmd=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(runtime)+':/consumer-check','-w','/consumer-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','QT_SCALE_FACTOR='+str(dpr),'--env','XDG_RUNTIME_DIR=/tmp/avelino-navigation',image,'python3','-c',startup]
    run(name,cmd)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
files={}
for path in sorted((capsule/'captures').iterdir()):
 if path.is_file():
  actual=runtime/'output'/path.name;assert actual.read_bytes()==path.read_bytes(),path.name;files[path.name]=sha(actual)
assert len(files)==376
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,contexts=8,galleryContexts=8,projectSourcesAbsent=True,exactOutputFiles=len(files),files=files,image=image,imageId=image_id),indent=2)+'\n');print('Exact portable replay:',len(files),'files; acceptance pending',flush=True)
