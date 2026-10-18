from pathlib import Path
import hashlib,json,re,shutil,subprocess
from urllib.parse import unquote,urlsplit
from PIL import Image
root=Path.cwd();base=Path('/Users/gaulatti/.codex/tmp/avelino-file-input-location-harness-20261017-v1');d=root/'evidence/reference-investigations/file-input-location-policy-20261017';assert not d.exists();d.mkdir()
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def copy(src,target):target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
def write(name,value):p=d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
copy(base/'build-command.json',d/'helper-build-command.json');copy(base/'build.log',d/'helper-build.log');copy(base/'inputs.json',d/'helper-inputs.json')
object_path=Path(json.loads((base/'build-command.json').read_text())['command'][-3]);assert object_path.name=='Sabella.o'
records={};images={};provenance=[]
for name in ['run-a','run-a2','run-b','run-c']:
 p=base/name;result=json.loads((p/'result.json').read_text());assert result['exitCode']==(-5 if name=='run-a'else 0)
 for filename in ['launch.json','fixture.json','result.json']:copy(p/filename,d/name/filename)
 copy(p/'output/helper.log',d/name/'helper.log')
 if name=='run-a':continue
 for filename in ['ui-trace.json','snapshots.json']:copy(p/'output'/filename,d/name/filename)
 trace=json.loads((p/'output/ui-trace.json').read_text());assert trace['steps'][-1]['phase']=='finished';records[name]=trace['steps'][-1]['results']
 for f in sorted((p/'output').glob('*.ax.txt')):
  raw=f.read_bytes();source=raw.decode();controls_only='Where:, Value: Documents,'in source;recent=False;lines=[]
  for line in source.splitlines():
   if controls_only:
    if re.search(r'^Window:|sheet |menu button|pop up button Where:|button (?:\(disabled\) )?(?:back|forward|Open|Cancel|New Folder)|Recent Places|(?:Mixed Root|Recent Child|Recent-\d\d), ID: retargetFromMenuItem:',line):lines.append(line)
    continue
   if 'URL:'in line and '/avelino-file-input-location-harness-20261017-v1/fixtures/'not in line:continue
   if 'menu Secondary Actions:'in line:recent=False
   if 'Recent Places'in line:recent=True
   if recent and 'retargetFromMenuItem:'in line and not re.search(r'(?:Mixed Root|Recent Child|Recent-\d\d), ID:',line):continue
   lines.append(line)
  target=d/name/f.name;target.write_text('\n'.join(lines)+'\n');provenance.append(dict(path=str(target.relative_to(d)),sourcePath=str(f),sourceSha256=sha(raw),filtered=True,controlsOnly=controls_only))
 for f in sorted((p/'output').glob('*.jpg')):
  target=d/name/f.name;copy(f,target)
  with Image.open(target)as image:assert image.format=='JPEG';size=list(image.size)
  images[str(target.relative_to(d))]=dict(sourceSha256=sha(f.read_bytes()),pixels=size,format='JPEG',resized=False,cropped=False,masked=False,artworkVerified=False)
relative=lambda row:[unquote(urlsplit(url).path).split('/fixtures/',1)[1]for url in row['urls']]
assert len(records['run-a2'])==13 and len(records['run-b'])==2 and len(records['run-c'])==1
assert relative(records['run-b'][0])==['Mixed Root/Recent Child/']and relative(records['run-b'][1])==['Mixed Root/']
assert relative(records['run-c'][0])==['Mixed Root/Blocked.png']
fixtures={}
for f in sorted((base/'fixtures').rglob('*')):
 if f.is_file()and f.name!='.DS_Store':
  raw=f.read_bytes();fixtures[str(f.relative_to(base/'fixtures'))]=dict(content=raw.decode(),bytes=len(raw),sha256=sha(raw))
