from pathlib import Path
import hashlib
import itertools
import json
import subprocess

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
RUNTIME = P.parent / 'mobile-shell-runtime-v3/runtime'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
commands, captures = [], []


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
    write('inputs.json', dict(sourceFree=True, producer='mobile-shell-compiled-v7',
        packageFiles=inputs['runtimePackageFiles'], nativeToolbarRasterAccepted=False, accepted=False))
    for dark, dpr in itertools.product([False, True], [1, 2]):
        name = ('dark' if dark else 'light') + '-dpr' + str(dpr) + '.png'
        command = ['docker', '--context', 'colima-avelino-verify', 'run', '--init', '--rm',
            '--ulimit', 'core=0', '-v', str(RUNTIME) + ':/package:ro',
            '-v', str(output) + ':/extra', '-w', '/package',
            '-e', 'QT_QPA_PLATFORM=offscreen', '-e', 'QT_QUICK_BACKEND=software',
            '-e', 'QT_SCALE_FACTOR=' + str(dpr),
            'sha256:e29f85ab0df39f3ae46c4d5ddcc075517701fc05359a230c8647b1174e862dd3',
            './install/bin/AvelinoCatalog', '--fixture', 'mobile-shell', '--capture', '/extra/' + name]
        if dark:
            command.append('--dark')
        with (P / (name + '.log')).open('x') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        commands.append(dict(command=command, exitCode=result.returncode))
        write('commands.json', commands)
        assert result.returncode == 0, name
        metadata = json.loads((output / (name + '.json')).read_text())
        assert metadata['qt'] == '6.8.3' and metadata['platform'] == 'offscreen'
        assert metadata['width'] == 1120 and metadata['height'] == 780 and metadata['dpr'] == dpr
        snapshot = metadata['mobileShell']
        assert snapshot['toolbarVisible'] is True and snapshot['toolbarCount'] == 2
        assert snapshot['frames']['component'] == dict(x=0, y=0, width=360, height=240)
        captures.append(dict(path=name, sha256=sha(output / name),
                             metadataSha256=sha(output / (name + '.json'))))
        print('gallery', name, 'passed', flush=True)
    assert all(sha(RUNTIME / n) == h for n, h in inputs['runtimePackageFiles'].items())
    write('result.json', dict(exitCode=0, captures=captures, sourceFree=True,
        scope='startup and capture; operator interaction and native toolbar acceptance remain pending',
        nativeToolbarRasterAccepted=False, physicalDisplay=False, accepted=False, fullMirrorAccepted=False))
except BaseException as error:
    write('result.json', dict(exitCode=1, error=repr(error), accepted=False))
    raise
