from pathlib import Path
import hashlib,json,shutil,subprocess,time
out=Path(__file__).resolve().parent;root=out.parents[2];producer=out.parent/'date-range-qt-v18';assert json.loads((producer/'result.json').read_text())['exitCode']==0
shutil.copytree(producer/'install',out/'install');image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3';steps=[]
for name,args in [('configure',['cmake','-S','source','-B','build','-G','Ninja','-DCMAKE_PREFIX_PATH=/opt/qt']),('build',['cmake','--build','build','--parallel','2'])]:
 cmd=['docker','--context','colima-avelino-verify','run','--rm','-v',str(out)+':/measure-check','-w','/measure-check',image]+args;start=time.monotonic()
 with(out/(name+'.log')).open('w')as log:result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=cmd,exitCode=result.returncode,seconds=time.monotonic()-start));(out/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True)
 if result.returncode:raise SystemExit(result.returncode)
(out/'inputs.json').write_text(json.dumps(dict(producer=producer.name,sourceFiles={str(p.relative_to(out/'source')):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((out/'source').glob('*'))if p.is_file()}),indent=2)+'\n')
