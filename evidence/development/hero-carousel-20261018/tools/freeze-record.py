"""Freeze HeroCarousel source attempts, installed runtime and raw diagnostics."""
from pathlib import Path
import gzip,hashlib,json,shutil,stat,sys
ROOT=Path.cwd();ART=ROOT/'artifacts/resumed-avelino-20261016'
FINAL=int(sys.argv[1]);PACKAGE=sys.argv[2];DISPLAY=sys.argv[3]
DEST=ROOT/'evidence/development/hero-carousel-20261018'
assert not DEST.exists();DEST.mkdir(parents=True);(DEST/'blobs').mkdir()
CHUNK=8*1024*1024
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def write(name,value):
 p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
def copy(source,name):
 p=DEST/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,p)
def store(path):
 raw=path.read_bytes();chunks=[]
 for offset in range(0,len(raw),CHUNK):
  part=raw[offset:offset+CHUNK];digest=sha(part);target=DEST/'blobs'/(digest+'.gz')
  if not target.exists():target.write_bytes(gzip.compress(part,compresslevel=6,mtime=0))
  chunks.append(dict(sha256=digest,bytes=len(part)))
 return dict(bytes=len(raw),sha256=sha(raw),mode=stat.S_IMODE(path.stat().st_mode),chunks=chunks)
sources={};records={}
for number in range(1,FINAL+1):
 producer=ART/f'hero-carousel-qt-v{number}';inputs=json.loads((producer/'inputs.json').read_text());files={}
 for name,digest in inputs['files'].items():
  path=producer/'source'/name;assert sha(path.read_bytes())==digest,name
  if number==FINAL:assert sha((ROOT/name).read_bytes())==digest,name
  files[name]=store(path)
 sources[producer.name]=dict(files=files,baseGit=inputs['baseGit'])
 for path in sorted(producer.iterdir()):
  if path.is_file():records['producers/'+producer.name+'/'+path.name]=store(path)
write('source-specs.json',sources)
package=ART/PACKAGE;display=ART/DISPLAY
assert json.loads((package/'result.json').read_text())['exitCode']==0
assert json.loads((display/'result.json').read_text())['exitCode']==0
runtime={str(path.relative_to(package/'runtime')):store(path) for path in sorted((package/'runtime').rglob('*'))if path.is_file()and 'output'not in path.relative_to(package/'runtime').parts and path.name!='environment.json'}
write('runtime-spec.json',runtime);copy(package/'runtime/environment.json','runtime-environment.json')
for prefix,directory in [('package',package),('display',display),('baseline-package',ART/'hero-carousel-package-v1'),('aligned-package',ART/'hero-carousel-package-v2'),('baseline-display',ART/'hero-carousel-display-v1'),('strict-default',ART/'hero-carousel-strict-v2'),('catalog',ART/'hero-carousel-catalog-v2')]:
 for path in sorted(directory.iterdir()):
  if path.is_file():records[prefix+'/'+path.name]=store(path)
 if prefix=='display':
  for path in sorted((directory/'output').rglob('*')):
   if path.is_file():copy(path,'display/'+str(path.relative_to(directory)))
for path in sorted((package/'runtime/output').iterdir()):
 if path.is_file():copy(path,'captures/'+path.name)
for path in sorted((ART/'hero-carousel-package-v1/runtime/output').iterdir()):
 if path.is_file():copy(path,'baseline-captures/'+path.name)
for path in sorted((ART/'hero-carousel-package-v2/runtime/output').iterdir()):
 if path.is_file():copy(path,'aligned-captures/'+path.name)
for path in sorted((ART/'hero-carousel-catalog-v2').glob('gallery.png*')):copy(path,'catalog/'+path.name)
write('records-spec.json',records)
copy(Path(__file__),'tools/freeze-record.py')
copy(ROOT/'scripts/compare-hero-carousel-captures.py','tools/compare-record.py')
copy(ROOT/'scripts/check-display-sessions-hero-carousel.sh','tools/check-display-sessions.sh')
script=(ROOT/'evidence/development/file-input-go-to-suggestions-20261018/tools/reconstruct.py').read_text()
script=script.replace('choices=[62, 63, 64], default=64',f'choices={list(range(1,FINAL+1))}, default={FINAL}')
script=script.replace("'file-input-qt-v'", "'hero-carousel-qt-v'")
(DEST/'tools/reconstruct.py').write_text(script)
write('validation.json',dict(accepted=False,producer=f'hero-carousel-qt-v{FINAL}',sourceCounts={name:len(row['files'])for name,row in sources.items()},sourceAttempts=list(range(1,FINAL+1)),reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',desktopCandidateCoverage=[76,80],acceptedDesktopEntries=0,expectedImagesChanged=False,tolerance='none',approvedExceptions=[],focusedQtTargets=5,finalFullQtSuiteRerun=False,packageContexts=8,galleryContexts=8,displayProfiles=8,strictComparison=json.loads((package/'comparison.json').read_text())['summary'],nativeCompleteGeometry='pending; histories project active frames and preserve raw cached frames',nativeDirectSizing='pending',nativeLazyTiming='pending',nativeGestureTiming='pending',nativeSystemFontMetrics='pending',readerAcceptance='pending',physicalInput=False,physicalDisplay=False,independentMachine='pending'))
print('Frozen',len(sources),'source attempts;',len(runtime),'runtime files;',len(records),'raw records; portable replay and seal still required',flush=True)
