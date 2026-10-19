from pathlib import Path
import hashlib
import json
import shutil

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
BASE = P.parent
TARGET = ROOT / 'evidence/development/mobile-shell-20261019'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def copy_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    assert not target.exists(), str(target)
    shutil.copy2(source, target)


def copy_tree(source, target):
    for path in sorted(source.rglob('*')):
        if path.is_file():
            copy_file(path, target / path.relative_to(source))


def write(name, value):
    (TARGET / name).write_text(json.dumps(value, indent=2) + '\n')


for name in ['mobile-shell-compiled-v5', 'mobile-shell-compiled-v6', 'mobile-shell-compiled-v7',
             'mobile-shell-runtime-v2', 'mobile-shell-runtime-v3',
             'mobile-shell-contracts-v1', 'mobile-shell-source-checks-v1',
             'mobile-shell-date-replay-v1', 'mobile-shell-footer-replay-v1',
             'mobile-shell-button-group-replay-v1', 'mobile-shell-installed-smoke-v1',
             'mobile-shell-gallery-v1']:
    assert json.loads((BASE / name / 'result.json').read_text())['exitCode'] == 0, name

TARGET.mkdir()
(TARGET / '.gitattributes').write_text('*.log -text -whitespace\nlibrary-v1/implementation-inputs/src/Avelino/daterangeinput.cpp -text -whitespace\nruntime-v2/display/capture-tool-version.txt -text -whitespace\nruntime/display/capture-tool-version.txt -text -whitespace\n')
for name, dest in [('mobile-shell-library-v1', 'library-v1'),
                   ('mobile-shell-runtime-preflight-v1', 'runtime-preflight-v1'),
                   ('mobile-shell-runtime-preflight-v2', 'runtime-preflight-v2'),
                   ('mobile-shell-compiled-v2', 'compiled-v2'),
                   ('mobile-shell-compiled-v3', 'compiled-v3'),
                   ('mobile-shell-compiled-v4', 'compiled-v4'),
                   ('mobile-shell-compiled-v5', 'compiled-v5'),
                   ('mobile-shell-compiled-v6', 'compiled-v6'),
                   ('mobile-shell-compiled-v7', 'compiled-v7'),
                   ('mobile-shell-disk-recovery-v1', 'disk-recovery'),
                   ('mobile-shell-contracts-v1', 'contracts'),
                   ('mobile-shell-source-checks-v1', 'source-checks'),
                   ('mobile-shell-runtime-v1', 'runtime-v1'),
                   ('mobile-shell-runtime-v2', 'runtime-v2'),
                   ('mobile-shell-runtime-v3', 'runtime'),
                   ('mobile-shell-date-replay-v1', 'date-replay'),
                   ('mobile-shell-footer-replay-v1', 'footer-replay'),
                   ('mobile-shell-button-group-replay-v1', 'button-group-replay'),
                   ('mobile-shell-installed-smoke-v1', 'installed-smoke'),
                   ('mobile-shell-gallery-v1', 'gallery')]:
    source = BASE / name
    for path in sorted(source.iterdir()):
        if path.is_file():
            copy_file(path, TARGET / dest / path.name)
        elif path.name == 'implementation-inputs':
            copy_tree(path, TARGET / dest / path.name)
    if name in ['mobile-shell-runtime-preflight-v1', 'mobile-shell-runtime-preflight-v2']:
        output = source / 'output'
        if output.exists():
            copy_tree(output, TARGET / dest / 'output')
    if name.endswith('-replay-v1') or name in ['mobile-shell-installed-smoke-v1', 'mobile-shell-gallery-v1']:
        copy_tree(source / 'output', TARGET / dest / 'output')

failed = BASE / 'mobile-shell-runtime-v1/runtime/offscreen'
copy_tree(failed, TARGET / 'runtime-v1/offscreen')
previous = BASE / 'mobile-shell-runtime-v2/runtime'
copy_tree(previous / 'offscreen', TARGET / 'runtime-v2/offscreen')
copy_tree(previous / 'display-evidence', TARGET / 'runtime-v2/display')
runtime = BASE / 'mobile-shell-runtime-v3/runtime'
copy_tree(runtime / 'offscreen', TARGET / 'runtime/offscreen')
copy_tree(runtime / 'display-evidence', TARGET / 'runtime/display')
copy_file(runtime / 'check-mobile-shell-display.sh', TARGET / 'runtime/check-mobile-shell-display.sh')
copy_file(runtime / 'environment.json', TARGET / 'runtime/environment.json')
copy_tree(BASE / 'mobile-shell-compiled-v7/implementation-inputs', TARGET / 'implementation-inputs')
write('implementation-inputs.json', {
    str(p.relative_to(TARGET / 'implementation-inputs')): sha(p)
    for p in sorted((TARGET / 'implementation-inputs').rglob('*')) if p.is_file()})
runtime_result = json.loads((BASE / 'mobile-shell-runtime-v3/result.json').read_text())
write('result.json', dict(sourceProfiles=72, fullCoreTests=55, contractTests=792,
    installedSmokeCommands=43, bodyGeometryPassed=runtime_result['bodyGeometryPassed'],
    exactBodyImages=runtime_result['exactPixels'], sourceFreeContexts=8,
    virtualDisplayContexts=8, dateRegressionCaptures=437, footerRegressionCaptures=120,
    buttonGroupRegressionCaptures=184, sourcePinsChanged=False, expectedImagesChanged=False,
    physicalDisplay=False, readerAcceptance=False, accepted=False, fullMirrorAccepted=False))
copy_file(P / 'run.py', TARGET / 'collect.py')
write('files.json', dict(files={str(p.relative_to(TARGET)): sha(p)
    for p in sorted(TARGET.rglob('*')) if p.is_file()}))
print('Collected', TARGET, len(json.loads((TARGET/'files.json').read_text())['files']), 'members')
