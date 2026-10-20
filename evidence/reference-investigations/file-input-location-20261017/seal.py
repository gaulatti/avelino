from pathlib import Path
import hashlib,json,re,shutil,subprocess
from PIL import Image
root=Path.cwd();base=Path('/Users/gaulatti/.codex/tmp');runs={str(n):base/f'avelino-file-input-location-20261017-v{n}'for n in [1,2,3]}
d=root/'evidence/reference-investigations/file-input-location-20261017';assert not d.exists();d.mkdir()
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def copy(src,target):target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
def write(name,value):p=d/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2)+'\n')
for n,p in runs.items():
 assert json.loads((p/'result.json').read_text())['exitCode']==0
 label='root-too-narrow'if n=='1'else'corrected'if n=='2'else'fresh-process'
 for name in ['launch.json','fixture.json','result.json']:
  copy(p/name,d/label/name)
 for name in ['ui-trace.json','helper.log']:copy(p/'output'/name,d/label/name)
 if n=='1':copy(p/'limitation.json',d/label/'limitation.json')
# The first REPL snapshot helper captured its original output-directory binding.
# Preserve each actual source path and raw hash; assign phases explicitly from
# the observed call sequence, not from the temporary containing directory.
phases={
 'corrected': ['leaf-ready','leaf-selected','ancestor-parent-chosen','ancestor-back','ancestor-forward','parent-file-selected','reopened-after-success','fresh-history-selected','current-item-keeps-selection','current-item-keeps-selection-settled','alternate-visited','alternate-reopened-after-cancel','recent-parent-navigation','recent-navigation-back','leaf-before-success','leaf-first-selected','reopened-after-leaf-success','older-recent-parent-visited','nested-menu-escape','parent-selected-again','reopened-after-parent-reaccept'],
 'fresh-process':['fresh-process-open','persisted-recent-leaf-selected','persisted-recent-leaf-selected-settled','before-go-to-folder','go-to-folder-cancel-preserves-selection','go-to-file-result']}
provenance=[]
def filtered_ax(f,label,name):
 raw=f.read_bytes();text=raw.decode();lines=[];recent=False
 for line in text.splitlines():
  if 'URL:'in line and '/avelino-file-input-location-20261017-v2/fixtures/'not in line:continue
  if 'Recent Places'in line:recent=True
  # All unrelated configured recent-place names are omitted. Keep the heading
  # and the two uniquely controlled recent entries used by these probes.
  if recent and 'retargetFromMenuItem:'in line and not re.search(r'(?:Menu Parent|Leaf), ID:',line):continue
  if 'menu Secondary Actions:'in line:recent=False
  lines.append(line)
 target=d/label/(name+'.ax.txt');target.parent.mkdir(parents=True,exist_ok=True);target.write_text('\n'.join(lines)+'\n')
 provenance.append(dict(path=str(target.relative_to(d)),sourcePath=str(f),sourceSha256=sha(raw),filtered=True,filter='Unrelated URL rows and configured recent-place names omitted; images unchanged'))
for label,names in phases.items():
 for name in names:filtered_ax(runs['1']/'output'/(name+'.ax.txt'),label,name)
for n,label in [('2','corrected'),('3','fresh-process')]:
 for f in sorted((runs[n]/'output').glob('*.ax.txt')):filtered_ax(f,label,f.name.removesuffix('.ax.txt'))
images={}
for n,label in [('2','corrected'),('3','fresh-process')]:
 for f in sorted((runs[n]/'output').glob('*.jpg')):
  target=d/label/f.name;copy(f,target)
  with Image.open(target)as im:assert im.format=='JPEG';pixels=list(im.size)
  images[str(target.relative_to(d))]=dict(sourceSha256=sha(f.read_bytes()),pixels=pixels,format='JPEG',resized=False,cropped=False,masked=False,artworkVerified=False)
fixtures={}
for f in sorted((runs['2']/'fixtures').rglob('*')):
 if f.is_file():
  if f.name=='.DS_Store':continue
  raw=f.read_bytes();fixtures[str(f.relative_to(runs['2']/'fixtures'))]=dict(content=raw.decode(),bytes=len(raw),sha256=sha(raw))
