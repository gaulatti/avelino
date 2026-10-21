from pathlib import Path
import gzip,hashlib,io,json,subprocess

BASE=Path('/Users/gaulatti/.codex/tmp')
REPO=BASE/'avelino-reference-repair-20261020-v1'
ARTIFACTS=Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016')
CONTROLLER=BASE/'avelino-file-search-compiled-20261020-v24'
CAPSULE=REPO/'evidence/development/file-input-search-accessibility-20261021'
inputs=json.loads((CONTROLLER/'inputs.json').read_text())
source=Path(inputs['snapshot']);package=Path(inputs['output'])/'package'
assert json.loads((CONTROLLER/'validation/ctest/result.json').read_text())['exitCode']==0
assert json.loads((BASE/'avelino-file-search-closed-regression-20261021-v2/result.json').read_text())['byteIdentical']==256
assert json.loads((BASE/'avelino-file-search-portable-20261021-v1/result.json').read_text())['exitCode']==0
CAPSULE.mkdir(exist_ok=False)
records={}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def put(name,raw):
    assert name not in records
    digest=sha(raw);png=raw.startswith(b'\x89PNG\r\n\x1a\n')
    stored=('images/'+digest+'.png') if png else ('blobs/'+digest+'.gz')
    target=CAPSULE/stored;target.parent.mkdir(exist_ok=True)
    if not target.exists():target.write_bytes(raw if png else gzip.compress(raw,mtime=0))
    records[name]={'sha256':digest,'bytes':len(raw),'stored':stored}
def tree(prefix,path):
    for p in sorted(path.rglob('*')):
        if p.is_file():put(prefix+'/'+str(p.relative_to(path)),p.read_bytes())
def write(name,value):
    (CAPSULE/name).write_text(json.dumps(value,indent=2)+'\n')

# Preserve the exact selected source snapshot without copying the whole repository.
# Historical Git supplies unchanged bytes; explicit overrides supply every delta.
names=list(inputs['sourceFiles'])
batch=subprocess.check_output(['git','cat-file','--batch'],cwd=REPO,input=('\n'.join(inputs['parent']+':'+n for n in names)+'\n').encode())
stream=io.BytesIO(batch);overrides=[]
for name in names:
    raw=(source/name).read_bytes();assert sha(raw)==inputs['sourceFiles'][name]
    header=stream.readline().split()
    if len(header)==3:
        assert header[1]==b'blob';prior=stream.read(int(header[2]));assert stream.read(1)==b'\n'
    else:
        assert header[-1]==b'missing';prior=None
    if prior!=raw:
        put('source-overrides/'+name,raw);overrides.append(name)
assert not stream.read()
put('producer/inputs.json',(CONTROLLER/'inputs.json').read_bytes())
for name in ['result.json','commands.json','configure.log','build.log','search-dpr1.log']:
    put('producer/'+name,(CONTROLLER/name).read_bytes())
tree('validation',CONTROLLER/'validation')
tree('consumer-output',package/'search-runtime')
tree('display-output',package/'display-search-v1')
put('display-environment.json',(package/'environment.json').read_bytes())
for number in [16,19,20,22,23]:
    path=BASE/f'avelino-file-search-compiled-20261020-v{number}'
    for name in ['inputs.json','result.json','search-dpr1.log']:
        if (path/name).is_file():put(f'previous-source-{number}/'+name,(path/name).read_bytes())
tree('invalid-loader-deletion-debug',BASE/'avelino-file-search-owner-debug-20261021-v1')
for number in range(1,7):
    tree(f'readers/v{number}',ARTIFACTS/f'file-search-a11y-v{number}')
    tree(f'reader-controllers/v{number}',BASE/f'avelino-file-search-a11y-20261021-v{number}')
