from pathlib import Path
import hashlib,json,shutil,subprocess,time
p=Path(__file__).resolve().parent;r=p.parents[2];runtime=p.parent/'hero-carousel-portable-v1/restore/runtime';capsule=r/'evidence/development/hero-carousel-20261018';image='avelino-toolchain:recovered-weston13-v2-20261017-qt6.8.3';steps=[]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
names=['scripts/check-installed.sh','scripts/check-linux.sh','scripts/check-installed-catalog.sh','scripts/check-display-sessions-hero-carousel.sh','.github/workflows/linux.yml']
inputs={name:sha(r/name)for name in names};(p/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
for name in names:shutil.copy2(r/name,p/Path(name).name)
lines=(r/'scripts/check-installed.sh').read_text().splitlines();fragment='\n'.join(['#!/usr/bin/env bash','set -euo pipefail']+[line for line in lines if '--hero-carousel' in line or line.startswith('hero_checks_dir=')])+'\n';assert fragment.count('--hero-carousel')==2
(p/'installed-hero-fragment.sh').write_text(fragment)
def run(name,cmd):
 start=time.monotonic()
 with(p/(name+'.log')).open('wb')as out:result=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,command=cmd,exitCode=result.returncode,seconds=time.monotonic()-start));(p/'commands.json').write_text(json.dumps(steps,indent=2)+'\n');print(name,result.returncode,flush=True);assert result.returncode==0
run('shell-syntax',['bash','-n']+[str(r/name)for name in names if name.endswith('.sh')])
base=['docker','--context','colima-avelino-verify','run','--rm','--ulimit','core=0','-v',str(runtime)+':/consumer-check','-v',str(p)+':/ci-driver','-w','/consumer-check']
startup="from pathlib import Path; import os; assert not Path('/work/src/Avelino').exists(); assert not Path('/consumer-check/consumer').exists(); assert not Path('/consumer-check/consumer-build/CMakeCache.txt').exists(); os.execv('/bin/bash',['bash','/ci-driver/installed-hero-fragment.sh'])"
run('installed-hero-fragment',base+[image,'python3','-c',startup])
folder,=runtime.glob('hero-carousel-installed.*');shutil.copytree(folder,p/'installed-gallery')
for actual in (p/'installed-gallery').iterdir():
 name=actual.name.replace('gallery','gallery-light-text1-dpr1',1);assert actual.read_bytes()==(capsule/'captures'/name).read_bytes(),name
for dark in [False,True]:
 for dpr in [1,2]:
  name=f'catalog-{"dark"if dark else"light"}-dpr{dpr}';args=['/consumer-check/install/bin/AvelinoCatalog','--fixture','hero-carousel','--capture','/ci-driver/'+name+'.png']+(['--dark']if dark else[])
  run(name,base+['--env','LANG=C.UTF-8','--env','QT_QPA_PLATFORM=offscreen','--env','QT_QUICK_BACKEND=software','--env','QT_SCALE_FACTOR='+str(dpr),image]+args)
  expected=capsule/'captures'/f'gallery-{"dark"if dark else"light"}-text1-dpr{dpr}-initial.png';assert(p/(name+'.png')).read_bytes()==expected.read_bytes()
(p/'result.json').write_text(json.dumps(dict(accepted=False,exitCode=0,projectSourcesAbsent=True,scope='Added installed-consumer HeroCarousel commands and four catalog contexts only; full CI pending',installedGalleryFiles=22,catalogContexts=4,allComparedImagesAndGalleryReportIdentical=True),indent=2)+'\n')
