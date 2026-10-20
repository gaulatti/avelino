#!/usr/bin/env python3
"""Verify the rebuilt divider package without accepting native visual parity."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/admin-divider-package-20261020'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'


def read(name):
    return json.loads((CAPSULE / name).read_text())


def digest(content):
    return hashlib.sha256(content).hexdigest()


def git_blobs(expressions):
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                            input=('\n'.join(expressions) + '\n').encode(), stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(result.stdout)
    for expression in expressions:
        header = stream.readline().split()
        assert len(header) == 3 and header[1] == b'blob', expression
        content = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        yield content
    assert not stream.read()


def verify_members():
    files = read('files.json')
    actual = {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p != CAPSULE / 'files.json'}
    assert set(files) == actual
    relative = CAPSULE.relative_to(ROOT)
    names = sorted({str(relative / n) for n in files} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(names), 'Every package capsule member must be in the Git index'
    for name, content in zip(names, git_blobs([':' + n for n in names]), strict=True):
        assert content == (ROOT / name).read_bytes(), name
        if name != str(relative / 'files.json'):
            assert digest(content) == files[str(Path(name).relative_to(relative))], name


def verify():
    verify_members()
    scope = read('scope.json')
    assert scope['reference'] == REFERENCE
    assert scope['compiledAdminTestsPerScale'] == 264 and scope['compiledMobileTestsPerScale'] == 40
    assert scope['scaleFactors'] == [1, 2] and scope['offscreenPackageContexts'] == 4
    assert scope['rawBodyCaptures'] == 320
    assert scope['incrementalCoreBuild'] and scope['apfsCloneOriginalPreserved'] and scope['freshIndependentConsumerBuild']
    assert scope['successfulSessionMatrixIncluded'] is False and scope['sessionMatrixLiveAtCapture'] is True
    for key in ['sourceProjectsMountedAtRuntime', 'productBuildMountedAtRuntime', 'nativeRasterAccepted', 'physicalInput', 'readerAcceptance', 'accepted']:
        assert scope[key] is False
    build, inputs = read('compiled/result.json'), read('compiled/inputs.json')
    revision = scope['sourceRevision']
    assert build['sourceRevision'] == inputs['sourceRevision'] == revision
    assert build['exitCode'] == 0 and build['sourceInputsUnchanged'] and build['incrementalCoreBuild'] and build['freshConsumerBuild']
    assert build['installedConsumerExecuted'] is build['accepted'] is False
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', revision], cwd=ROOT, text=True).splitlines()
    prefixes = tuple(n + '/' for n in ['src', 'samples', 'assets', 'tokens', 'tests', 'scripts', 'cmake', 'tools', 'evidence/geometry'])
    expected = {n for n in paths if n in ['CMakeLists.txt', 'CMakePresets.json'] or n.startswith(prefixes)}
    assert set(inputs['sourceFiles']) == expected
    for (name, checksum), content in zip(inputs['sourceFiles'].items(), git_blobs([revision + ':' + n for n in inputs['sourceFiles']]), strict=True):
        assert digest(content) == checksum, name
    commands = read('compiled/commands.json')
    assert [r['name'] for r in commands] == ['configure', 'build', 'admin-dpr1', 'mobile-dpr1', 'admin-dpr2', 'mobile-dpr2', 'install', 'consumer-configure', 'consumer-build']
    assert all(r['exitCode'] == 0 for r in commands)
    for scale in [1, 2]:
        for api, count in [('admin', 264), ('mobile', 40)]:
            assert f'Totals: {count} passed, 0 failed' in (CAPSULE / f'compiled/{api}-dpr{scale}.log').read_text()
    assert read('compiled/clone-audit.json')['cloneLibraryBytesIdentical'] is True
    preserved = read('compiled/preservation-audit.json')
    assert preserved['originalCoreBuildLibraryBytesUnchanged'] and preserved['originalPackageConsumerAndLibraryBytesUnchanged']
    artifacts = read('compiled/artifacts.json')
    native = json.loads(subprocess.check_output(['git', 'show', revision + ':tests/consumer/native-admin-shell-witnesses.json'], cwd=ROOT))
    profiles = {r['name']: r for r in native['profiles']}
    images = read('images.json'); assert len(images) == 320
    dimensions = {}
    for stored in {r['stored'] for r in images.values()}:
        path = CAPSULE / stored
        assert path.parent == CAPSULE / 'images' and digest(path.read_bytes()) == path.stem
        with Image.open(path) as image:
            image.load(); assert image.format == 'PNG'; dimensions[stored] = image.size
    assert len(dimensions) == scope['uniquePngBlobs']
    assert set(dimensions) == {str(p.relative_to(CAPSULE)) for p in (CAPSULE / 'images').glob('*.png')}
    for name, row in images.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert row['sha256'] == Path(row['stored']).stem and row['bytes'] == (CAPSULE / row['stored']).stat().st_size
    captures = set()
    for context in ['light-dpr1', 'dark-dpr1', 'light-dpr2', 'dark-dpr2']:
        command, report = read('runtime/' + context + '.json'), read('reports/' + context + '.json')
        assert command['sourceRevision'] == revision and command['exitCode'] == 0
        assert command['consumerSha256'] == artifacts['consumerSha256'] and command['librarySha256'] == artifacts['librarySha256']
        assert command['sourceProjectsMounted'] is command['productBuildMounted'] is command['accepted'] is False
        argv = command['command']; assert argv.count('-v') == 1 and argv[argv.index('-v') + 1].endswith('/admin-divider-compiled-v1/output/package:/package')
        assert 'test ! -e /work/src; test ! -e /work/CMakeLists.txt;' in argv[argv.index('bash') + 2]
        scale = 1 if context.endswith('1') else 2
        assert report['platform'] == 'offscreen' and report['dpr'] == scale and report['appearance'] == context.split('-')[0]
        assert report['nativeLayouts'] == len(report['layouts']) == 80
        assert report['nativeHistoryStates'] == sum(len(r['states']) for r in report['histories']) == 160
        assert report['nativeDividerCases'] == len(report['boundaries']) == 168
        assert report['qtAccessibilityInterfaces'] == 2 and report['qtToolbarPointerActions'] == 4
        assert report['qtCallerIdentityRetained'] and report['qtKeyboardActivation'] and report['qtShortcutActivation']
        for key in ['nativeToolbarEquivalentVerified', 'nativeKeyboardEquivalentVerified', 'nativeRasterAccepted', 'physicalInput', 'physicalDisplay', 'readerAcceptance', 'accepted']:
            assert report[key] is False
        assert {r['name'] for r in report['layouts']} == set(profiles)
        for row in report['layouts']:
            state = profiles[row['name']]['state']; assert all(row[k] == v for k, v in state.items() if k != 'step')
            captures.add(row['capture']); assert dimensions[images[row['capture']]['stored']] == (row['pixelWidth'], row['pixelHeight'])
        for row, expected_history in zip(report['histories'], native['histories'], strict=True):
            assert row['owner'] == expected_history['owner'] and row['initial'] == expected_history['initial'] and row['states'] == expected_history['states']
        for row, expected_boundary in zip(report['boundaries'], native['boundaries'], strict=True):
            assert all(row[k] == expected_boundary[k] for k in ['columnWidth', 'initial', 'requestedPosition'])
            pane = expected_boundary['after'][0]; state = row['actual']
            assert state['columnWidth'] == pane['width'] and state['displayedNavigation'] == (not pane['collapsed'])
            assert state['navigation'] == expected_boundary['navigation'] and state['requests'] == expected_boundary['requests']
    assert captures == set(images)
    print('Rebuilt divider: compiled 264+40 at both scales, fresh consumer, four source-absent contexts and 320 captures; native acceptance pending')


if __name__ == '__main__':
    verify()