comparison=BASE/'avelino-file-search-closed-regression-20261021-v2'
tree('closed-comparison-controller',comparison)
tree('closed-comparison-output',Path(inputs['output'])/'closed-regression')
tree('portable-controller',BASE/'avelino-file-search-portable-20261021-v1')
tree('portable-output',ARTIFACTS/'file-search-portable-v1/proof')
put('portable-controller/run.py',(BASE/'avelino-search-portable-20261021.py').read_bytes())
image='sha256:e2c92a8b5a48fe0215e9dc42ff81d9d454f3497b4ee7d56bed95647f0cee7d21'
command=['docker','--context','colima-avelino-verify','run','--rm',image,'dpkg-query','-W','-f=${Package}\t${Version}\n','orca','python3-pyatspi','at-spi2-core','speech-dispatcher','speech-dispatcher-espeak-ng','libespeak-ng1','libtracker-sparql-3.0-0','tracker-miner-fs']
result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert result.returncode==0,result.stderr
put('reader-image/packages.txt',result.stdout)
put('reader-image/package-command.json',(json.dumps({'command':command,'exitCode':0,'stderr':result.stderr.decode()},indent=2)+'\n').encode())
tree('reader-image/build',BASE/'avelino-file-search-a11y-image-20261021-v1')
write('source-overrides.json',{'baseSourceRevision':inputs['parent'],'selectedFiles':len(names),'overrides':overrides,'sourceUncommittedAtExecution':True})
write('records.json',records)
write('validation.json',{'producer':'file-search-compiled-v24','sourceFiles':len(names),'sourceParent':inputs['parent'],'qt':'6.8.3','operatingSystem':'Ubuntu 24.04','architecture':'arm64','desktopCandidateCoverage':[78,80],'acceptedDesktopEntries':0,'focusedSearchDpr1':'passed','fullCtestGroups':58,'installedConsumer':['available','unavailable','legacy-file-input'],'searchDisplayProfiles':8,'closedImagesByteIdentical':256,'closedFramesAndStatesIdentical':256,'readerProfiles':[{'attempt':5,'protocol':'xcb','backend':'software','scaled':False,'phases':12},{'attempt':6,'protocol':'wayland','backend':'opengl','scaled':True,'phases':12}],'priorAttemptsRetained':True,'invalidManualLoaderDeletionAttempt':22,'nativeReaderComparisonAccepted':False,'speechEngineAudioAccepted':False,'physicalInput':False,'physicalDisplay':False,'independentMachineAccepted':False,'expectedImagesChanged':False,'referenceChanged':False,'tolerancesChanged':False,'accepted':False})
(CAPSULE/'README.md').write_text('''# Indexed search accessibility checkpoint

This is scoped Linux candidate evidence. Desktop coverage remains 78/80
candidates and 0/80 native accepted. References, expected images, tolerances and
approval gates are unchanged.

The exact source24 snapshot contains 4046 selected inputs. `source-overrides.json`
names every change from the recorded Git parent; `records.json` maps the original
bytes to losslessly compressed blobs or raw content-addressed PNGs. The captured
producer inputs and commands retain their original absolute execution paths.
Unchanged selected source bytes remain recoverable from that immutable Git parent.
The source was uncommitted when compiled; this is not a claim that a later commit
was independently rebuilt. Module and consumer hashes bind each runtime receipt.

The focused DPR1 search group and all57 remaining Qt groups pass. An installed
consumer passes available-index, unavailable-index and legacy flows without
library sources. That first package mount still contains the independent consumer
project. A separate portable runtime contains only the installed prefix, compiled
consumer, two harness scripts and environment metadata; both development projects
are absent. It repeats all three flows and all eight X11/Wayland, software/OpenGL
and scale profiles. The same current consumer compares old/new installed modules in
eight contexts: all256 closed PNG pairs and their frame/state records are exact.

Actual AT-SPI/Orca runs5 and6 each pass twelve phases, covering offscreen and
multiple selection, token actions, focused and keyboard-selected result speech
before Return, editable queries, native undo/redo, owner delivery and cancellation.
They use X11/software and scaled dark Wayland/OpenGL on Ubuntu24.04 arm64,
Qt6.8.3 and the recorded package versions. The reader runs mount only the installed
prefix and private harness. Speech-dispatcher uses null audio output: commands
are observed, while physical listening and engine audio acceptance stay pending.
Qt AT-SPI ChildrenChanged signature warnings remain in the raw logs.

Earlier reader runs1 and2 retain actual missing token Press and EditableText
failures. Runs3 and4 pass an earlier module and are retained as prior evidence.
Source16 lacks selection access; source19 imposed an invalid atomic undo
assumption; source20 loses editor focus on empty-query Undo. Source22 manually
deleted a Loader-owned item and is invalid as supported-owner-removal evidence.
Source23 uses normal Loader unmount and exposes a real result during deferred
deletion. Source24 fixes that with a C++ owner-scene observer; its UI test uses
normal Loader removal, and its separate C++ browser test covers direct deletion.

Run `python3 scripts/verify-file-input-search-accessibility.py` from the repository
root to audit hashes, source reconstruction, runtime bindings, raw closed PNGs
and actual speech windows. Native hierarchy/timing/reader/raster parity, physical
input/display/listening and independent-machine acceptance remain pending.
''')
(CAPSULE/'freeze.py').write_bytes(Path(__file__).read_bytes())
(CAPSULE/'reconstruct.py').write_bytes((BASE/'avelino-search-capsule-reconstruct-20261021.py').read_bytes())
write('files.json',{str(p.relative_to(CAPSULE)):{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(CAPSULE.rglob('*')) if p.is_file()})
print(json.dumps({'capsule':str(CAPSULE),'records':len(records),'overrides':len(overrides),'storedBytes':sum(p.stat().st_size for p in CAPSULE.rglob('*') if p.is_file())}))
