from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
r=Path.cwd();p=r/'artifacts/resumed-avelino-20261016/date-range-catalog-repeat-v1';assert not p.exists();p.mkdir();old=subprocess.check_output(['git','show','HEAD:scripts/check-linux.sh'],text=True);new=(r/'scripts/check-linux.sh').read_text();needle='cp -R "$stage/date-range-catalog-evidence" artifacts/linux/date-range-catalog-installed';assert old.count(needle)==new.count(needle)==1
before=needle;after=new[new.index('# Keep each earlier date catalog intact'):new.index(needle)+len(needle)]
(p/'before-check-linux.sh').write_text(old);(p/'after-check-linux.sh').write_text(new);(p/'before-block.sh').write_text(before+'\n');(p/'after-block.sh').write_text(after+'\n')
source=r/'artifacts/resumed-avelino-20261016/date-range-catalog-v1/output';assert json.loads((source/'result.json').read_text())['installedCatalogStartup']=='passed'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
files=lambda root:{str(f.relative_to(root)):sha(f)for f in root.rglob('*')if f.is_file()}
steps=[]
for mode,block in [('before',before),('after',after)]:
 work=p/mode;work.mkdir();stage=work/'stage';stage.mkdir();incoming=stage/'date-range-catalog-evidence';shutil.copytree(source,incoming);current=work/'artifacts/linux/date-range-catalog-installed';current.parent.mkdir(parents=True);shutil.copytree(source,current);(current/'prior-only.txt').write_text('prior generated evidence\n');prior=files(current)
 for iteration in range(1,3 if mode=='after'else 2):
  (incoming/'generation.txt').write_text(str(iteration)+'\n');expected=files(incoming);start=time.monotonic();result=subprocess.run(['bash','-c',block],cwd=work,env=dict(os.environ,stage=str(stage)),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(p/f'{mode}-{iteration}.log').write_text(result.stdout);assert result.returncode==0
  if mode=='before':assert(current/'date-range-catalog-evidence').is_dir()and(current/'prior-only.txt').exists();correct=False
  else:
   assert files(current)==expected
   archives=sorted((work/'artifacts/linux').glob('date-range-catalog-previous.*'));assert len(archives)==iteration
   matches=[folder for folder in archives if files(folder/'catalog-installed')==prior];assert len(matches)==1
   assert not matches[0].is_relative_to(stage)
   correct=True;prior=expected
  steps.append(dict(mode=mode,iteration=iteration,exitCode=result.returncode,correctCurrentTree=correct,seconds=time.monotonic()-start))
assert len(steps)==3
(p/'result.json').write_text(json.dumps(dict(accepted=False,beforeNestedOutputReproduced=True,afterFreshTree=True,repeatedGenerations=2,priorGenerationsPreservedOutsideTemporaryStage=True,imageBytesChanged=False,steps=steps),indent=2)+'\n');print('Repeated date catalog: nesting reproduced; both fresh generations correct; both earlier trees preserved byte-for-byte outside the temporary stage')
