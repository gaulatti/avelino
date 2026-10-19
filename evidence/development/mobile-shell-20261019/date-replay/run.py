from pathlib import Path
import hashlib
import json
import subprocess
import time

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
SOURCE = P.parent / 'mobile-shell-runtime-v3'
DOCKER = ['docker', '--context', 'colima-avelino-verify']
steps = []
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def write(name, value):
    (P / name).write_text(json.dumps(value, indent=2) + '\n')


def run(name, command):
    write('phase.json', dict(phase=name, startedAt=time.time()))
    started = time.monotonic()
    with (P / (name + '.log')).open('x') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    steps.append(dict(name=name, command=command, exitCode=result.returncode,
                      seconds=time.monotonic() - started))
    write('commands.json', steps)
    print(name, result.returncode, flush=True)
    assert result.returncode == 0, (name, result.returncode)


try:
    previous = json.loads((SOURCE / 'result.json').read_text())
    assert previous['exitCode'] == 0 and previous['sourceFreeContexts'] == 8
    image_id = 'sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3'
    runtime = SOURCE / 'runtime'
    source_inputs = json.loads((SOURCE / 'inputs.json').read_text())
    inputs = dict(consumerSha256=sha(runtime/'consumer-build/InstalledConsumer'),
        freshConsumerCompilationProducer='mobile-shell-compiled-v7',
        packageFiles=source_inputs['runtimePackageFiles'])
    assert all(sha(runtime/name)==value for name,value in inputs['packageFiles'].items())
    consumer_files = {str(p.relative_to(ROOT/'tests/consumer')):sha(p)
                      for p in sorted((ROOT/'tests/consumer').rglob('*')) if p.is_file()}
    spec = dict(consumerFiles=consumer_files)
    output = P / 'output'; output.mkdir()
    write('inputs.json', dict(imageId=image_id, consumerSha256=inputs['consumerSha256'],
        freshConsumerCompilationProducer=inputs['freshConsumerCompilationProducer'],
        consumerFiles=spec['consumerFiles'], sourceRuntime=SOURCE.name,
        sourceProjectsMounted=False, fullMirrorAccepted=False))
    base = DOCKER + ['run', '--init', '--rm', '--ulimit', 'core=0',
        '-v', str(runtime) + ':/package:ro', '-v', str(output) + ':/extra-output',
        '-w', '/package', '-e', 'QT_QPA_PLATFORM=offscreen', '-e', 'QT_QUICK_BACKEND=software']
    absence = '''from pathlib import Path
work=Path('/work')
assert not work.exists() or (work.is_dir() and not any(work.iterdir()))
assert not any(Path(p).exists() for p in ['/work/src/Avelino','/work/CMakeLists.txt','/work/build',
 '/consumer-check','/package/consumer','/package/src','/package/build',
 '/package/consumer-build/CMakeCache.txt','/Users/gaulatti/source/gaulatti/avelino'])
'''
    for group in ['navigation', 'date', 'gallery']:
        for dark in [False, True]:
            for scale in [1, 1.5]:
                for dpr in [1, 2]:
                    context = f'{"dark" if dark else "light"}-text{scale:g}-dpr{dpr}'
                    name = ('' if group == 'date' else group + '-') + context
                    prefix = '/extra-output/' + name
                    arguments = ['./consumer-build/InstalledConsumer', '--text-scale', str(scale)]
                    if dark: arguments += ['--dark']
                    if group == 'navigation':
                        arguments += ['--navigation', '--evidence', prefix]
                        startup = absence + '''import json,subprocess,time
arguments=ARGS
prefix=PREFIX
child=subprocess.Popen(arguments)
while child.poll() is None and not Path(prefix+'.json').exists():time.sleep(0.02)
if Path(prefix+'.json').exists():
 json.loads(Path(prefix+'.json').read_text());assert Path(prefix+'.png').exists()
 Path(prefix+'.captured').touch()
raise SystemExit(child.wait())
'''.replace('ARGS', repr(arguments)).replace('PREFIX', repr(prefix))
                    else:
                        arguments += ['--date-range', '--date-range-report', prefix,
                                      '--date-range-observe' if group == 'date' else '--date-range-gallery']
                        startup = absence + 'import os\nos.execv("./consumer-build/InstalledConsumer",' + repr(arguments) + ')\n'
                    run(name, base + ['-e', 'QT_SCALE_FACTOR=' + str(dpr), image_id,
                                      'python3', '-c', startup])
    parent = ROOT / 'evidence/development/date-range-fields-20261018'
    expected = [(r['fixture'], r['candidateSHA256'])
                for r in json.loads((parent / 'strict/comparison.json').read_text())['results']]
    expected += [(r['candidateName'], r['candidateSHA256'])
                 for r in json.loads((parent / 'chinese-comparison.json').read_text())['results']]
    assert len(expected) == 437 and len({name for name, value in expected}) == 437
    rows = [dict(path=name, expected=value, actual=sha(output / name),
                 identical=value == sha(output / name)) for name, value in expected]
    write('raw-image-comparison.json', dict(count=437, identical=sum(r['identical'] for r in rows),
        rows=rows, parentManifestSha256=sha(parent / 'files.json'), fullMirrorAccepted=False))
    assert all(r['identical'] for r in rows), [r for r in rows if not r['identical']][:3]
    profiles = []
    for f in output.glob('*.json'):
        record = json.loads(f.read_text())
        if record.get('fixture') != 'date-range' or not record.get('closed'):
            continue
        literal = record['literalInput']
        assert len(literal) == 16 and all(r['samePixels'] and r['before'] == r['after'] for r in literal)
        assert sum(r['nativeValueCompared'] for r in literal) == 8
        assert record['accepted'] is False
        profiles.append(dict(path=f.name, literalChecks=16, nativeValueComparisons=8, sha256=sha(f)))
    assert len(profiles) == 8
    write('literal-validation.json', dict(profiles=profiles, checks=128, nativeValueComparisons=64,
        initialFieldAcceptance='pending', rtlGlyphAcceptance='pending', fullMirrorAccepted=False))
    assert all(sha(runtime / name) == value for name, value in inputs['packageFiles'].items())
    write('result.json', dict(exitCode=0, imageId=image_id, navigationContexts=8, dateContexts=8,
        galleryContexts=8, coldCaptures=437, coldByteIdentical=437, literalChecks=128,
        nativeValueComparisons=64, sourceProjectsMounted=False, consumerRecompiledDuringReplay=False,
        freshConsumerCompilationProducer=inputs['freshConsumerCompilationProducer'],
        physicalDisplay=False, nativeAcceptance=False, fullMirrorAccepted=False))
    write('phase.json', dict(phase='complete', finishedAt=time.time()))
except BaseException as error:
    write('result.json', dict(exitCode=1, error=repr(error), fullMirrorAccepted=False))
    raise
