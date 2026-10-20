"""Preserve native history observations; Apple tooling stays external."""
from pathlib import Path
import hashlib
import json
import plistlib
import re
import shutil
import subprocess

from PIL import Image

BASE = Path(__file__).resolve().parent
ROOT = Path.cwd()
DEST = ROOT / 'evidence/reference-investigations/file-input-go-to-history-20261018'
assert not DEST.exists()
DEST.mkdir(parents=True)
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def write(name, value):
    path = DEST / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def copy(source, name):
    path = DEST / name
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, path)


images, captures, consumers = {}, [], {}
for name, run in [('run-a', BASE), ('run-b', BASE / 'run-b'), ('run-c', BASE / 'run-c')]:
    launch = json.loads((run / 'launch.json').read_text())
    terminal = json.loads((run / 'result.json').read_text())
    trace = json.loads((run / 'output/ui-trace.json').read_text())
    assert terminal['exitCode'] == 0 and trace['steps'][-1]['phase'] == 'finished'
    assert all(step['results'] == [] for step in trace['steps'])
    binary = Path(launch['command'][0])
    assert sha(binary.read_bytes()) == launch['executableSha256']
    bundle = plistlib.loads((binary.parent.parent / 'Info.plist').read_bytes())['CFBundleIdentifier']
    consumers[name] = dict(bundleIdentifier=bundle, executableSha256=launch['executableSha256'],
                           pid=trace['pid'], completedCaptures=0)
    for filename in ['launch.json', 'fixture.json', 'result.json', 'launch.py']:
        copy(run / filename, name + '/' + filename)
    for filename in ['ui-trace.json', 'helper.log']:
        copy(run / 'output' / filename, name + '/' + filename)
    for source in sorted((run / 'output').glob('*.ax.txt')):
        raw = source.read_bytes()
        lines, sidebar = [], False
        for line in raw.decode().splitlines():
            if 'outline sidebar' in line:
                sidebar = True
            if sidebar and 'splitter (disabled' in line:
                sidebar = False
            if sidebar:
                continue
            if 'URL:' in line and '/.codex/tmp/avelino-file-input-' not in line:
                continue
            if 'retargetFromMenuItem:' in line and not re.search(
                r'(?:History-\d\d|History Root|Navigator Root|Mixed Root|Recent-\d\d), ID:', line):
                continue
            lines.append(line)
        phase = source.name.removesuffix('.ax.txt')
        target = DEST / name / source.name
        target.write_text('\n'.join(lines).rstrip('\n') + '\n')
        receipt_source = source.with_name(phase + '.receipt.json')
        receipt = json.loads(receipt_source.read_text())
        assert receipt['pid'] == trace['pid'] and receipt['axSha256'] == sha(raw)
        assert receipt['ownerResultCount'] == 0
        assert launch['startedAt'] <= receipt['capturedAt'] <= terminal['finishedAt']
        copy(receipt_source, name + '/' + receipt_source.name)
        captures.append(dict(run=name, phase=phase, path=name + '/' + source.name,
                             sourcePath=str(source), sourceSha256=sha(raw),
                             capturedAt=receipt['capturedAt'], ownerResultCount=0, filtered=True,
                             filtering='Sidebar subtree, unrelated URL rows and unrelated menu ancestors omitted; original indices retained; trailing blank lines removed'))
        consumers[name]['completedCaptures'] += 1
        screenshot = source.with_name(phase + '.jpg')
        if screenshot.exists():
            assert 'GoToWindow' in raw.decode(), 'Only controlled path-sheet images are included'
            copy(screenshot, name + '/' + screenshot.name)
            with Image.open(screenshot) as image:
                assert image.format == 'JPEG'
                pixels = list(image.size)
            images[name + '/' + screenshot.name] = dict(sourcePath=str(screenshot),
                sourceSha256=sha(screenshot.read_bytes()), pixels=pixels, format='JPEG',
                resized=False, cropped=False, masked=False, reencoded=False, artworkVerified=False)

fixtures = dict(directories=[], files={})
for path in sorted((BASE / 'fixtures').rglob('*')):
    relative = str(path.relative_to(BASE / 'fixtures'))
    if path.is_dir():
        fixtures['directories'].append(relative)
    elif path.name != '.DS_Store':
        raw = path.read_bytes()
        fixtures['files'][relative] = dict(bytes=len(raw), sha256=sha(raw), content=raw.decode())
write('fixtures.json', fixtures)
write('captures.json', captures)
write('investigation.json', dict(
    accepted=False, baseGit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',
    helperProvenance='evidence/reference-investigations/file-input-location-policy-20261017/helper-inputs.json',
    sourceLibrary='evidence/reference-investigations/file-input-types-20261017',
    reusedExecutable=True, independentBehaviorSourceReplay=False, physicalInput=False,
    physicalDisplayAcceptance='pending', nativeReaderAcceptance='pending',
    strictRasterAcceptance='pending', completeContextCoverage='pending',
    generalHistoryCapacity='pending', generalSuggestionRanking='pending',
    unavailableTargetBehavior='pending', generalRelativeResolution='pending', inputTiming='pending',
    linuxGoToImplementation='pending', expectedImagesChanged=False, tolerance='none', approvedExceptions=[],
    fixtureRoot=str(BASE / 'fixtures/History Root'), consumers=consumers, images=images,
    successfulCallbacks=0, navigatedFolders=[f'History-{i:02}' for i in range(1, 13)],
    emptyFieldRecents=[f'History-{i:02}' for i in range(12, 7, -1)],
    afterPromotion=['History-10', 'History-12', 'History-11', 'History-09', 'History-08'],
    sourceOfEarlierTwelveRows='evidence/reference-investigations/file-input-location-policy-20261017/run-a2/existing-file-path-prompt.ax.txt',
    earlierTwelveRowsHeading='Go to:',
    scope='Three successful reused-helper processes, two distinct consumer bundle identifiers, twelve navigation-only GoTo folder destinations and ordinary-navigation control; public.plain-text on the same host. No preference reset or owner acceptance.'
))
copy(Path(__file__), 'seal.py')
write('files.json', {str(p.relative_to(DEST)): dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
                     for p in sorted(DEST.rglob('*')) if p.is_file()})
print(f'Sealed {len(captures)} complete history captures and {len(images)} original images; three terminal processes, zero callbacks')
