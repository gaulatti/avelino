from pathlib import Path
import hashlib
import json
import subprocess
import time

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
RUNTIME = P.parent / 'mobile-shell-runtime-v3/runtime'
NATIVE = ROOT / 'evidence/reference-investigations/button-group-slots-20261019'
PREVIOUS = ROOT / 'evidence/development/button-group-layout-20261019'
IMAGE = 'sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
commands, comparisons = [], []


def write(name, value):
    temporary = P / (name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(P / name)


try:
    assert json.loads((RUNTIME.parent / 'result.json').read_text())['exitCode'] == 0
    inputs = json.loads((RUNTIME.parent / 'inputs.json').read_text())
    assert all(sha(RUNTIME / n) == h for n, h in inputs['runtimePackageFiles'].items())
    output = P / 'output'
    output.mkdir()
    rows = json.loads((NATIVE / 'captures.json').read_text())['captures']
    definitions = json.loads((NATIVE / 'fixtures.json').read_text())
    for definition in definitions['fixtures']:
        frames = [r['frames']['component'] for r in rows if r['variant'] == definition['variant']]
        flags = {f['width'] == 0 or f['height'] == 0 for f in frames}
        assert len(frames) == 8 and len(flags) == 1
        definition['expectedEmpty'] = flags.pop()
    (output / 'fixtures.json').write_text(json.dumps(definitions, indent=2) + '\n')
    write('inputs.json', dict(imageId=IMAGE, sourceFree=True,
        producer='mobile-shell-compiled-v7', sourcePackageFiles=inputs['runtimePackageFiles'],
        previousManifestSha256=sha(PREVIOUS / 'files.json'), accepted=False))
    for i, row in enumerate(rows):
        name = Path(row['path']).name
        command = ['docker', '--context', 'colima-avelino-verify', 'run', '--init', '--rm',
            '--ulimit', 'core=0', '-v', str(RUNTIME) + ':/package:ro',
            '-v', str(output) + ':/extra', '-w', '/package', '-e', 'QT_QPA_PLATFORM=offscreen',
            '-e', 'QT_QUICK_BACKEND=software', '-e', 'QT_SCALE_FACTOR=' + str(row['dpr']),
            IMAGE, './install/bin/AvelinoCatalog', '--fixture', 'reference-case',
            '--case', row['fixture'], '--case-definitions', '/extra/fixtures.json',
            '--text-scale', str(row['textScale']), '--capture', '/extra/' + name]
        if row['appearance'] == 'dark':
            command.append('--dark')
        write('phase.json', dict(phase='catalog', index=i, total=len(rows), startedAt=time.time()))
        with (P / ('catalog-' + str(i).zfill(3) + '.log')).open('x') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        commands.append(dict(command=command, exitCode=result.returncode))
        write('commands.json', commands)
        assert result.returncode == 0, (name, result.returncode)
        capture = output / name
        old = PREVIOUS / 'runtime/captures' / name
        metadata = json.loads(Path(str(capture) + '.json').read_text())
        actual = metadata['buttonGroupFrames']
        geometry = all(actual[n][axis] == value for n, frame in row['frames'].items()
                       if n in {'component', 'first', 'second'} for axis, value in frame.items())
        labels = all(actual[n][axis] == value for n, frame in row['frames'].items()
                     if n.endswith('Text') for axis, value in frame.items())
        identical = capture.read_bytes() == old.read_bytes()
        comparisons.append(dict(path=name, expected=sha(old), actual=sha(capture),
            byteIdentical=identical, geometryPassed=geometry, labelGeometryPassed=labels,
            metadataSha256=sha(Path(str(capture) + '.json'))))
        write('comparison.json', dict(rows=comparisons, accepted=False))
        assert identical and geometry, comparisons[-1]
        if (i + 1) % 24 == 0:
            print('button group captures', i + 1, flush=True)
    assert len(comparisons) == 184
    assert all(sha(RUNTIME / n) == h for n, h in inputs['runtimePackageFiles'].items())
    write('result.json', dict(exitCode=0, captures=184, byteIdentical=184,
        geometryPassed=184, labelGeometryPassed=sum(r['labelGeometryPassed'] for r in comparisons),
        sourceFree=True, sourcePackageUnchanged=True, physicalDisplay=False,
        accepted=False, fullMirrorAccepted=False))
    write('phase.json', dict(phase='complete', finishedAt=time.time()))
except BaseException as error:
    write('result.json', dict(exitCode=1, error=repr(error), accepted=False))
    raise
