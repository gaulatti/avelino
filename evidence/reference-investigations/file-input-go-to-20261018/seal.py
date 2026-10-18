"""Seal a bounded native UI trial; never modifies its original observations."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

from PIL import Image

ROOT = Path.cwd()
RUN = Path(__file__).resolve().parent
DEST = ROOT / 'evidence/reference-investigations/file-input-go-to-20261018'
assert not DEST.exists(), 'A sealed investigation must not be overwritten'
DEST.mkdir(parents=True)
sha = lambda data: hashlib.sha256(data).hexdigest()


def write(name, value):
    (DEST / name).write_text(json.dumps(value, indent=2) + '\n')


def copy(source, name):
    target = DEST / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


launch = json.loads((RUN / 'launch.json').read_text())
result = json.loads((RUN / 'result.json').read_text())
trace = json.loads((RUN / 'output/ui-trace.json').read_text())
assert result['exitCode'] == 0 and trace['steps'][-1]['phase'] == 'finished'
assert sha(Path(launch['command'][0]).read_bytes()) == launch['executableSha256']
assert len(trace['steps'][-1]['results']) == 1
for name in ['launch.json', 'result.json', 'fixture.json']:
    copy(RUN / name, name)
copy(RUN / 'output/ui-trace.json', 'ui-trace.json')
copy(RUN / 'output/helper.log', 'helper.log')
copy(RUN / 'launch.py', 'launch.py')
copy(Path(__file__), 'seal.py')

captures = []
images = {}
omitted_images = {}
for source in sorted((RUN / 'output').glob('*.ax.txt')):
    raw = source.read_bytes()
    state = raw.decode()
    lines = []
    sidebar = False
    for line in state.splitlines():
        if 'outline sidebar' in line:
            sidebar = True
        if sidebar and 'splitter (disabled' in line:
            sidebar = False
        if sidebar:
            continue
        if 'URL:' in line and '/.codex/tmp/avelino-file-input-' not in line:
            continue
        lines.append(line)
    copy_name = 'captures/' + source.name
    target = DEST / copy_name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('\n'.join(lines).rstrip('\n') + '\n')
    phase = source.name.removesuffix('.ax.txt')
    receipt = source.with_name(phase + '.receipt.json')
    row = dict(phase=phase, path=copy_name, sourcePath=str(source),
               sourceSha256=sha(raw), filtered=True,
               filtering='Sidebar subtree and any unrelated URL rows omitted; original indices retained; trailing blank lines removed',
               receiptAvailable=receipt.exists())
    if receipt.exists():
        captured = json.loads(receipt.read_text())
        assert captured['pid'] == trace['pid']
        assert captured['axSha256'] == sha(raw)
        assert launch['startedAt'] <= captured['capturedAt'] <= result['finishedAt']
        copy(receipt, 'captures/' + receipt.name)
        row.update(capturedAt=captured['capturedAt'], ownerResultCount=captured['ownerResultCount'])
    else:
        row['failure'] = 'AX written before screenshot API failure; no completed snapshot receipt'
    captures.append(row)
    screenshot = source.with_name(phase + '.jpg')
    if screenshot.exists():
        image_row = dict(sourceSha256=sha(screenshot.read_bytes()),
                         sourcePath=str(screenshot), resized=False, cropped=False,
                         masked=False, reencoded=False, artworkVerified=False)
        with Image.open(screenshot) as image:
            assert image.format == 'JPEG'
            image_row.update(format=image.format, pixels=list(image.size))
        if 'ID: open-panel' in state:
            image_row['reason'] = 'Whole original panel image omitted to avoid publishing unrelated configured sidebar names'
            omitted_images[screenshot.name] = image_row
        else:
            copy(screenshot, 'captures/' + screenshot.name)
            images['captures/' + screenshot.name] = image_row

write('captures.json', captures)
fixtures = dict(directories=[], files={})
for source in sorted((RUN / 'fixtures').rglob('*')):
    relative = str(source.relative_to(RUN / 'fixtures'))
    if source.is_dir():
        fixtures['directories'].append(relative)
    elif source.name != '.DS_Store':
        raw = source.read_bytes()
        fixtures['files'][relative] = dict(content=raw.decode(), bytes=len(raw), sha256=sha(raw))
write('fixtures.json', fixtures)

write('operations.json', [
    dict(before='prompt-initial', action='Click native CloseButton', after='close-control-result'),
    dict(before='close-control-result', action='Attempt app.paste of absolute Alpha path; no visible change', after='absolute-alpha-proposal', claim='diagnostic only'),
    dict(before='absolute-alpha-proposal', action='typeText absolute Alpha path', after='absolute-alpha-typed'),
    dict(before='absolute-alpha-typed', action='Return', after='absolute-alpha-submitted'),
    dict(before='relative-child-initial', action='Replace initially selected field with Child', after='relative-child-proposal'),
    dict(before='relative-child-proposal', action='Return', after='relative-child-submitted'),
    dict(before='relative-parent-proposal', action='Return on ..', after='relative-parent-return'),
    dict(before='relative-parent-return', action='Append /', after='relative-parent-slash-proposal'),
    dict(before='relative-parent-slash-proposal', action='Return', after='relative-parent-slash-submitted'),
    dict(before='relative-parent-file-proposal', action='Return on ../A.txt', after='relative-parent-file-return'),
    dict(before='relative-parent-file-return', action='Escape', after='relative-parent-file-cancel'),
    dict(before='absolute-missing-proposal', action='Return', after='absolute-missing-return'),
    dict(before='absolute-missing-return', action='Escape', after='absolute-missing-cancel'),
    dict(before='recents-after-clear', action='Click Alpha recent row', after='recent-alpha-single-click'),
    dict(before='recent-alpha-single-click', action='Attempt AX row double-click; element invalidated during UI change', after='recent-double-click-element-error', claim='Partial tool failure; exact click sequence unproven'),
    dict(before='recent-pointer-clear', action='Pointer double-click at screenshot pixel [788,202]', after='recent-alpha-pointer-double-click'),
    dict(before='absolute-prefix-proposal', action='Down', after='absolute-prefix-down'),
    dict(before='absolute-prefix-down', action='Return', after='absolute-prefix-selected-submit'),
    dict(before='absolute-prefix-retained', action='Attempt app.paste Beta; no visible change', after='paste-beta-result', claim='diagnostic only'),
    dict(before='tab-trial-initial', action='Tab with Edit menu closed', after='tab-trial-result'),
    dict(before='tab-trial-result', action='Attempt Command+A then type root; text appended instead', after='root-proposal', claim='Malformed input; no path-resolution claim'),
    dict(before='root-retry-selected-input', action='Click native clear control then type root', after='root-retry-proposal'),
    dict(before='root-retry-proposal', action='Return', after='root-retry-submitted'),
    dict(before='root-retry-submitted', action='Click Other.png ordinary row', after='other-png-ordinary-click'),
    dict(before='other-png-path-proposal', action='Return', after='other-png-path-submitted'),
    dict(before='other-png-path-submitted', action='Click Open', after='other-png-owner-accepted'),
])

write('investigation.json', dict(
    accepted=False, baseGit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    reference=trace['reference'], helperSha256=launch['executableSha256'],
    helperProvenance='evidence/reference-investigations/file-input-location-policy-20261017/helper-inputs.json',
    sourceLibrary='evidence/reference-investigations/file-input-types-20261017',
    sourceLibraryObjectSha256='61d1e55c6f9c17c841eded420066c72b5611ec51af8c5a4821306f1751ea6514',
    reusedExecutable=True, independentBehaviorSourceReplay=False, physicalInput=False,
    nativeReaderAcceptance='pending', physicalDisplayAcceptance='pending',
    strictRasterAcceptance='pending', completeContextCoverage='pending',
    generalSuggestionOrdering='pending', generalRelativeResolution='pending',
    inputTiming='pending', pasteBehavior='unproven', commandAAfterTab='unproven',
    otherTypeArraysAndPathSelection='pending', expectedImagesChanged=False,
    tolerance='none', approvedExceptions=[], linuxGoToImplementation='pending',
    hostVersion=subprocess.check_output(['sw_vers'], text=True),
    sdk=subprocess.check_output(['xcrun', '--show-sdk-version'], text=True).strip(),
    fixtureRoot=str(RUN / 'fixtures/Navigator Root'),
    successfulCallbacks=1, completedCaptureReceipts=55, partialAXCaptures=2,
    images=images, omittedImages=omitted_images,
    diagnostics=[
        'AX row double-click failed with error -10005 after the path field changed; pointer replay is the completed trial',
        'Two app.paste calls produced no visible field change; no native paste conclusion',
        'Edit menu Paste was disabled; screenshot unavailable for edit-menu-paste-availability',
        'Escape while Edit menu was open dismissed the GoTo sheet; Tab trial in that menu context is excluded; screenshot unavailable for prefix-tab-completion',
        'Exposed menu Cancel closes the menu; a fresh GoTo sheet provides the valid tab-trial result',
        'Command+A after Tab did not replace the field and root text appended; native clear control provided the corrected trial',
    ],
    scope='Same-host reused pinned native helper, one process, public.plain-text, controlled fixtures, actual CUA UI. Bounded observations only; no preference reset, component change or injected completion.'
))
files = {str(p.relative_to(DEST)): dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
         for p in sorted(DEST.rglob('*')) if p.is_file()}
write('files.json', files)
print(f'Sealed {len(files)} members, {len(captures)} AX captures, {len(images)} original images; one native callback')