write('fixtures.json',dict(files=fixtures))
observations=dict(ancestorOrder=['Leaf','Menu Parent','fixtures'],currentItemPreservesSelection=True,currentItemAddsHistory=False,ancestorClearsFileSelection=True,ancestorAddsNavigationHistory=True,backAndForwardClearFileSelection=True,successfulFolderAddedToRecent=True,browsingAndCancelDoNotAddRecent=True,browsingOlderRecentDoesNotReorder=True,successfulReacceptPromotesWithoutDuplicate=True,freshProcessRetainsRecentOrder=True,recentOrderAfterTwoSuccesses=['Leaf','Menu Parent'],recentOrderAfterBrowsingOlder=['Leaf','Menu Parent'],recentOrderAfterReaccept=['Menu Parent','Leaf'],freshProcessRecentOrder=['Menu Parent','Leaf'],successfulCallbackFiles=['Menu Parent/Parent.txt','Menu Parent/Leaf/First.txt','Menu Parent/Parent.txt'],freshProcessOwnerResults=[],goToFolderPresentation='Separate GoToWindow sheet with a path text field and suggestions',missingPath='Return leaves the prompt open with the verified missing path and no suggestion rows; Escape preserves the selected file',filePathSubmission='Input and prompt-dismissal sequence unresolved; stable main panel later shows Parent.txt selected, without an owner callback',generalRecentCapacityAndCrossApplicationScope='pending',recentUpdatesAcrossDirectoriesAndDirectorySelections='pending',inputTiming='pending')
report=dict(accepted=False,baseGit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',method='Normal CUA native interactions in controlled fixture directories; later path experiments also use observed AX selection/value APIs',helperSha256='8e3db8c9c0089e3365def776393f3b0b5ddeccbf8835aea9079e94022d907b70',sourceLibrary='evidence/reference-investigations/file-input-types-20261017',hostVersion=subprocess.check_output(['sw_vers'],text=True),sdk=subprocess.check_output(['xcrun','--show-sdk-version'],text=True).strip(),independentBehaviorSourceReplay=False,physicalInput=False,physicalDisplayAcceptance='pending',nativeReaderAcceptance='pending',strictRasterAcceptance='pending',completeContextCoverage='pending',linuxImplementation='pending',expectedImagesChanged=False,approvedExceptions=[],tolerance='none',images=images,accessibility=provenance,observations=observations,snapshotTransport='The first REPL snapshot helper retained its original output directory; per-file source paths and raw hashes identify the copied bytes. Later corrected/fresh-process phases are assigned explicitly. Overwritten earlier phase bytes are not reconstructed.',rootTooNarrowAttempt='The first helper used the nested initial directory as its redaction root, hiding its controlled parent callback URL. Its launch, trace, result and limitation remain preserved; corrected callbacks all belong to the complete controlled root.',pathInputLimitations='Command+A did not reliably replace text in this minimal helper; AX value/selection and keyboard retries produced inconsistent prompt observations. General file-path submission and dismissal semantics remain pending.',menuArtworkVerified=False)
write('investigation.json',report)
(d/'README.md').write_text('''# Native FileInput location-menu investigation

This diagnostic supplement records the unchanged pinned desktop component through
its existing source-built helper. It approves no Linux implementation or native
parity. Reference pins, expected captures, tolerances and exceptions are unchanged.
Apple source and executables remain outside the Linux repository.

The corrected run starts with a complete controlled fixture root. The location
menu lists the current folder, its ancestors, and Recent Places. Choosing the
current folder preserves the selected file and leaves Back disabled in a fresh
history. Choosing an ancestor clears file selection and adds a navigation step;
Back and Forward restore locations with file selection cleared. Menu-only Escape
leaves the chooser open. Those menu/navigation actions send no owner result.

Accepting `Menu Parent/Parent.txt` adds `Menu Parent` to Recent Places. Visiting
`Alternate/Leaf` and cancelling retains that visible location on reopening but
does not add it to Recent Places. Accepting `Menu Parent/Leaf/First.txt` puts
`Leaf` before `Menu Parent`. Browsing the older recent parent leaves that order
unchanged. Accepting Parent.txt again promotes its folder without a duplicate.
These are three single-file cases. Recent updates for cross-directory or directory
selections remain pending. Three successful callbacks retain exact controlled URLs and report the panel
visible during the callback. Final cancellation adds no fourth result.

A separately started process preserves the order `Menu Parent`, `Leaf`, and its
recent Leaf entry navigates to the expected controlled directory. This establishes
same-bundle process persistence on this configured host. General capacity,
cross-application sharing, unavailable volumes and independent-machine behavior
remain pending; unrelated configured recent-place names are not Linux defaults.

Go to Folder appears as a separate GoToWindow sheet with a path field and
suggestions. Return on a verified missing path leaves the prompt open without a
candidate row; Escape returns to the selected First.txt without an owner callback.
The file-path experiments are diagnostic: Command+A did not reliably replace text
in the minimal helper, and AX value/selection plus keyboard retries gave
inconsistent prompt observations. After dismissing the remaining prompt, the
stable main chooser shows Parent.txt selected and no owner result. General file
submission/dismissal and timing are unresolved; these attempts are not grounds
for silently accepting a guessed file-path behavior.

The first attempt had a helper redaction root that was too narrow for its parent
navigation; its callback URL was therefore hidden. Its launch, trace, result and
limitation are retained separately. Corrected callbacks are all inside their
complete controlled root. The first REPL snapshot helper also retained its original
output directory binding. Corrected/fresh-process phase files are copied from their
actual storage paths, recorded with raw source hashes. Some earlier same-name
snapshots were overwritten; unavailable bytes are not reconstructed. Transient AX
states can show a new location with old selected rows or an exposed old menu;
settled observations and callbacks remain distinct.

AX excerpts omit unrelated URL rows and configured recent-place names. Every
filter and raw source hash is recorded. Five JPEGs are copied as original CUA
bytes at their recorded dimensions, without resizing, cropping, masking or
re-encoding. The menu artwork and all JPEG/raster equivalence remain unverified.
This is a single-host observation using a reused source-built library, not a
fresh independent behavior-source rebuild, full accessibility hierarchy, physical
input/display, reader or strict native acceptance.

Run `python3 scripts/verify-file-input-location.py` to audit the retained records.
Desktop coverage remains 75/80 candidates and 0/80 accepted entries; FileInput,
the Linux location menu and native path presentation remain pending.
''')
copy(Path(__file__),d/'seal.py')
files={str(f.relative_to(d)):dict(bytes=f.stat().st_size,sha256=sha(f.read_bytes()))for f in sorted(d.rglob('*'))if f.is_file()};write('files.json',files)
print('Sealed',len(files),'native location investigation members')
