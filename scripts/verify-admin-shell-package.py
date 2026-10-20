#!/usr/bin/env python3
"""Audit compiled/package AdminShell results without approving native parity."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/admin-shell-package-20261020'
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
    outcome = read('result.json')
    assert outcome['reference'] == REFERENCE
    assert outcome['successfulSessionMatrixIncluded'] is False
    assert outcome['sessionMatrixWasLiveAtCapture'] is True
    for key in ['nativeRasterAccepted', 'nativeToolbarEquivalentVerified', 'physicalInput', 'readerAcceptance', 'accepted']:
        assert outcome[key] is False
    first = read('compiled-v1/commands.json')
    assert [r['name'] for r in first] == ['configure', 'build', 'admin-dpr1', 'mobile-dpr1',
        'admin-dpr2', 'mobile-dpr2', 'install', 'consumer-configure', 'consumer-build']
    assert [r['exitCode'] for r in first] == [0] * 8 + [1]
    assert 'ambiguous overload' in (CAPSULE / 'compiled-v1/consumer-build.log').read_text()
    assert read('compiled-v1/result.json')['exitCode'] == 1
    for scale in [1, 2]:
        for name, count in [('admin', 260), ('mobile', 40)]:
            assert f'Totals: {count} passed, 0 failed' in (CAPSULE / f'compiled-v1/{name}-dpr{scale}.log').read_text()
    for stage in ['consumer-repair-v2', 'session-schema-v3', 'activation-v4']:
        result, inputs = read(stage + '/result.json'), read(stage + '/inputs.json')
        assert result['exitCode'] == 0 and result['consumerBuildPassed']
        assert result['sourceInputsUnchanged'] and result['coreLibrariesUnchanged']
        assert not inputs['coreLibraryChanged']
        for (name, checksum), content in zip(inputs['sourceFiles'].items(),
                git_blobs([inputs['sourceRevision'] + ':' + n for n in inputs['sourceFiles']]), strict=True):
            assert digest(content) == checksum, name
    native = json.loads((ROOT / 'tests/consumer/native-admin-shell-witnesses.json').read_text())
    assert native['reference'] == REFERENCE
    profiles = {r['name']: r for r in native['profiles']}
    images = read('images.json')
    dimensions = {}
    for name in {r['stored'] for r in images.values()}:
        path = CAPSULE / name
        assert path.parent == CAPSULE / 'images' and path.suffix == '.png'
        content = path.read_bytes(); assert digest(content) == path.stem
        with Image.open(io.BytesIO(content)) as image:
            image.load(); assert image.format == 'PNG'; dimensions[name] = image.size
    assert set(dimensions) == {str(p.relative_to(CAPSULE)) for p in (CAPSULE / 'images').glob('*.png')}
    for logical, row in images.items():
        assert not Path(logical).is_absolute() and '..' not in Path(logical).parts
        assert row['sha256'] == Path(row['stored']).stem
        assert row['bytes'] == (CAPSULE / row['stored']).stat().st_size
    for context in ['light-dpr1', 'dark-dpr1', 'light-dpr2', 'dark-dpr2']:
        command, report = read('offscreen/' + context + '.json'), read('reports/output/' + context + '.json')
        assert command['exitCode'] == 0 and not command['sourceProjectsMounted'] and not command['productBuildMounted']
        assert report['reference'] == REFERENCE and report['accepted'] is False
        assert report['nativeLayouts'] == len(report['layouts']) == 80
        assert report['nativeHistoryStates'] == sum(len(r['states']) for r in report['histories']) == 160
        assert report['nativeDividerCases'] == len(report['boundaries']) == 168
        assert report['qtAccessibilityInterfaces'] == 2
        assert report['qtKeyboardActivation'] and report['qtShortcutActivation'] and report['qtCallerIdentityRetained']
        for row in report['layouts']:
            expected = profiles[row['name']]['state']
            assert all(row[k] == v for k, v in expected.items() if k != 'step')
            item = images['reports/' + row['capture']]
            assert dimensions[item['stored']] == (row['pixelWidth'], row['pixelHeight'])
        for history, expected in zip(report['histories'], native['histories'], strict=True):
            assert history['owner'] == expected['owner'] and history['initial'] == expected['initial']
            assert history['states'] == expected['states']
        for row, expected in zip(report['boundaries'], native['boundaries'], strict=True):
            assert all(row[k] == expected[k] for k in ['columnWidth', 'initial', 'requestedPosition'])
            actual = row['actual']; pane = expected['after'][0]
            assert actual['displayedNavigation'] == (not pane['collapsed'])
            assert actual['columnWidth'] == pane['width']
            assert actual['navigation'] == expected['navigation'] and actual['requests'] == expected['requests']
    assert read('sessions-v1/result.json')['exitCode'] != 0
    assert 'Window shortcut failed' in (CAPSULE / 'sessions-v1/output/admin-shell-xcb-software-standard.log').read_text()
    smoke = read('smokes/result.json')
    assert smoke['exitCode'] == 0 and smoke['consumerSmokeCommands'] == 44
    assert len(smoke['originalCommands']) == len(smoke['executedCommands']) == 44
    assert not smoke['sourceProjectsMounted'] and not smoke['otherInstalledScriptStepsExecuted']
    smoke_source = subprocess.check_output(['git', 'show', '484b7ab9b4588c289f2becbd0216d43d34ae80a0:scripts/check-installed.sh'], cwd=ROOT)
    assert digest(smoke_source) == smoke['sourceSha256']
    catalog = read('catalog-regression/output/catalog-results.json')
    assert len(catalog['captures']) == 167 and catalog['missingModuleRefusal'] == 'passed'
    assert read('catalog-regression/result.json')['exitCode'] == 0
    for row in catalog['captures']:
        image = images['catalog-regression/' + row['path']]
        assert image['sha256'] == row['sha256']
        metadata = CAPSULE / 'catalog-regression/output' / (row['path'] + '.json')
        assert digest(metadata.read_bytes()) == row['metadataSha256']
        record = json.loads(metadata.read_text())
        assert dimensions[image['stored']] == (record['width'] * record['dpr'], record['height'] * record['dpr'])
    assert read('gallery/result.json')['exitCode'] == 0 and read('gallery/result.json')['captures'] == 4
    assert outcome['compiledAdminTestsPerScale'] == 260 and outcome['compiledMobileTestsPerScale'] == 40
    assert outcome['installedSmokeCommands'] == 44 and outcome['installedCatalogCaptures'] == 167
    return outcome


if __name__ == '__main__':
    verify()
    print('AdminShell compiled/package checks: two scales, four source-absent runs, 44 smokes and 167 catalog captures; native parity pending')
