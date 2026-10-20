from pathlib import Path
import hashlib,json,subprocess,time
p=Path(__file__).resolve().parent;root=p.parents[2];seed=p.parent/'qt-rectangle-installer-v1';image=json.loads((seed/'runtime-image.json').read_text())['imageId'];rows=[]
assert hashlib.sha256((root/'scripts/check-linux.sh').read_bytes()).hexdigest()==json.loads((p/'inputs.json').read_text())['driverSha256']
for name in ['valid','missing-stage','broken-chain','wrong-header-record','stale-header','stale-library']:
 out=p/name;out.mkdir();(out/'artifacts/linux').mkdir(parents=True)
 sdk='sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3'if name=='missing-stage'else image
 command=['docker','--context','colima-avelino-verify','run','--rm','-v',str(root)+':/work:ro','-v',str(out/'artifacts')+':/work/artifacts','-v',str(p)+':/probe:ro','-v',str(seed)+':/seed:ro','-w','/work',sdk,'python3','/probe/case.py',name]
 start=time.monotonic()
 with(out/'run.log').open('x')as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
 expected=0 if name=='valid'else 1
 rows.append(dict(case=name,imageId=sdk,command=command,exitCode=r.returncode,expectedExitCode=expected,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(name,r.returncode,flush=True);assert r.returncode==expected,name
 if name=='valid':
  env=json.loads((out/'artifacts/linux/environment.json').read_text());stages=env['qtSoftwareRendererStages']
  assert len(stages)==2 and stages[0]['installedLibrarySha256']==stages[1]['originalLibrarySha256']
  assert stages[1]['installedLibrarySha256']==env['qtQuickSha256']
 else:
  log=(out/'run.log').read_text();assert ('FileNotFoundError'if name=='missing-stage'else'AssertionError')in log
  assert not(out/'artifacts/linux/environment.json').exists()
result=dict(exitCode=0,cases=len(rows),validSdkAccepted=True,invalidSdkConfigurationsRejected=5,oldSdkCompatibilityFallback=False,applicationOrGraphicsTestsRun=False,accepted=False)
(p/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
