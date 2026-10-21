from pathlib import Path
import gzip,hashlib,io,json,subprocess

BASE=Path('/Users/gaulatti/.codex/tmp')
ROOT=BASE/'avelino-reference-repair-20261020-v1'
ARTIFACTS=Path('/Users/gaulatti/source/gaulatti/avelino/artifacts/resumed-avelino-20261016')
DIRECTORY=ROOT/'evidence/development/file-input-search-token-editing-20261021'
DIRECTORY.mkdir(exist_ok=False)
sha=lambda raw:hashlib.sha256(raw).hexdigest()
records={}
def put(name,raw):
    assert name not in records,name
    digest=sha(raw);png=raw.startswith(b'\x89PNG\r\n\x1a\n')
    stored='images/'+digest+'.png' if png else 'blobs/'+digest+'.gz'
    path=DIRECTORY/stored;path.parent.mkdir(exist_ok=True)
    if not path.exists():path.write_bytes(raw if png else gzip.compress(raw,mtime=0))
    records[name]={'stored':stored,'sha256':digest,'bytes':len(raw)}
def tree(prefix,directory):
    for path in sorted(directory.rglob('*')):
        if path.is_file():put(prefix+'/'+str(path.relative_to(directory)),path.read_bytes())
def write(name,value):(DIRECTORY/name).write_text(json.dumps(value,indent=2)+'\n')

assert json.loads((BASE/'avelino-file-search-portable-20261021-v5/result.json').read_text())['exitCode']==0
assert json.loads((BASE/'avelino-file-search-closed-regression-20261021-v5/result.json').read_text())['byteIdentical']==256
sources={}
for number in range(28,37):
    controller=BASE/f'avelino-file-search-compiled-20261020-v{number}'
    inputs=json.loads((controller/'inputs.json').read_text());snapshot=Path(inputs['snapshot'])
    tree(f'source{number}/controller',controller)
    names=list(inputs['sourceFiles']);changed=[]
    batch=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=('\n'.join(inputs['parent']+':'+n for n in names)+'\n').encode());stream=io.BytesIO(batch)
    for name in names:
        raw=(snapshot/name).read_bytes();assert sha(raw)==inputs['sourceFiles'][name]
        header=stream.readline().split()
        if len(header)==3:
            assert header[1]==b'blob';prior=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        else:assert header[-1]==b'missing';prior=None
        if raw!=prior:put(f'source{number}/overrides/'+name,raw);changed.append(name)
    assert not stream.read()
    sources[str(number)]={'parent':inputs['parent'],'selectedFiles':len(names),'overrides':changed}
for number in [34,35,36]:tree(f'consumer{number}/output',ARTIFACTS/f'file-search-compiled-v{number}/package/search-runtime')
for number in [9,10]:
    tree(f'reader{number}/controller',BASE/f'avelino-file-search-a11y-20261021-v{number}')
    tree(f'reader{number}/output',ARTIFACTS/f'file-search-a11y-v{number}')
for number in [4,5]:
    tree(f'portable{number}/controller',BASE/f'avelino-file-search-portable-20261021-v{number}')
    tree(f'portable{number}/output',ARTIFACTS/f'file-search-portable-v{number}/proof')
    put(f'portable{number}/run.py',(BASE/f'avelino-search-portable-20261021-v{number}.py').read_bytes())
    tree(f'closed{number}/controller',BASE/f'avelino-file-search-closed-regression-20261021-v{number}')
    version=35 if number==4 else 36
    tree(f'closed{number}/output',ARTIFACTS/f'file-search-compiled-v{version}/closed-regression')
    put(f'closed{number}/run.py',(BASE/f'avelino-search-token-closed-20261021-v{number}.py').read_bytes())
