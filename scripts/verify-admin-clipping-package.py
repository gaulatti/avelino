#!/usr/bin/env python3
"""Verify the compiled clipping package and retained virtual runs; native gates stay open."""
import hashlib
import importlib.util
import io
import itertools
import json
from pathlib import Path
import re
import subprocess
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / 'evidence/development/admin-clipping-package-20261020'
MODULE = '7253695c3e94b0626bcb0612fbc8467fe94445b5'
HARNESS = '043352da9b7879e50526bbb4b9c652bdc9374264'


def read(name):
    return json.loads((CAP / name).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blobs(expressions):
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT, check=True,
                            input=('\n'.join(expressions) + '\n').encode(), stdout=subprocess.PIPE)
    stream = io.BytesIO(result.stdout)
    for expression in expressions:
        header = stream.readline().split()
        assert len(header) == 3 and header[1] == b'blob', expression
        content = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        yield content
    assert not stream.read()


def historical(revision, name):
    return next(blobs([revision + ':' + name]))


def verify_members():
    files = read('files.json')
    actual = {str(p.relative_to(CAP)) for p in CAP.rglob('*') if p.is_file() and p != CAP / 'files.json'}
    assert set(files) == actual
    relative = CAP.relative_to(ROOT)
    names = sorted({str(relative / n) for n in files} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(names), 'Every clipping-package member must be in the Git index'
    for name, raw in zip(names, blobs([':' + n for n in names]), strict=True):
        assert raw == (ROOT / name).read_bytes(), name
        if name != str(relative / 'files.json'):
            assert sha(raw) == files[str(Path(name).relative_to(relative))], name


def verify():
    verify_members()
    scope = read('scope.json')
    assert scope['moduleSourceRevision'] == MODULE and scope['testHarnessRevision'] == HARNESS
    assert (scope['compiledAdminTestsPerScale'], scope['compiledMobileTestsPerScale']) == (266, 40)
    assert (scope['offscreenConsumerContexts'], scope['fixedInstalledModuleDisplayContexts'], scope['consumerDisplayContexts']) == (4, 8, 8)
    tree = subprocess.check_output(['git', 'rev-parse', HARNESS + '^{tree}'], cwd=ROOT, text=True).strip()
    assert tree == scope['testHarnessStagedTree']
    assert subprocess.run(['git', 'diff', '--quiet', MODULE, HARNESS, '--', 'src', 'samples', 'assets',
                           'tokens', 'tests/consumer', 'cmake', 'tools', 'CMakeLists.txt', 'CMakePresets.json'], cwd=ROOT).returncode == 0
    for key in ['sourceProjectsMounted', 'productBuildMounted', 'librarySourceOverlayProvided',
                'libraryQmldirModified', 'imageBytesConverted', 'expectedImagesChanged', 'nativeRasterAccepted',
                'physicalInput', 'physicalDisplay', 'hardwareAcceleration', 'readerAcceptance', 'iccConversionReviewed', 'accepted']:
        assert scope[key] is False
    build, inputs = read('compiled/result.json'), read('compiled/inputs.json')
    assert build['sourceRevision'] == inputs['sourceRevision'] == MODULE and build['exitCode'] == 0
    assert build['sourceInputsUnchanged'] and build['freshConsumerBuild'] and build['incrementalCoreBuild']
    assert build['installedConsumerExecuted'] is build['accepted'] is False
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', MODULE], cwd=ROOT, text=True).splitlines()
    prefixes = tuple(n + '/' for n in ['src', 'samples', 'assets', 'tokens', 'tests', 'scripts', 'cmake', 'tools', 'evidence/geometry'])
    expected = {n for n in paths if n in ['CMakeLists.txt', 'CMakePresets.json'] or n.startswith(prefixes)}
    assert set(inputs['sourceFiles']) == expected and len(expected) == scope['frozenSourceInputs'] == 868
    for (name, digest), raw in zip(inputs['sourceFiles'].items(), blobs([MODULE + ':' + n for n in inputs['sourceFiles']]), strict=True):
        assert sha(raw) == digest, name
    commands = read('compiled/commands.json')
    assert [r['name'] for r in commands] == ['configure', 'build', 'admin-dpr1', 'mobile-dpr1', 'admin-dpr2', 'mobile-dpr2', 'install', 'consumer-configure', 'consumer-build']
    assert all(r['exitCode'] == 0 for r in commands)
    for api, count in [('admin', 266), ('mobile', 40)]:
        for scale in [1, 2]:
            assert f'Totals: {count} passed, 0 failed, 0 skipped, 0 blacklisted' in (CAP / f'compiled/{api}-dpr{scale}.log').read_text()
    audit, clone, artifacts = read('compiled/completion-audit.json'), read('compiled/clone-inputs.json'), read('compiled/artifacts.json')
    assert audit['sourceRevision'] == MODULE and audit['sourceInputsRechecked'] == 868
    assert audit['sourceInputsUnchanged'] and audit['originalCriticalArtifactsUnchanged']
    assert audit['preservedOriginalArtifactHashes'] == clone['originalArtifactHashes'] and len(clone['originalArtifactHashes']) == 4
    assert artifacts['consumerSha256'] == audit['currentArtifactHashes']['package/consumer-build/InstalledConsumer']
    assert artifacts['librarySha256'] == audit['currentArtifactHashes']['package/install/lib/qml/Avelino/libAvelino.so']
    images = read('images.json'); dimensions = {}
    assert len(images) == scope['rawImageAliases']
    for stored in {r['stored'] for r in images.values()}:
        path = CAP / stored
        assert path.parent == CAP / 'images' and sha(path.read_bytes()) == path.stem
        with Image.open(path) as image:
            image.load(); assert image.format == 'PNG'; dimensions[stored] = image.size
    assert len(dimensions) == scope['uniquePngBlobs']
    assert set(dimensions) == {str(p.relative_to(CAP)) for p in (CAP / 'images').glob('*.png')}
    for name, row in images.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert row['sha256'] == Path(row['stored']).stem and row['bytes'] == (CAP / row['stored']).stat().st_size
    used = set()
    def use(name):
        used.add(name)
        return CAP / images[name]['stored']
    native = json.loads(historical(MODULE, 'tests/consumer/native-admin-shell-witnesses.json'))
    profiles = {r['name']:r for r in native['profiles']}
    def report_checks(report, prefix):
        assert report['reference'] == native['reference'] and report['qt'] == '6.8.3'
        assert report['nativeLayouts'] == len(report['layouts']) == 80
        assert report['nativeHistoryStates'] == sum(len(h['states']) for h in report['histories']) == 160
        assert report['nativeDividerCases'] == len(report['boundaries']) == 168
        assert report['qtCallerIdentityRetained'] and report['qtKeyboardActivation'] and report['qtShortcutActivation']
        assert report['qtToolbarPointerActions'] == 4 and report['qtAccessibilityInterfaces'] == 2
        for key in ['nativeToolbarEquivalentVerified', 'nativeKeyboardEquivalentVerified', 'nativeRasterAccepted',
                    'physicalInput', 'physicalDisplay', 'readerAcceptance', 'accepted']:
            assert report[key] is False
        assert {r['name'] for r in report['layouts']} == set(profiles)
        for row in report['layouts']:
            state = profiles[row['name']]['state']
            assert all(row[k] == v for k,v in state.items() if k != 'step')
            use(prefix + row['capture'])
            assert dimensions[images[prefix + row['capture']]['stored']] == (row['pixelWidth'], row['pixelHeight'])
        for row, expected_history in zip(report['histories'], native['histories'], strict=True):
            assert all(row[k] == expected_history[k] for k in ['owner', 'initial', 'states'])
        for row, expected_boundary in zip(report['boundaries'], native['boundaries'], strict=True):
            assert all(row[k] == expected_boundary[k] for k in ['columnWidth', 'initial', 'requestedPosition'])
            pane, actual = expected_boundary['after'][0], row['actual']
            assert actual['columnWidth'] == pane['width'] and actual['displayedNavigation'] == (not pane['collapsed'])
            assert actual['navigation'] == expected_boundary['navigation'] and actual['requests'] == expected_boundary['requests']
    contexts = ['light-dpr1', 'dark-dpr1', 'light-dpr2', 'dark-dpr2']
    for context in contexts:
        receipt, report = read('offscreen/' + context + '.json'), read('reports/' + context + '.json')
        assert receipt['exitCode'] == 0 and receipt['sourceRevision'] == MODULE
        assert receipt['librarySha256'] == artifacts['librarySha256'] and receipt['consumerSha256'] == artifacts['consumerSha256']
        assert receipt['sourceProjectsMounted'] is receipt['productBuildMounted'] is False
        assert receipt['command'].count('-v') == 1 and '/admin-clipping-compiled-v1/output/package:/package' in receipt['command'][receipt['command'].index('-v') + 1]
        assert report['platform'] == 'offscreen' and report['dpr'] == int(context[-1]) and report['appearance'] == context.split('-')[0]
        report_checks(report, 'offscreen/')
    comparison = read('offscreen/body-comparison.json')
    assert comparison['sourceRevision'] == MODULE and comparison['contexts'] == 4
    assert comparison['rawBodyCaptures'] == comparison['byteIdenticalToPrior'] == 320
    prior_path = 'evidence/development/admin-source-colour-package-20261020/'
    prior = json.loads(historical(MODULE, prior_path + 'images.json'))
    for row in comparison['comparisons']:
        name = row['capture']; assert row['bytesIdentical'] is True
        assert row['sha256'] == row['priorSha256'] == images['offscreen/' + name]['sha256'] == prior[name]['sha256']
        assert use('offscreen/' + name).read_bytes() == historical(MODULE, prior_path + prior[name]['stored'])
    def module_test(folder, name, scale, harness, image_prefix, passed=True):
        receipt = read(folder + name + '.json'); log = (CAP / (folder + name + '.log')).read_text()
        assert receipt['exitCode'] == (0 if passed else 1) and receipt['sourceRevision'] == MODULE
        assert receipt['librarySha256'] == artifacts['librarySha256'] and artifacts['librarySha256'] in log
        argv = receipt['command']
        assert argv.count('-v') == 2
        assert argv[argv.index('-v') + 1].endswith('/admin-clipping-compiled-v1/output/package/install:/avelino:ro')
        assert 'test ! -e /work/src;' in argv[-1] and '-import /avelino/lib/qml' in argv[-1]
        assert '/overlay' not in argv[-1] and 'sed ' not in argv[-1]
        for key in ['sourceProjectsMounted', 'productBuildMounted', 'librarySourceOverlayProvided', 'libraryQmldirModified', 'nativeRasterAccepted', 'accepted']:
            assert receipt[key] is False
        assert ('266 passed, 0 failed' if passed else '265 passed, 1 failed') in log
        original = {}
        for path, digest in receipt['sourceInputHashes'].items():
            revision = harness if path == 'tests/components/tst_admin_shell.qml' else MODULE
            original[path] = historical(revision, path); assert sha(original[path]) == digest
        assert all(n.startswith('tests/') for n in original)
        payload = dict(original)
        payload['tests/components/witnesses.js'] = b'var data = ' + original['tests/consumer/native-admin-shell-witnesses.json'] + b';\n'
        path = 'tests/components/tst_admin_shell.qml'
        text = payload[path].decode().replace('import QtTest', 'import QtTest\nimport "witnesses.js" as Native', 1).replace('    id: root', '    id: root\n    property var nativeAdminShellWitnesses: Native.data', 1)
        text = text.replace('            const after = grabImage(host)', '            const after = grabImage(host)\n            before.save("/evidence/' + name + '-before.png"); after.save("/evidence/' + name + '-after.png")', 1)
        payload[path] = text.encode(); assert {n:sha(b) for n,b in payload.items()} == receipt['executedPayloadHashes']
        a, b = [Image.open(use(image_prefix + phase + '.png')).convert('RGBA') for phase in ['before', 'after']]
        for x, y in [[10, 10], [15, 100], [405, 100], [210, 230]]:
            assert a.getpixel((x * scale, y * scale)) == b.getpixel((x * scale, y * scale))
        assert b.getpixel((285 * scale, 40 * scale)) == (255, 255, 0, 255)
        return receipt, log
    for scale in [1, 2]:
        module_test('module-tests/offscreen/', f'dpr{scale}', scale, MODULE, f'module-tests/offscreen-dpr{scale}-')
    for protocol, backend, scale in itertools.product(['xcb', 'wayland'], ['software', 'opengl'], [1, 2]):
        name = f'{protocol}-{backend}-dpr{scale}'
        receipt, log = module_test('module-tests/fixed/', name, scale, HARNESS, 'module-tests/fixed-' + name + '-')
        assert receipt['testHarnessStagedTree'] == tree and receipt['platform'] == protocol and receipt['backend'] == backend
        if backend == 'opengl': assert 'Mesa RENDERER: llvmpipe' in log
        if protocol == 'xcb' or (backend == 'software' and scale == 1):
            earlier, _ = module_test('module-tests/earlier/', name, scale, MODULE, 'module-tests/earlier-' + name + '-', protocol == 'xcb')
            if protocol == 'wayland':
                failure = (CAP / ('module-tests/earlier/' + name + '.log')).read_text()
                assert 'Actual   (): 0' in failure and 'Expected (): 180' in failure
    stopped = read('module-tests/earlier-pipeline/result.json')
    assert stopped['exitCode'] == 1 and stopped['failedPhase'] == 'installed-test-matrix'
    assert len(read('module-tests/earlier-pipeline/commands.json')) == 1
    diagnostic = (CAP / 'module-tests/diagnostic/wayland-software-dpr1.log').read_text()
    diagnostic_receipt = read('module-tests/diagnostic/wayland-software-dpr1.json')
    assert diagnostic_receipt['diagnosticOnly'] and diagnostic_receipt['waitForPolishObservationAdded']
    assert diagnostic_receipt['librarySha256'] == artifacts['librarySha256']
    observations = {}
    for label in ['SETTLE_CREATED', 'SETTLE_POLISHED']:
        line = next(s for s in diagnostic.splitlines() if label in s)
        observations[label] = json.loads(line[line.index('{'):])
    assert observations['SETTLE_CREATED']['frames']['content']['width'] == 0
    assert observations['SETTLE_POLISHED']['frames']['content']['width'] == 180
    assert observations['SETTLE_CREATED']['requests'] == observations['SETTLE_POLISHED']['requests']
    assert 'verify-admin-sidebar-background.py' in (CAP / 'ci/725-references-failed.log').read_text()
    strict, bindings = read('strict/result.json'), read('strict/image-bindings.json')
    assert strict['sourceRevision'] == MODULE and strict['comparisonExitCode'] == 1
    assert strict['comparisonStatus'] == 'failed' and strict['comparedFixtures'] == strict['iccPolicyRefusals'] == 80
    assert strict['imageBytesConverted'] is strict['nativeRasterAccepted'] is strict['accepted'] is False
    comparator = ROOT / 'scripts/compare-captures.py'
    assert next(blobs([':scripts/compare-captures.py'])) == comparator.read_bytes()
    assert sha(comparator.read_bytes()) == strict['comparatorSha256'] == sha(historical(MODULE, 'scripts/compare-captures.py'))
    reference_path = 'evidence/reference-investigations/admin-shell-pinned-matrix-20261020/'
    reference_index = json.loads(historical(MODULE, reference_path + 'images.json'))
    manifest = read('strict/reference-captures.json'); assert len(bindings) == len(manifest['captures']) == 80
    by_name = {r['profile']:r for r in bindings}
    actual_report = read('reports/light-dpr2.json')
    actual_layouts = {r['name']:r for r in actual_report['layouts']}
    with tempfile.TemporaryDirectory(prefix='avelino-clipping-compare-') as folder:
        folder = Path(folder); expected_dir, candidate_dir = folder / 'reference', folder / 'candidate'
        expected_dir.mkdir(); candidate_dir.mkdir()
        for fixture in manifest['captures']:
            name = Path(fixture['path']).stem; row = by_name[name]
            assert fixture['sha256'] == row['nativeSha256'] == reference_index[row['nativeAlias']]['sha256']
            expected = historical(MODULE, reference_path + reference_index[row['nativeAlias']]['stored'])
            assert sha(expected) == fixture['sha256']; (expected_dir / fixture['path']).write_bytes(expected)
            actual = use('offscreen/' + row['packageCapture']).read_bytes(); assert sha(actual) == row['candidateSha256']
            (candidate_dir / fixture['path']).write_bytes(actual)
            metadata = (CAP / 'strict/metadata' / (fixture['path'] + '.json')).read_bytes()
            measured = actual_layouts[name]; frame = measured['frames']['root']
            expected_metadata = {
                'width': measured['pixelWidth'] / actual_report['dpr'],
                'height': measured['pixelHeight'] / actual_report['dpr'],
                'dpr': actual_report['dpr'], 'textScale': actual_report['textScale'],
                'fixture': name, 'appearance': 'dark' if profiles[name]['dark'] else 'light',
                'api': 'BleeckerAdminShell', 'state': {'navigationPresented': measured['navigation']},
                'componentSize': {'width': frame['width'], 'height': frame['height']},
            }
            supplied = json.loads(metadata)
            assert all(supplied[k] == v == fixture[k] for k,v in expected_metadata.items())
            assert fixture['source'] == native['reference']
            (candidate_dir / (fixture['path'] + '.json')).write_bytes(metadata)
        (expected_dir / 'captures.json').write_text(json.dumps(manifest))
        spec = importlib.util.spec_from_file_location('strict_clipping_comparator', comparator)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        assert module.compare(expected_dir, candidate_dir, folder / 'output') == 1
        replay = json.loads((folder / 'output/comparison.json').read_text())
        assert len(replay['results']) == 80
        assert all(r.get('error') == 'ICC-managed captures require an explicitly reviewed color-space conversion' and r['geometryStatus'] == 'passed' for r in replay['results'])
        captured = read('strict/comparison.json')
        assert captured['status'] == replay['status'] == 'failed' and len(captured['results']) == 80
        stable = ['fixture', 'status', 'error', 'referenceSHA256', 'candidateSHA256', 'componentGeometry', 'geometryStatus']
        assert [{k:r[k] for k in stable} for r in captured['results']] == [{k:r[k] for k in stable} for r in replay['results']]
    execution, display_inputs = read('display/result.json'), read('display/inputs.json')
    assert execution['exitCode'] == 0 and execution['binariesUnchangedSinceLaunch']
    assert execution['sourceProjectsMounted'] is execution['productBuildMounted'] is execution['accepted'] is False
    for key in ['sourceProjectsMounted', 'productBuildMounted', 'physicalDisplay', 'hardwareAcceleration', 'accepted']:
        assert display_inputs[key] is False
    argv = execution['command']
    assert argv.count('-v') == 1 and argv[argv.index('-v') + 1].endswith('/admin-clipping-compiled-v1/output/package:/package')
    assert argv[-4] == inputs['imageId'] and 'test ! -e /work/src;' in argv[-1]
    assert display_inputs['sourceRevision'] == MODULE
    assert display_inputs['consumerSha256'] == artifacts['consumerSha256'] and display_inputs['librarySha256'] == artifacts['librarySha256']
    assert read('display/output/environment.json') == display_inputs
    canonical = (CAP / 'display/canonical.sh').read_bytes()
    assert canonical == historical(MODULE, 'scripts/check-display-sessions.sh')
    assert sha(canonical) == display_inputs['canonicalSessionScriptSha256']
    filtered, count = re.subn(r'for fixture in [^\n]+; do', 'for fixture in admin-shell; do', canonical.decode(), count=1)
    assert count == 1 and filtered.encode() == (CAP / 'display/filtered.sh').read_bytes() == (CAP / 'display/executed.sh').read_bytes()
    assert sha(filtered.encode()) == display_inputs['filteredSessionScriptSha256']
    preserved = read('display/artifact-audit.json')
    assert preserved['unchangedSinceSessionLaunch'] and preserved['executedScriptSha256'] == sha(filtered.encode())
    assert preserved['files'] == {'consumer-build/InstalledConsumer': artifacts['consumerSha256'], 'install/lib/qml/Avelino/libAvelino.so': artifacts['librarySha256']}
    for protocol, backend, configuration in itertools.product(['xcb', 'wayland'], ['software', 'opengl'], ['standard', 'scaled']):
        prefix = f'admin-shell-{protocol}-{backend}-{configuration}'
        report = read('display/output/' + prefix + '.json'); scale = 1 if configuration == 'standard' else 2
        assert report['platform'] == protocol and report['graphicsApi'] == (1 if backend == 'software' else 3)
        assert report['dpr'] == scale and report['textScale'] == (1 if scale == 1 else 1.5)
        assert report['appearance'] == ('light' if scale == 1 else 'dark') and report['hardwareAcceleration'] is False
        report_checks(report, 'display/')
        if backend == 'opengl': assert 'Mesa RENDERER: llvmpipe' in (CAP / 'display/output' / (prefix + '.log')).read_text()
        for suffix, key in [('.png', 'windowCaptureSha256'), ('-session.png', 'sessionCaptureSha256')]:
            alias = 'display/' + prefix + suffix; use(alias); assert images[alias]['sha256'] == report[key]
            assert dimensions[images[alias]['stored']] == ((report['width'] * scale, report['height'] * scale) if suffix == '.png' else (2560, 1920))
        assert (CAP / 'display/output' / (prefix + '.captured')).is_file()
    assert used == set(images)
    print('Clipping package: compiled 266+40 per DPR, four consumer runs, eight fixed installed-module and eight consumer display contexts; strict ICC failures and all native/physical gates retained')


if __name__ == '__main__':
    verify()
