"""Freeze the owned path-editing checkpoint, including before/after raw probes."""
from pathlib import Path
import gzip,hashlib,json,shutil,stat,sys
ROOT=Path.cwd();ART=ROOT/'artifacts/resumed-avelino-20261016'
DEST=ROOT/'evidence/development/file-input-go-to-editing-20261018'
producer=ART/sys.argv[1]
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
inputs=json.loads((producer/'inputs.json').read_text());assert json.loads((producer/'result.json').read_text())['exitCode']==0
sources={}
for name,digest in inputs['files'].items():
 p=producer/'source'/name;assert sha(p.read_bytes())==digest
 sources[name]=store(p)
write('source-specs.json',{producer.name:dict(files=sources,baseGit=inputs['baseGit'])})
package=ART/'file-input-go-to-package-v3';display=ART/'file-input-go-to-display-v3'
assert json.loads((package/'result.json').read_text())['exitCode']==0
assert json.loads((display/'result.json').read_text())['exitCode']==0
runtime={str(p.relative_to(package/'runtime')):store(p)for p in sorted((package/'runtime').rglob('*'))if p.is_file()and 'output'not in p.relative_to(package/'runtime').parts and p.name!='environment.json'}
write('runtime-spec.json',runtime);copy(package/'runtime/environment.json','runtime-environment.json')
records={}
for prefix,directory in [('producer',producer),('package',package),('display',display)]:
 for p in sorted(directory.iterdir()):
  if p.is_file():records[prefix+'/'+p.name]=store(p)
 for sub in ['ui-output','output']:
  if(directory/sub).exists():
   for p in sorted((directory/sub).rglob('*')):
    if p.is_file():copy(p,prefix+'/'+str(p.relative_to(directory)))
for p in sorted((package/'runtime/output').iterdir()):
 if p.is_file():copy(p,'captures/'+p.name)
stability={}
prior=ROOT/'evidence/development/file-input-go-to-20261018/captures'
for p in sorted((DEST/'captures').glob('*.json')):
 current=json.loads(p.read_text());previous=json.loads((prior/p.name).read_text())
 assert current['closed']==previous['closed'] and current['sizing']==previous['sizing']
 images={}
 for row in current['closed']:
  name=p.stem+'-'+row['configuration']['id']+'.png'
  assert (DEST/'captures'/name).read_bytes()==(prior/name).read_bytes(),name
  images[name]=sha((DEST/'captures'/name).read_bytes())
 stability[p.name]=dict(prior=str((prior/p.name).relative_to(ROOT)),images=images)
assert sum(len(v['images'])for v in stability.values())==256
write('closed-stability.json',stability)
# Keep all previous raw failures/limitations. Their source60 package is preserved
# by the preceding committed GoTo capsule; each input manifest names exact hashes.
for number in range(1,11):
 directory=ART/f'file-input-go-to-reader-v{number}'
 assert json.loads((directory/'session-result.json').read_text())['containerExit']=='0'
 for p in sorted(directory.rglob('*')):
  relative=p.relative_to(directory)
  if not p.is_file()or relative.parts[0]in ['install','config']or '__pycache__'in relative.parts or p.suffix=='.pyc':continue
  name='readers/'+directory.name+'/'+str(relative)
  if relative.parts[0]=='operator-controls-v1'and p.suffix in ['.json','.png']:copy(p,name)
  else:records[name]=store(p)
write('records-spec.json',records)
copy(ART/'go-to-reader-control-v1.py','tools/reader-control-record.py')
copy(ART/'validate-go-to-editing-readers-v1.py','tools/validate-readers-record.py')
copy(ART/'prepare-go-to-reader-editing-v1.py','tools/prepare-readers-record.py')
copy(Path(__file__),'tools/freeze.py')
s=(ROOT/'evidence/development/file-input-go-to-20261018/tools/reconstruct.py').read_text()
s=s.replace('choices=range(55, 61), default=60','choices=['+sys.argv[1].split('-v')[-1]+'], default='+sys.argv[1].split('-v')[-1])
s=s.replace("parser.add_argument('--runtime-only', action='store_true')","parser.add_argument('--runtime-only', action='store_true')\n    parser.add_argument('--records', action='store_true')")
s=s.replace("(args.destination / 'runtime/output').mkdir()","if args.records:\n        restore(json.loads((DIRECTORY / 'records-spec.json').read_text()), args.destination / 'records')\n    (args.destination / 'runtime/output').mkdir()")
(DEST/'tools/reconstruct.py').write_text(s)
write('validation.json',dict(accepted=False,producer=producer.name,sourceFiles=len(sources),reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',desktopCandidateCoverage=[75,80],acceptedDesktopEntries=0,expectedImagesChanged=False,tolerance='none',approvedExceptions=[],focusedQtTargets=8,finalFullQtSuiteRerun=False,packageContexts=8,displayProfiles=8,closedImagesUnchanged=256,directAtSpiTextEditing='verified in recorded X11 and Wayland probes',nativeHierarchy='pending',nativeReaderComparison='pending',completeFileChooser='pending',physicalInput=False,physicalDisplay=False,physicalListening=False,independentMachine='pending'))
# README and portable replay receipts are added before the final member seal.
print('Frozen',len(sources),'source files;',len(runtime),'runtime files;',len(records),'raw records')
