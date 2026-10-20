from pathlib import Path
import json, subprocess, time
p=Path(__file__).resolve().parent
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(p)+':/consumer-check','-w','/consumer-check',
      '--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','XDG_RUNTIME_DIR=/tmp/avelino-error-package']
image='avelino-toolchain:recovered-20261017-qt6.8.3';steps=[]
for dark in [False,True]:
    for scale in [1,1.5]:
        for dpr in [1,2]:
            name=f'{"dark" if dark else "light"}-text{scale:g}-dpr{dpr}'
            command=base+['--env',f'QT_SCALE_FACTOR={dpr}',image,'python3','-c',
                "from pathlib import Path; import os; assert not Path('/work/src/Avelino').exists(); assert not Path('/consumer-check/consumer').exists(); assert not Path('/consumer-check/src').exists(); os.execv('./consumer-build/InstalledConsumer',['./consumer-build/InstalledConsumer','--file-input','--file-input-observe','--text-scale',"+repr(str(scale))+",'--file-input-report','/consumer-check/output/"+name+"']"+("+['--dark']"if dark else "")+")"]
            start=time.monotonic()
            with(p/(name+'.log')).open('wb')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
            steps.append(dict(name=name,command=command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n')
            print(name,result.returncode,flush=True)
            if result.returncode:raise SystemExit(result.returncode)
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,contexts=8,consumerSourceAbsent=True,nativeAcceptance='pending'),indent=2)+'\n')