put('consumer-check.py',(BASE/'avelino-file-search-token-check-20261021.py').read_bytes())
put('historical-audits.log',(BASE/'avelino-file-search-token-local-audits-20261021.log').read_bytes())
put('preserved-untracked-cache.json',(BASE/'avelino-preserved-capsule-cache-20261021-v1/receipt.json').read_bytes())
native=ROOT/'evidence/reference-investigations/file-input-search-history-20261021/files.json'
put('native-manifest.json',native.read_bytes())
write('source-overrides.json',sources)
write('records.json',records)
write('validation.json',{
    'sourceAttempt':36,'sourceParent':sources['36']['parent'],'selectedSourceFiles':sources['36']['selectedFiles'],
    'coreRuntimeExecutedOnSourceAttempt':34,'identicalInstalledPrefixSourceAttempts':[34,35,36],
    'focusedQtGroups':9,'installedConsumerSourceAttempt':36,'consumerSearchPhases':9,
    'portableAttempt':5,'portableProfiles':8,'portableSessionPhases':10,'closedAttempt':5,'closedImagePairs':256,
    'readerAttempts':[9,10],'readerPhasesEach':17,
    'historicalFullSuite':{'sourceAttempt':24,'groups':58,'capsule':'evidence/development/file-input-search-accessibility-20261021'},
    'nativeObservations':'evidence/reference-investigations/file-input-search-history-20261021',
    'retainedFailures':{'28':'expected red: whole replacement retains Filename','29':'invalid Popup visibility assertion; corrected to actual delegates','30':'throwError overload compile error','31':'real undo restoration and merged-group failures','32':'private Qt separate helper compile error; corrected to exact guarded separator flag','consumer34':'input focus/selection not established before replacement; new consumer verifies editable-region focus and selection','portable4':'display phase contract still expected old seven phases','closed4':'comparison context directory missing before capture'},
    'accepted':False,'nativeReaderComparisonAccepted':False,'speechEngineAudioAccepted':False,
    'physicalInputAccepted':False,'physicalDisplayAccepted':False,'independentMachineAccepted':False,
    'expectedImagesChanged':False,'referenceChanged':False,'tolerancesChanged':False,
})
(DIRECTORY/'README.md').write_text('''# Search token editing checkpoint

This is scoped Linux candidate evidence. Native parity, full editing/commit and
query membership, AX identity/hierarchy, reader comparison, engine audio,
physical input/display and independent-machine acceptance remain pending. Pins,
expected images, tolerances and earlier capsule members are unchanged.

The search-specific editor associates token metadata with normalized Qt6.8.3
undo positions and marks token creation as a Qt edit boundary. Qt still owns
text, selection, composition and undo commands. Whole keyboard/assistive
replacement returns to raw presentation; Undo/Redo restores token metadata.
Actual input tests cover identical literal replacement, read-only rejection,
selection without replacement, redo branches and external query assignment.
The adapter stores mode metadata rather than whole text at every undo position.

Attempts28 through36 preserve their exact selected source snapshots through
immutable Git parents and explicit overrides. These are selected compile/test
inputs, not a full project archive. Source28 is the expected red regression;
29 has an invalid popup-object assertion;30 and32 retain compile errors;
31 exposes real undo restoration/merging failures. Sources33-36 pass the initial
search group. Source34 passes all nine focused groups. All158 installed prefix
files and all223 component/input-test source files are identical34/36. The
separate current consumer36 is rebuilt and passes available/unavailable/legacy
flows, including replacement, Undo and Redo. Source34's consumer failure is
retained;35 adds explicit editable-region focus/selection checks and passes.

Portable5 contains only the installed prefix, current compiled consumer, two
harness scripts and measured environment metadata: both development projects
are absent. Three flows and all eight X11/Wayland, software/OpenGL and scale
profiles pass. Each search session has ten phases. Portable4 is retained with
its obsolete phase-contract failure; the new contract preserves all prior
readiness and appearance checks and adds the three token-edit phases.

Actual AT-SPI/Orca9/10 execute module34 on X11/software and scaled dark
Wayland/OpenGL, passing17 phases each, including assistive token replacement
and native key Undo/Redo. These are bound to current36 by exact installed-byte
identity, not mislabeled as fresh36 executions. Speech-dispatcher uses null
audio. Closed comparison5 uses the current consumer with both old/new installed
prefixes in eight source-free virtual contexts: all256 FileInput PNGs and raw
closed frame/state records are exact. Failed comparison4 lacked its output
context directories and is retained separately. Historical full58 Qt success
belongs to source24, not the current candidate.

`records.json` maps original JSON, logs, Linux harnesses and raw PNGs to
content-addressed compressed blobs. A historical audit encountered an ignored
Python bytecode cache outside a frozen capsule's inventory; that cache was
preserved externally, and the unchanged historical capsule audit then passed.
No recorded capsule member was changed or excluded to conceal the extra file.
''')
(DIRECTORY/'freeze.py').write_bytes(Path(__file__).read_bytes())
write('files.json',{str(p.relative_to(DIRECTORY)):{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(DIRECTORY.rglob('*')) if p.is_file()})
print(json.dumps({'capsule':str(DIRECTORY),'records':len(records),'selectedSourceFiles':sources['36']['selectedFiles'],'sourceOverrides':{k:len(v['overrides']) for k,v in sources.items()},'storedBytes':sum(p.stat().st_size for p in DIRECTORY.rglob('*') if p.is_file())},indent=2))