write('fixtures.json',dict(files=fixtures))
report=dict(accepted=False,baseGit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',sourceLibrary='evidence/reference-investigations/file-input-types-20261017',sourceLibraryObjectSha256=sha(object_path.read_bytes()),helperSha256=json.loads((base/'inputs.json').read_text())['executableSha256'],hostVersion=subprocess.check_output(['sw_vers'],text=True),sdk=subprocess.check_output(['xcrun','--show-sdk-version'],text=True).strip(),physicalInput=False,independentBehaviorSourceReplay=False,physicalDisplayAcceptance='pending',nativeReaderAcceptance='pending',strictRasterAcceptance='pending',completeContextCoverage='pending',linuxImplementation='in-progress',expectedImagesChanged=False,tolerance='none',approvedExceptions=[],images=images,accessibility=provenance,observations=dict(recentLimitObserved=10,capacityAcceptedFolders=[f'Recent-{i:02}'for i in range(1,13)],recentAfterCapacity=[f'Recent-{i:02}'for i in range(12,2,-1)],secondConsumerInitialRecent=[f'Recent-{i:02}'for i in range(12,2,-1)],differentBundleIdentifiersSharePool=True,currentFolderRecordedForCrossDirectorySelection='Mixed Root',crossDirectoryCallbackOrder=relative(records['run-a2'][0]),currentFolderRecordedForSelectedDirectory='Mixed Root',selectedDirectoryResult=['Mixed Root/Recent Child/'],unselectedCurrentDirectoryCanBeAccepted=True,currentDirectoryResult=['Mixed Root/'],sameFolderPathPreservesSelection=True,missingPathCancelPreservesSelection=True,normalEditMenuReplacesPathInput=True,existingFilePathSelectsWithoutOwner=True,pathSelectedNonmatchingFileResult=['Mixed Root/Blocked.png'],ordinaryPointerCannotSelectSameNonmatchingFile=True,relativeInput='Trial ../Recent-12 had a Recent Child suggestion and navigated there; the resolution rule and suggestion-settling timing remain pending',hiddenFolderExplicitNavigation=True,lastPathInputRetainedAcrossOpenings=True,cancelledInvalidPathDoesNotReplaceRememberedInput=True,inputTiming='pending',otherTypeArraysAndPathSelection='pending',generalCrossDirectoryResultOrder='pending'),successfulCallbacks=16,harnessChanges=['Normal Edit/Quit responder menus; unchanged public component','No programmatic panel directory assignment; actual UI navigates the controlled folders','Timestamped recorder and capture receipts with each run passed explicitly'],startupFailure='First launch omitted the required source-library resource bundle and exited -5. The failure is preserved; the corrected bundles copy identical existing library resources.',scope='Three successful processes on the same host, including two distinct app bundle identifiers. The source library object is reused; this is not an independent behavior-source rebuild.')
write('investigation.json',report)
(d/'README.md').write_text('''# Native FileInput recent-policy and path-input supplement

This record extends the earlier location investigation without modifying any
sealed record, reference pin, expected image, tolerance or exception. It uses the
unchanged pinned component and an externally built helper with normal Edit/Quit
responder menus, timestamped observations and no programmatic panel-directory
assignment. The source library object and resource bundle are reused. Apple
source, build products and capture tooling remain outside Avelino.

Two files selected across a root and expanded child return together, while
Recent Places records the visible `Mixed Root`, not each selected file's parent.
Twelve subsequent successful folder locations leave exactly the latest ten,
newest first (`Recent-12` through `Recent-03`). A second app with a different
bundle identifier sees that same pool before making any selection. Selecting a
directory in List returns the directory URL but records the unchanged visible
parent. With no row selected, a directory chooser can accept its current folder.
All fifteen callbacks in those two processes retain their exact controlled URLs.

Normal Command+A now replaces the path field. A verified missing path remains
in its own prompt; Escape preserves the underlying selected file. Submitting an
existing file path closes the prompt and selects that file without calling the
owner. Submitting the current folder preserves its selected file. An explicitly
typed hidden folder can be reached. Successful path input persists across openings and these consumer processes.
Cancelling the invalid input leaves the previous saved path intact.

The text-only process exposes a distinct source behavior: Go to Folder selects
`Blocked.png`, Open is enabled, and acceptance returns that exact URL. Ordinary
pointer selection of the same PNG remains disabled. Both routes use the same
unchanged `public.plain-text` configuration. This does not establish the path
selection rule for every other type array. Its sixteenth callback is retained.
The relative-input trial `../Recent-12` has a Recent Child suggestion and
navigates there. It does not establish relative normalization or whether
suggestion updates had settled; those input/timing gates remain pending.

The first startup failure lacks the required source-library resource bundle and
exits -5. It is preserved separately; corrected launches copy the existing bundle
unchanged. Each successful run receives its own capture object/output path and
records timestamps and recorder PID/count receipts, avoiding the earlier snapshot
helper's captured-directory problem. AX records omit unrelated URL rows and
configured recent-place names. Initial Documents views retain panel controls and controlled recent entries only.
Per-file raw hashes and filtering scope are recorded. The single JPEG is copied
as original CUA bytes without resizing, cropping, masking or re-encoding.

This is same-host diagnostic source evidence, not a fresh independent source
behavior rebuild, complete hierarchy, reader, physical input/display, menu/raster
acceptance or a portable statement about every macOS configuration. General type
conformance, relative input, callback ordering and timing remain pending. Linux
location controls are in progress; desktop coverage remains 75/80 candidates and
0/80 accepted entries. Run `python3 scripts/verify-file-input-location-policy.py`
to audit the record.
''')
copy(Path(__file__),d/'seal.py')
files={str(f.relative_to(d)):dict(bytes=f.stat().st_size,sha256=sha(f.read_bytes()))for f in sorted(d.rglob('*'))if f.is_file()};write('files.json',files);print('Sealed native policy:',len(files),'members, 16 callbacks')
