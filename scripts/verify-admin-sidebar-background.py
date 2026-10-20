#!/usr/bin/env python3
"""Check the padded-sidebar candidate evidence; native rendering stays pending."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / 'evidence/development/admin-sidebar-background-20261020'


def read(name):
    return json.loads((CAP / name).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify():
    files = read('files.json')
    assert set(files) == {str(p.relative_to(CAP)) for p in CAP.rglob('*') if p.is_file() and p.name != 'files.json'}
    relative = CAP.relative_to(ROOT)
    names = sorted({str(relative / n) for n in files} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(names), 'Every sidebar checkpoint member must be in the Git index'
    result = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                            input=('\n'.join(':' + n for n in names) + '\n').encode(), stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(result.stdout)
    for name in names:
        header = stream.readline().split(); assert len(header) == 3 and header[1] == b'blob'
        raw = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        assert raw == (ROOT / name).read_bytes()
        if name != str(relative / 'files.json'):
            assert sha(raw) == files[str(Path(name).relative_to(relative))]
    assert not stream.read()
    scope = read('scope.json')
    assert scope['sourcePaddingBackgroundImplemented'] and scope['sourceUncommittedAtCapture']
    assert scope['scaleFactors'] == [1, 2] and scope['qtTestsPerContext'] == 264
    assert (scope['rawBeforeCaptures'], scope['rawAfterCaptures'], scope['nativeRowObservations']) == (4, 4, 2)
    for key in ['freshModuleCompilation', 'newInstalledConsumerExecuted', 'sourceColourInputsIntegrated',
                'fullDisplayMatrixPassed', 'nativeGlassImplemented', 'nativeRasterAccepted',
                'physicalInput', 'readerAcceptance', 'accepted']:
        assert scope[key] is False
    source = read('source-reference.json')
    manifest = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    assert source['revision'] == scope['reference'] == manifest['revision']
    assert source['file'] == next(f for f in manifest['files'] if f['path'] == 'Sources/Sabella/Mobile.swift')
    assert (source['paddingPoints'], source['standardCallerWidth'], source['standardCardX'], source['standardCardWidth']) == (16, 180, 44, 212)
    assert source['sourceFileCopiedIntoLinuxRepository'] is source['accepted'] is False
    parent = ROOT / 'evidence/reference-investigations/admin-shell-colour-inputs-20261020'
    native = read('native-row-observations.json')
    assert native['parent'] == str(parent.relative_to(ROOT)) and native['backingScale'] == 2
    assert native['colorConversionPerformed'] is native['nativeRasterAccepted'] is native['accepted'] is False
    native_index = json.loads((parent / 'images.json').read_text())
    assert [r['theme'] for r in native['rows']] == ['light', 'dark']
    for row in native['rows']:
        entry = native_index[row['capture']]; raw = (parent / entry['stored']).read_bytes()
        assert sha(raw) == row['sha256'] == entry['sha256']
        assert row['row'] == 500 and row['inspectedColumns'] == [0, 602]
        with Image.open(io.BytesIO(raw)) as image:
            image = image.convert('RGBA')
            for segment in row['segments']:
                assert all(list(image.getpixel((x, row['row']))) == segment['rgba'] for x in range(segment['x'], segment['end']))
        assert [(s['x'], s['end']) for s in row['segments']] == [(0, 88), (88, 512), (512, 600), (600, 601), (601, 602)]
    for scale in [1, 2]:
        receipt = read(f'runtime/run-v{scale}.json')
        assert receipt['exitCode'] == 0 and receipt['freshCompilation'] is receipt['accepted'] is False
        assert f'QT_SCALE_FACTOR={scale}' in receipt['command']
        assert '264 passed, 0 failed' in (CAP / f'runtime/run-v{scale}.log').read_text()
        original = {n: (CAP / f'runtime/inputs-v{scale}' / n).read_bytes() for n in receipt['sourceInputHashes']}
        assert {n: sha(b) for n, b in original.items()} == receipt['sourceInputHashes']
        assert all((ROOT / n).read_bytes() == b for n, b in original.items())
        payload = dict(original)
        payload['tests/components/witnesses.js'] = b'var data = ' + original['tests/consumer/native-admin-shell-witnesses.json'] + b';\n'
        name = 'tests/components/tst_admin_shell.qml'
        text = payload[name].decode().replace('import QtTest', 'import QtTest\nimport "witnesses.js" as Native', 1)
        payload[name] = text.replace('    id: root', '    id: root\n    property var nativeAdminShellWitnesses: Native.data', 1).encode()
        assert {n: sha(b) for n, b in payload.items()} == receipt['executedPayloadHashes']
        capture = read(f'runtime/capture-dpr{scale}.json')
        assert capture['exitCode'] == 0 and capture['scaleFactor'] == scale
        assert '4 passed, 0 failed' in (CAP / f'runtime/capture-dpr{scale}.log').read_text()
        for key in ['freshCompilation', 'sourceColourInputsIntegrated', 'nativeRasterAccepted', 'accepted']:
            assert capture[key] is False
        for name, digest in capture['sourceInputHashes'].items():
            assert sha((ROOT / name).read_bytes()) == digest
        for name, digest in capture['executedPayloadHashes'].items():
            assert sha((CAP / f'runtime/capture-inputs-dpr{scale}' / name).read_bytes()) == digest
    base = read('base-module.json')
    published = json.loads((ROOT / 'evidence/development/admin-shell-sessions-20261020/inputs.json').read_text())
    assert base['sha256'] == published['librarySha256'] and base['newQmlInterpreted'] and base['moduleReused']
    assert base['freshCompilation'] is base['accepted'] is False
    images = read('images.json'); render = read('render-check.json')
    assert len(images) == 8 and len(render['checks']) == 4
    assert render['rawDiagnosticInputs'] and render['nativeRasterAccepted'] is render['accepted'] is False
    previous = ROOT / render['beforeCapsule']; previous_index = json.loads((previous / 'images.json').read_text())
    assert previous == ROOT / 'evidence/development/admin-divider-package-20261020'
    for logical, entry in images.items():
        raw = (CAP / entry['stored']).read_bytes()
        assert sha(raw) == entry['sha256'] == Path(entry['stored']).stem and len(raw) == entry['bytes']
    assert {r['stored'] for r in images.values()} == {str(p.relative_to(CAP)) for p in (CAP / 'images').glob('*.png')}
    for check in render['checks']:
        scale, theme = check['scale'], check['theme']
        before = Image.open(CAP / images[f'before/dpr{scale}/{theme}.png']['stored']).convert('RGBA')
        after_entry = images[f'after/dpr{scale}/{theme}.png']
        after = Image.open(CAP / after_entry['stored']).convert('RGBA')
        capture = read(f'runtime/capture-dpr{scale}.json')
        assert capture['rawCaptures'][f'standard-{theme}-True.png'] == after_entry['sha256']
        assert before.size == after.size == tuple(check['dimensions']) == (840 * scale, 500 * scale)
        assert images[f'before/dpr{scale}/{theme}.png']['sha256'] == previous_index[check['beforeAlias']]['sha256']
        diff = ImageChops.difference(before, after).convert('RGB')
        assert diff.getbbox() == (tuple(check['differenceBounds']) if check['differenceBounds'] else None)
        changed = sum(count for count, colour in diff.getcolors(diff.width * diff.height) if colour != (0, 0, 0))
        assert changed == check['changedPixels'] == (0 if theme == 'light' else 44000 * scale * scale)
        assert diff.crop((44 * scale, 0, 256 * scale, 500 * scale)).getbbox() is None
        assert diff.crop((300 * scale, 0, 840 * scale, 500 * scale)).getbbox() is None
        for sample in check['samples']:
            point = (sample['x'], check['sampledRow'])
            assert list(before.getpixel(point)) == sample['before'] and list(after.getpixel(point)) == sample['after']
    print('Admin sidebar background: 264 tests at each DPR; four raw renders; padded-card bounds corrected; native glass and raster acceptance pending')


if __name__ == '__main__':
    verify()
