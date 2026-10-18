from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent;runtime=p.parent/'date-range-package-v2/runtime'
assert json.loads((p.parent/'date-range-package-v2/result.json').read_text())['exitCode']==0
steps=[]
for name,args in [('main',[]),('controls',['--controls']),('hero-carousel',['--hero-carousel','--hero-carousel-observe'])]:
 command=['docker','--context','colima-avelino-verify','run','--rm','-v',str(runtime)+':/regression-check','-w','/regression-check','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3','./consumer-build/InstalledConsumer']+args
 start=time.monotonic()
 with(p/(name+'.log')).open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,consumerSha256=hashlib.sha256((runtime/'consumer-build/InstalledConsumer').read_bytes()).hexdigest(),runtimeMount='/regression-check',buildMountAbsent='/consumer-check',sourceMountAbsent='/work'),indent=2)+'\n')
