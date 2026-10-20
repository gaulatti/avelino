from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent;b=p.parent;r=p.parents[2]
original=json.loads((b/'navigation-cjk-ci-v1/metric-probe-v2-command.json').read_text())['command']
assert '--ulimit'in original and 'core=0'in original
steps=[]
for dpr in [1,2]:
 command=list(original);command[command.index('-input')+1]='/work/'+str((p/'tst_metric_matrix.qml').relative_to(r));index=command.index('avelino-toolchain:recovered-weston13-cjk-v1-20261018-qt6.8.3');command[index:index]=['-e','QT_SCALE_FACTOR='+str(dpr)]
 start=time.monotonic()
 with(p/f'dpr{dpr}.log').open('w')as log:result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(dpr=dpr,command=command,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print('matrix DPR',dpr,result.returncode,flush=True)
(p/'result.json').write_text(json.dumps(dict(accepted=False,steps=steps,productChanged=False,scope='Diagnostic font flags on caller objects; native expected observations unchanged'),indent=2)+'\n')
