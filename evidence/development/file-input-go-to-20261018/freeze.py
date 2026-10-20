"""Preserve scoped Linux results and exact sources/runtime without altering images."""
from pathlib import Path
import gzip
import hashlib
import json
import shutil
import stat

ROOT = Path.cwd()
ART = ROOT / 'artifacts/resumed-avelino-20261016'
DEST = ROOT / 'evidence/development/file-input-go-to-20261018'
assert not DEST.exists()
DEST.mkdir(parents=True)
(DEST / 'blobs').mkdir()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
CHUNK = 8 * 1024 * 1024


def write(name, value):
    path = DEST / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def copy(source, name):
    target = DEST / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def store(path):
    raw = path.read_bytes()
    chunks = []
    for offset in range(0, len(raw), CHUNK):
        part = raw[offset:offset + CHUNK]
        digest = sha(part)
        target = DEST / 'blobs' / (digest + '.gz')
        if not target.exists():
            target.write_bytes(gzip.compress(part, compresslevel=6, mtime=0))
        chunks.append(dict(sha256=digest, bytes=len(part)))
    return dict(bytes=len(raw), sha256=sha(raw), mode=stat.S_IMODE(path.stat().st_mode), chunks=chunks)


specs = {}
for number in range(55, 61):
    name = f'file-input-qt-v{number}'
    source = ART / name
    inputs = json.loads((source / 'inputs.json').read_text())
    terminal = json.loads((source / 'result.json').read_text())
    assert terminal['exitCode'] == (8 if number in [55, 56, 58] else 0)
    files = {}
    for relative, expected in inputs['files'].items():
        path = source / 'source' / relative
        assert sha(path.read_bytes()) == expected, (name, relative)
        files[relative] = store(path)
    specs[name] = dict(files=files, inputRecord='attempts/' + name + '/inputs.json')
    for path in sorted(source.iterdir()):
        if path.is_file():
            copy(path, 'attempts/' + name + '/' + path.name)
    for path in sorted((source / 'ui-output').glob('*')):
        if path.is_file():
            copy(path, 'attempts/' + name + '/ui-output/' + path.name)
write('source-specs.json', specs)

package = ART / 'file-input-go-to-package-v2'
display = ART / 'file-input-go-to-display-v2'
assert json.loads((package / 'result.json').read_text())['exitCode'] == 0
assert json.loads((display / 'result.json').read_text())['exitCode'] == 0
for name, source in [('package', package), ('display', display)]:
    for path in sorted(source.iterdir()):
        if path.is_file():
            copy(path, name + '/' + path.name)
for path in sorted((display / 'output').rglob('*')):
    if path.is_file():
        copy(path, 'display/output/' + str(path.relative_to(display / 'output')))
for path in sorted((package / 'runtime/output').iterdir()):
    if path.is_file():
        copy(path, 'captures/' + path.name)
runtime = {}
for folder in ['install', 'consumer-build']:
    for path in sorted((package / 'runtime' / folder).rglob('*')):
        if path.is_file():
            runtime[str(path.relative_to(package / 'runtime'))] = store(path)
copy(package / 'runtime/environment.json', 'runtime-environment.json')
write('runtime-spec.json', runtime)

stability = {}
prior = ROOT / 'evidence/development/file-input-location-20261017/captures'
for path in sorted((DEST / 'captures').glob('*.json')):
    record = json.loads(path.read_text())
    previous = json.loads((prior / path.name).read_text())
    assert record['closed'] == previous['closed'] and record['sizing'] == previous['sizing']
    rows = {}
    for closed in record['closed']:
        name = path.stem + '-' + closed['configuration']['id'] + '.png'
        assert (DEST / 'captures' / name).read_bytes() == (prior / name).read_bytes(), name
        rows[name] = sha((DEST / 'captures' / name).read_bytes())
    stability[path.name] = dict(prior='evidence/development/file-input-location-20261017/captures/' + path.name, images=rows,
                                completeClosedAndSizingMetadataUnchanged=True)
assert sum(len(row['images']) for row in stability.values()) == 256
write('closed-stability.json', stability)
write('validation.json', dict(
    accepted=False, reference='fe8a1d462fbd793d883fb92086a16aa2947e32c9',
    baseGit='78708f69205379cc858f596a913bb32063c16b9e', finalSource='file-input-qt-v60', sourceFiles=567,
    desktopCandidateCoverage=[75, 80], acceptedDesktopEntries=0,
    expectedImagesChanged=False, tolerance='none', approvedExceptions=[],
    finalFullQtSuiteRerun=False, focusedQtTargets=8, packageContexts=8, displayProfiles=8,
    independentConsumerBuild=True, libraryAndConsumerSourcesAbsentAtRuntime=True,
    consumerActionsPerContext=30, consumerImagesPerContext=49, pointerEventsPerContext=62, keyEventsPerContext=164,
    closedImagesUnchanged=256, physicalDisplay=False, physicalInput=False, physicalListening=False,
    toolchain=json.loads((package / 'inputs.json').read_text())['imageId'],
    gates={name:'pending' for name in ['completeFileChooser','nativeRaster','nativeHierarchy','nativeReader',
        'goToAtSpiOrcaFlow','physicalDisplay','physicalInput','physicalListening','independentMachine',
        'generalSuggestionRanking','generalHistoryCapacity','relativeResolution','otherTypeArraysAndPathSelection','nativeSizing','nativeInputTiming']},
    scope='Linux candidate checkpoint: frozen attempts 55-60, eight focused Qt targets, fresh independent source-free consumer in eight contexts and eight virtual display profiles. Qt modal reachability and key focus are tested; the new actual AT-SPI/Orca GoTo flow is pending. No native equivalence gate is closed.'
))
copy(Path(__file__), 'freeze.py')
print('Preserved source attempts 55-60, fresh runtime, 8 package contexts and 8 display profiles; strict parity pending')
