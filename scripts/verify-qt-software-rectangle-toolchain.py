#!/usr/bin/env python3
"""Audit the integrated rectangle-stage evidence without accepting mirror parity."""
import hashlib
import io
import importlib.util
import itertools
import json
from pathlib import Path
import re
import subprocess
import tempfile
from PIL import Image,ImageChops

ROOT=Path(__file__).resolve().parents[1]
CAPSULE=ROOT/'evidence/development/qt-rectangle-toolchain-20261020'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((CAPSULE/n).read_text())
def difference(a,b):
 with Image.open(a)as x,Image.open(b)as y:
  x=x.convert('RGBA');y=y.convert('RGBA');assert x.size==y.size
  d=ImageChops.difference(x,y);m=d.getchannel('R')
  for c in ['G','B','A']:m=ImageChops.lighter(m,d.getchannel(c))
  return x.width*x.height-m.histogram()[0]
def verify():
 manifest=read('files.json');assert set(manifest)=={str(p.relative_to(CAPSULE))for p in CAPSULE.rglob('*')if p.is_file()and p!=CAPSULE/'files.json'}
 for n,r in manifest.items():
  assert not Path(n).is_absolute()and'..'not in Path(n).parts
  assert digest(CAPSULE/n)==r['sha256']and(CAPSULE/n).stat().st_size==r['bytes'],n
 core=read('core/result.json');assert core['exitCode']==0 and core['completeFreshBuild']and core['fullCoreTestsPassed']and core['freshConsumerBuild']and core['sourceInputsUnchanged']
 assert '100% tests passed, 0 tests failed out of 55'in(CAPSULE/'core/core-tests.log').read_text()
 assert len(read('core/commands.json'))==8 and all(r['exitCode']==0 for r in read('core/commands.json'))
 frozen=read('core/inputs.json');assert frozen['sourceBase']=='281b39fec537bbb0e6758c252f5620a3cc1f9e9b'and len(frozen['sourceFiles'])==954
 names=list(frozen['sourceFiles']);payload=''.join(frozen['sourceBase']+':'+n+'\n'for n in names).encode()
 stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=payload,cwd=ROOT))
 for n in names:
  header=stream.readline().split();assert len(header)==3 and header[1]==b'blob'
  data=stream.read(int(header[2]));assert stream.read(1)==b'\n'and hashlib.sha256(data).hexdigest()==frozen['sourceFiles'][n],n
 assert not stream.read()
 assert read('controls-v1/result.json')['exitCode']==1
 assert len(list((CAPSULE/'controls-v1/baseline/captures/xcb-dpr1').glob('frame-*.png')))==90
 assert not(CAPSULE/'controls-v1/baseline/captures/xcb-dpr1/result.json').exists()
 assert read('controls-v2/attempt-note.json')['rendererChanged']is False
 for n in ['qt-software-rectangle.cpp','check-qt-software-rectangle.sh']:
  assert(CAPSULE/'controls-v2'/n).read_bytes()==(ROOT/'tools'/n).read_bytes()
 total=plain=legacy=old_mismatches=0
 for platform,dpr in itertools.product(['xcb','wayland'],[1,2]):
  label=f'{platform}-dpr{dpr}';a=CAPSULE/'controls-v2/baseline/captures'/label;b=CAPSULE/'controls-v2/patched/captures'/label
  old=json.loads((a/'result.json').read_text());new=json.loads((b/'result.json').read_text())
  for r in [old,new]:
   assert r['qt']=='6.8.3'and r['platform']==platform and r['dpr']==dpr and r['graphicsApi']==1
   assert r['stabilityFailures']==r['alphaFailures']==0 and len(r['frames'])==120
   assert {(f['kind'],f['shift'],f['height'])for f in r['frames']}==set(itertools.product(range(4),[0,.25,.5,.75,1],[17.125,17.25,17.5,17.75,18,18.125]))
  assert old['floatingGeometryFailures']>0 and new['floatingGeometryFailures']==0
  for x,y in zip(old['frames'],new['frames'],strict=True):
   assert all(x[k]==y[k]for k in ['index','kind','shift','height','actualRect','radius','borderWidth','gradientActive'])
   for folder,row in [(a,x),(b,y)]:
    assert digest(folder/row['capture'])==row['sha256']and row['stable']and row['paintedPixels']>0 and row['nonOpaquePixels']==0
    assert row['actualRect']==[7+row['shift'],8.5,30.5,row['height']]
    assert row['radius']==(4.5 if row['kind']==2 else 0)and row['borderWidth']==(1.25 if row['kind']==1 else 0)and row['gradientActive']==(row['kind']==3)
   if x['kind']==0:
    assert(a/x['reference']).read_bytes()==(b/y['reference']).read_bytes()
    assert digest(a/x['reference'])==x['referenceSha256']and digest(b/y['reference'])==y['referenceSha256']
    before,after=difference(a/x['capture'],a/x['reference']),difference(b/y['capture'],b/y['reference'])
    assert before==x['changedPixels']and after==y['changedPixels']==0
    old_mismatches+=before>0;plain+=1
   else:
    assert(a/x['capture']).read_bytes()==(b/y['capture']).read_bytes();legacy+=1
   total+=1
 assert(total,plain,legacy,old_mismatches)==(480,120,360,114)
 factory=read('factory/result.json');assert factory['exitCode']==0 and factory['canonicalRectangleRecipeExecuted']and factory['opacityStageSeededFromProduct']and factory['sourceCacheReused']
 assert read('factory/bootstrap-result.json')['exactProductSdkSeed']and read('factory/bootstrap-result.json')['sdkEntries']==9236
 before=read('factory/rectangle-stage/sdk-before.json');after=read('factory/rectangle-stage/sdk-after.json')
 assert before==read('factory/product-sdk-files.json')and before.keys()==after.keys()and len(after)==9236
 prior=ROOT/'evidence/development/qt-fractional-rectangle-20261019/sdk-v2/immutable-sdk-files.json'
 assert after==json.loads(prior.read_text())
 changed=[n for n in before if before[n]!=after[n]]
 assert changed==['include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h','lib/libQt6Quick.so.6.8.3']
 alpha=read('factory/previous-stage/provenance.json');rectangle=read('factory/rectangle-stage/provenance.json')
 assert rectangle['previousStage']=='qt-software-opacity'and rectangle['originalLibrarySha256']==alpha['installedLibrarySha256']
 assert rectangle['installedLibrarySha256']==after[changed[1]]['sha256']and rectangle['installedHeaderSha256']==after[changed[0]]['sha256']
 assert rectangle['patchSha256']==digest(ROOT/'tools/qt-software-rectangle.patch')and rectangle['featuresMatched']==49
 assert rectangle['floatingReferences']==120 and rectangle['legacyByteIdentical']==360 and not rectangle['nativeAcceptance']
 for name,r in read('factory/inputs.json')['recipeFiles'].items():assert digest(ROOT/name)==r,name
 assembly=read('factory/runtime-assembly-result.json');assert assembly['exitCode']==0 and assembly['sdkMatchesTestedCandidate']and assembly['chainedProvenance']and assembly['producerSourceAndBuildCacheAbsent']and not assembly['fullDockerfileBuild']
 spec=importlib.util.spec_from_file_location('rectangle_opacity',ROOT/'scripts/verify-qt-software-source-patch.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 with tempfile.TemporaryDirectory()as temporary:
  directory=Path(temporary);(directory/'regression').mkdir()
  (directory/'regression/installed').symlink_to(CAPSULE/'factory/rectangle-stage/opacity-regression',target_is_directory=True)
  module.CAPSULE=directory
  assert module.profiles('installed',{n:0 for n in ['xcb-dpr1','xcb-dpr2','wayland-dpr1','wayland-dpr2']})==(120,12,0)
 preflight=read('driver-preflight/result.json');assert preflight['exitCode']==0 and preflight['cases']==6 and preflight['invalidSdkConfigurationsRejected']==5
 assert digest(ROOT/'scripts/check-linux.sh')==read('driver-preflight/inputs.json')['driverSha256']
 for row in read('driver-preflight/commands.json'):
  assert row['exitCode']==row['expectedExitCode']
  folder=CAPSULE/'driver-preflight'/row['case']
  if row['case']=='valid':
   env=json.loads((folder/'artifacts/linux/environment.json').read_text());assert env['qtQuickSha256']==rectangle['installedLibrarySha256']and len(env['qtSoftwareRendererStages'])==2
  else:assert not(folder/'artifacts/linux/environment.json').exists()
 assert 'cp -R /opt/qt/share/avelino/qt-software-rectangle /evidence/'in(ROOT/'.github/workflows/linux.yml').read_text()
 assert 'install-qt-software-rectangle.sh'in(ROOT/'tools/Dockerfile').read_text()
 result=read('result.json');assert result['accepted']is result['nativeAcceptance']is result['fullMirrorAccepted']is False
 print('Rectangle stage:954 frozen source inputs;55 component groups;fresh consumer;114 geometry failures to zero;360 legacy identities;factory SDK9236 identical to tested candidate;6 preflight cases;full driver and mirror acceptance separate')
if __name__=='__main__':verify()
