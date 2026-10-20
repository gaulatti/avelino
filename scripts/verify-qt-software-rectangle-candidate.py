#!/usr/bin/env python3
"""Decode the fractional-rectangle experiment; grant no mirror acceptance."""
import difflib
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/qt-fractional-rectangle-20261019'
NATIVE = ROOT / 'evidence/reference-investigations/mobile-shell-slots-20261019/run-v2/output'
PREVIOUS = ROOT / 'evidence/development/mobile-shell-20261019/runtime'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def difference(a, b):
    with Image.open(a) as x, Image.open(b) as y:
        x, y = x.convert('RGBA'), y.convert('RGBA')
        assert x.size == y.size, (a, b)
        delta = ImageChops.difference(x, y)
        mask = delta.getchannel('R')
        for channel in ['G', 'B', 'A']:
            mask = ImageChops.lighter(mask, delta.getchannel(channel))
        return x.width * x.height - mask.histogram()[0]


def verify():
    read = lambda name: json.loads((CAPSULE / name).read_text())
    manifest = read('files.json')
    actual = {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*')
              if p.is_file() and p != CAPSULE / 'files.json'}
    assert actual == set(manifest)
    for name, row in manifest.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        path = CAPSULE / name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name
    result = read('result.json')
    for key in ['canonicalToolchainIntegrated', 'productSdkChanged', 'physicalDisplay',
                'readerAcceptance', 'nativeAcceptance', 'accepted', 'fullMirrorAccepted']:
        assert result[key] is False
    assert result['fullCoreSuite'].startswith('running separately;')
    assert result['directRectangleControls'].startswith('prepared separately;')
    assert read('source-build/build-result.json')['exitCode'] == 0
    archive = read('source-build/archive-source-verification.json')
    assert archive['archiveSha256'] == '1f03a2b8f5588b4face7da87926e9b2c1372b3a32157c52df07a75067a9db1af'
    original = {
        'qsgsoftwareinternalrectanglenode.cpp': '521ae4ffc0a145c2de839b149873b2caa2718118eff603c4a47dd931e6251db2',
        'qsgsoftwareinternalrectanglenode_p.h': 'c9f8f2e22bf8a7501cc781d3411078312a5037a848b5c132c2bf6a5c160acb38',
    }
    applied = read('source-build/applied-patch.json')
    patch = CAPSULE / 'source-build/fractional-rectangle.patch'
    public_patch = ROOT / 'tools/qt-software-rectangle.patch'
    normalized = []
    for name in original:
        relative = 'src/quick/scenegraph/adaptations/software/' + name
        before_text = (CAPSULE / 'source-build/original' / name).read_text()
        after_text = (CAPSULE / 'source-build/patched' / name).read_text()
        normalized.extend(difflib.unified_diff(before_text.splitlines(True), after_text.splitlines(True),
                                             fromfile='a/' + relative, tofile='b/' + relative, n=0))
    assert public_patch.read_text() == ''.join(normalized)
    with tempfile.TemporaryDirectory() as temporary:
        target = Path(temporary) / 'src/quick/scenegraph/adaptations/software'
        target.mkdir(parents=True)
        for name, checksum in original.items():
            source = CAPSULE / 'source-build/original' / name
            assert digest(source) == checksum == archive['files'][name]['sha256']
            assert archive['files'][name]['originalMatchesArchive']
            (target / name).write_bytes(source.read_bytes())
        subprocess.run(['git', 'apply', '--check', str(patch)], cwd=temporary, check=True)
        subprocess.run(['git', 'apply', str(patch)], cwd=temporary, check=True)
        for name in original:
            assert (target / name).read_bytes() == (CAPSULE / 'source-build/patched' / name).read_bytes()
            assert digest(target / name) == applied['after'][name]
            (target / name).write_bytes((CAPSULE / 'source-build/original' / name).read_bytes())
        subprocess.run(['git', 'apply', '--unidiff-zero', str(public_patch)], cwd=temporary, check=True)
        for name in original:
            assert digest(target / name) == applied['after'][name]
    linux_patch = json.loads((CAPSULE / 'publication-checks/public-patch-linux.log').read_text())
    assert linux_patch['exitCode'] == 0 and linux_patch['gnuPatch']
    assert linux_patch['patchedSourceSha256'] == applied['after']
    assert linux_patch['compiledSourceBytesChanged'] is False
    assert read('publication-checks/public-patch-linux-command.json')['exitCode'] == 0
    assert read('sdk-v1/stage-result.json')['exitCode'] == 1
    assert 'QT_CONFIG' in (CAPSULE / 'sdk-v1/stage.log').read_text()
    stage, audit = read('sdk-v2/stage-result.json'), read('sdk-v2/immutable-audit-result.json')
    assert stage['exitCode'] == audit['exitCode'] == 0
    before = read('sdk-v2/sdk-before.json')
    after = read('sdk-v2/immutable-sdk-files.json')
    assert after == read('sdk-v2/sdk-after.json')
    old_sdk = json.loads((ROOT / 'evidence/development/qt-software-toolchain-20261019/sdk/actual-image-sdk.json').read_text())
    assert before == old_sdk['after']
    assert before.keys() == after.keys() and len(after) == result['sdkEntries'] == 9236
    changed = [name for name in before if before[name] != after[name]]
    assert changed == ['include/QtQuick/6.8.3/QtQuick/private/qsgsoftwareinternalrectanglenode_p.h',
                       'lib/libQt6Quick.so.6.8.3']
    assert changed == stage['changed'] == audit['changed']
    assert audit['unchangedEntries'] == 9234 and audit['actualImageSdkAudited']
    assert after[changed[0]]['sha256'] == applied['after']['qsgsoftwareinternalrectanglenode_p.h']
    assert after[changed[1]]['sha256'] == stage['installedQuickSha256']
    assert audit['imageId'] == result['imageId'] == read('sdk-v2/image.json')['imageId']
    assert audit['target'] == 'aarch64-linux-gnu' and audit['qt'] == '6.8.3'
    linkage = (CAPSULE / 'sdk-v2/immutable-linkage.log').read_text()
    assert all(value not in linkage for value in ['undefined symbol', 'not found', '/qt-build/'])
    assert 'libQt6Qml.so.6 => /opt/qt/lib/' in linkage
    features = read('sdk-v2/features.json')
    cache = dict(re.findall(r'^(QT_FEATURE_\w+):[^=]+=(ON|OFF)$',
                            (CAPSULE / 'sdk-v2/CMakeCache.txt').read_text(), re.M))
    assert len(features) == 7 and sum(len(row['sdk']) for row in features) == 49
    for row in features:
        assert row['matches'] and row['source'] == {k: cache[k] for k in row['sdk']}
        assert row['source'] == {k: 'ON' if v == '1' else 'OFF' for k, v in row['sdk'].items()}
    assert next(row['sdk']['QT_FEATURE_qml_jit'] for row in features if 'QT_FEATURE_qml_jit' in row['sdk']) == '1'
    for name, row in read('source-build/licenses.json').items():
        assert digest(CAPSULE / 'source-build/licenses' / name) == row['sha256']

    inputs = read('runtime/inputs.json')
    previous_inputs = json.loads((PREVIOUS / 'inputs.json').read_text())
    assert inputs['sourceFiles'] == previous_inputs['sourceFiles']
    assert inputs['runtimePackageFiles'] == previous_inputs['runtimePackageFiles']
    assert inputs['imageId'] == audit['imageId']
    assert all(r['exitCode'] == 0 for r in read('runtime/commands.json'))
    source = {r['name']: r for r in json.loads((NATIVE / 'measurements.json').read_text())['profiles']}
    previous = {(r['context'], r['profile']): r for r in json.loads((PREVIOUS / 'comparison.json').read_text())['rows']}
    rows = read('runtime/comparison.json')['rows']
    exact = old_exact = improved = regressed = identical = 0
    assert len(rows) == 144
    for row in rows:
        baseline = previous[(row['context'], row['profile'])]
        native = NATIVE / row['source']
        before_png = PREVIOUS / 'offscreen' / baseline['capture']
        after_png = CAPSULE / 'runtime/offscreen' / row['capture']
        assert digest(native) == row['sourceSha256'] == baseline['sourceSha256']
        assert digest(before_png) == baseline['sha256'] and digest(after_png) == row['sha256']
        a, b = difference(native, before_png), difference(native, after_png)
        assert a == baseline['changedPixels'] and b == row['changedPixels']
        exact += b == 0
        old_exact += a == 0
        improved += b < a
        regressed += b > a
        identical += before_png.read_bytes() == after_png.read_bytes()
        report = read('runtime/offscreen/' + row['context'] + '.json')
        layout = next(r for r in report['layouts'] if r['name'] == row['profile'])
        assert layout['geometryPassed'] and layout['frames'] == source[row['profile']]['frames']
        assert report['qtFocusScope'] and report['qtTabFocusEntries'] == 1
        viewport = layout['captureViewport']
        assert viewport['x'] == viewport['y'] == 0
        with Image.open(CAPSULE / 'runtime/offscreen' / layout['overscanCapture']) as raw, Image.open(after_png) as retained:
            assert raw.width >= viewport['width'] and raw.height >= viewport['height']
            part = raw.crop((0, 0, viewport['width'], viewport['height']))
            assert part.size == retained.size and part.convert('RGBA').tobytes() == retained.convert('RGBA').tobytes()
    assert (old_exact, exact, improved, regressed, identical) == (76, 80, 8, 0, 136)
    assert {row['context'] for row in rows} == {f'{theme}-text{scale}-dpr{dpr}' for theme, scale, dpr in
        itertools.product(['light', 'dark'], ['1', '1.5'], [1, 2])}
    runtime = read('runtime/result.json')
    assert runtime['exitCode'] == 0 and runtime['bodyCaptures'] == runtime['bodyGeometryPassed'] == 144
    assert runtime['exactPixels'] == 80 and runtime['virtualDisplayContexts'] == 8
    display = CAPSULE / 'runtime/display-evidence'
    sessions = list(display.glob('mobile-shell-*.json'))
    assert len(sessions) == 8
    assert {tuple(p.stem.removeprefix('mobile-shell-').split('-')) for p in sessions} == set(
        itertools.product(['xcb', 'wayland'], ['software', 'opengl'], ['standard', 'scaled']))
    for path in sessions:
        row = json.loads(path.read_text())
        assert row['structuralChecks'] == 'passed' and row['nativeStateChecks'] == 25
        assert row['qtFocusScope'] and row['qtTabFocusEntries'] == 1
        assert row['physicalDisplay'] is row['hardwareAcceleration'] is False
        assert digest(path.with_suffix('.png')) == row['windowCaptureSha256']
        assert digest(display / row['sessionCapture']) == row['sessionCaptureSha256']
    spec = importlib.util.spec_from_file_location('opacity_controls', ROOT / 'scripts/verify-qt-software-source-patch.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.CAPSULE = CAPSULE / 'opacity'
    assert module.profiles('patched-regression', {name: 0 for name in
        ['xcb-dpr1', 'xcb-dpr2', 'wayland-dpr1', 'wayland-dpr2']}) == (120, 12, 0)
    print('Fractional rectangle candidate:2 SDK entries,49 features;144 native body layouts,80 exact images vs76;8 improved,0 regressed,136 unchanged;8 virtual displays;120 opacity and12 Canvas frames; canonical integration and mirror acceptance pending')


if __name__ == '__main__':
    verify()
