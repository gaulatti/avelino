from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];steps=[]
for name in ['scripts/check-installed-catalog.sh','scripts/check-display-sessions.sh','.github/workflows/linux.yml']:
 source=p/'before'/name;source.parent.mkdir(parents=True,exist_ok=True);source.write_bytes(subprocess.check_output(['git','show','HEAD:'+name],cwd=r))
 current=p/'after'/name;current.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/name,current)
def run(name,cmd,expected=0):
 start=time.monotonic()
 with(p/(name+'.log')).open('wb')as out:result=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=cmd,exitCode=result.returncode,expectedExitCode=expected,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True);assert result.returncode==expected,name
run('shell-syntax',['bash','-n',str(r/'scripts/check-installed-catalog.sh'),str(r/'scripts/check-display-sessions.sh')])
source=r/'evidence/development/file-input-go-to-suggestions-20261018/display/output'
for state in ['before','after']:
 block=re.findall(r"<<'PY'\n(.*?)\nPY",(p/state/'scripts/check-display-sessions.sh').read_text(),re.S)[1];(p/(state+'-validate.py')).write_text(block+'\n')
 output=p/state/'display';output.mkdir()
 for path in source.iterdir():
  if path.is_file():shutil.copy2(path,output/path.name)
 for path in sorted(output.glob('file-input-*.json')):
  prefix=str(path.with_suffix(''));fixture,protocol,backend,configuration=path.stem.rsplit('-',3)
  run(state+'-'+path.stem,['python3',str(p/(state+'-validate.py')),prefix,protocol,backend,configuration,fixture],1 if state=='before'else 0)
image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3';runtime=p.parent/'hero-carousel-portable-v1/restore/runtime'
run('installed-catalog',['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(runtime)+':/consumer-check','-v',str(p)+':/ci-proof','-w','/consumer-check',image,'bash','/ci-proof/after/scripts/check-installed-catalog.sh','/ci-proof/catalog-evidence'])
record=json.loads((p/'catalog-evidence/catalog-results.json').read_text());assert len(record['captures'])==159
# Exercise root-created private evidence as an unprivileged upload reader.
probe="from pathlib import Path; import json,os,subprocess; p=Path('/ci-proof/permissions/artifacts/linux/app-tabs-raster/private'); p.mkdir(parents=True); p.chmod(0o700); f=p/'report.json'; f.write_text('synthetic evidence'); f.chmod(0o600); cmd=['runuser','-u','nobody','--','python3','-c',\"from pathlib import Path; assert Path('/ci-proof/permissions/artifacts/linux/app-tabs-raster/private/report.json').read_text()=='synthetic evidence'\"]; before=subprocess.run(cmd,capture_output=True); assert before.returncode!=0; subprocess.run(['chmod','-R','a+rX','--','/ci-proof/permissions/artifacts/linux'],check=True); after=subprocess.run(cmd,capture_output=True); assert after.returncode==0; assert f.read_text()=='synthetic evidence'; Path('/ci-proof/permissions/result.json').write_text(json.dumps(dict(beforeExit=before.returncode,afterExit=after.returncode,bytesUnchanged=True)))"
run('artifact-permissions',['docker','--context','colima-avelino-verify','run','--rm','-v',str(p)+':/ci-proof',image,'python3','-c',probe])
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,baselineDisplayFailures=8,fixedDisplayProfiles=8,catalogCaptures=159,unprivilegedArtifactRead='passed',applicationSourcesChanged=False,fullRemoteCi='pending'),indent=2)+'\n')
