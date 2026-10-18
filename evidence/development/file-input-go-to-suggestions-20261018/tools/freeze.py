"""Freeze suggestion-selection sources and raw failed/final Linux probes."""
from pathlib import Path
import gzip,hashlib,json,shutil,stat

ROOT=Path.cwd();ART=ROOT/'artifacts/resumed-avelino-20261016'
DEST=ROOT/'evidence/development/file-input-go-to-suggestions-20261018'
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
for number in (62,63,64):
    producer=ART/f'file-input-qt-v{number}'
    inputs=json.loads((producer/'inputs.json').read_text())
    files={}
    for name,digest in inputs['files'].items():
        path=producer/'source'/name;assert sha(path.read_bytes())==digest
        if number==64:assert sha((ROOT/name).read_bytes())==digest,name
        files[name]=store(path)
    assert len(files)==571
    sources[producer.name]=dict(files=files,baseGit=inputs['baseGit'])
    for path in sorted(producer.iterdir()):
        if path.is_file():records['producers/'+producer.name+'/'+path.name]=store(path)
    for path in sorted((producer/'ui-output').rglob('*')):
        if path.is_file():copy(path,'producers/'+producer.name+'/'+str(path.relative_to(producer)))
write('source-specs.json',sources)
package=ART/'file-input-go-to-package-v5';display=ART/'file-input-go-to-display-v5'
assert json.loads((package/'result.json').read_text())['exitCode']==0
assert json.loads((display/'result.json').read_text())['exitCode']==0
runtime={str(path.relative_to(package/'runtime')):store(path)for path in sorted((package/'runtime').rglob('*'))if path.is_file()and 'output'not in path.relative_to(package/'runtime').parts and path.name!='environment.json'}
write('runtime-spec.json',runtime);copy(package/'runtime/environment.json','runtime-environment.json')
for prefix,directory in [('package',package),('display',display),('provisional-package',ART/'file-input-go-to-package-v4')]:
    for path in sorted(directory.iterdir()):
        if path.is_file():records[prefix+'/'+path.name]=store(path)
    if prefix=='display':
        for path in sorted((directory/'output').rglob('*')):
            if path.is_file():copy(path,'display/'+str(path.relative_to(directory)))
for path in sorted((package/'runtime/output').iterdir()):
    if path.is_file():copy(path,'captures/'+path.name)
stability={};prior=ROOT/'evidence/development/file-input-go-to-editing-20261018/captures'
for path in sorted((DEST/'captures').glob('*.json')):
    current=json.loads(path.read_text());previous=json.loads((prior/path.name).read_text())
    assert current['closed']==previous['closed']and current['sizing']==previous['sizing']
    images={}
    for row in current['closed']:
        name=path.stem+'-'+row['configuration']['id']+'.png'
        assert (DEST/'captures'/name).read_bytes()==(prior/name).read_bytes(),name
        images[name]=sha((DEST/'captures'/name).read_bytes())
    stability[path.name]=dict(prior=str((prior/path.name).relative_to(ROOT)),images=images)
assert sum(len(row['images'])for row in stability.values())==256
write('closed-stability.json',stability)
for number in (11,12,13,14):
    directory=ART/f'file-input-go-to-reader-v{number}'
    assert json.loads((directory/'session-result.json').read_text())['containerExit']=='0'
    for path in sorted(directory.rglob('*')):
        relative=path.relative_to(directory)
        if not path.is_file()or relative.parts[0]in ('install','config')or '__pycache__'in relative.parts or path.suffix=='.pyc':continue
        name='readers/'+directory.name+'/'+str(relative)
        if relative.parts[0]=='operator-controls-v1'and path.suffix in ('.json','.png'):copy(path,name)
        else:records[name]=store(path)
write('records-spec.json',records)
copy(ART/'go-to-reader-control-v1.py','tools/reader-control-record.py')
copy(ART/'validate-go-to-suggestion-readers-v1.py','tools/validate-readers-record.py')
copy(Path(__file__),'tools/freeze.py')
script=(ROOT/'evidence/development/file-input-go-to-editing-20261018/tools/reconstruct.py').read_text()
script=script.replace('choices=[61], default=61','choices=[62, 63, 64], default=64')
(DEST/'tools/reconstruct.py').write_text(script)
write('validation.json',dict(accepted=False,producer='file-input-qt-v64',sourceFiles=571,sourceAttempts=[62,63,64],reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',desktopCandidateCoverage=[75,80],acceptedDesktopEntries=0,expectedImagesChanged=False,tolerance='none',approvedExceptions=[],focusedQtTargets=8,finalFullQtSuiteRerun=False,packageContexts=8,displayProfiles=8,closedImagesUnchanged=256,readerAttempts=[11,12,13,14],finalReaderAttempts=[13,14],finalReaderPhases=21,selectionEventTransport='verified in measured native-arrow windows',assistiveSingleSelection='verified',readerSpeechCommands='verified before Return in raw byte windows',speechPolicyChanged=False,diagnosticLogging='Original Orca debug.println flush after actual speech and backend messages',nativeHierarchy='pending',nativeReaderComparison='pending',nativeTiming='pending',speechEngineAudioVerification='pending',completeFileChooser='pending',physicalInput=False,physicalDisplay=False,physicalListening=False,independentMachine='pending'))
print('Frozen 3 x 571 source files;',len(runtime),'runtime files;',len(records),'raw records; member seal follows portable replay')
