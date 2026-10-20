#!/usr/bin/env python3
"""Check native material observations; rendering and physical gates remain open."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/reference-investigations/admin-shell-materials-20261020'
PARENT = ROOT / 'evidence/reference-investigations/admin-shell-colour-inputs-20261020'


def read(name):
    return json.loads((CAPSULE / name).read_text())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify():
    files = read('files.json')
    assert set(files) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p != CAPSULE / 'files.json'}
    relative = CAPSULE.relative_to(ROOT)
    names = sorted({str(relative / n) for n in files} | {str(relative / 'files.json')})
    tracked = subprocess.check_output(['git', 'ls-files', '-z', '--', str(relative)], cwd=ROOT).decode().strip('\0').split('\0')
    assert set(tracked) == set(names), 'Every material capsule member must be in the Git index'
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
    assert (scope['contextsPerVersion'], scope['versions'], scope['controlImages'], scope['byteIdenticalControlImages']) == (4, 3, 36, 36)
    assert (scope['nativeDividerViewWidth'], scope['actualBackingScale'], scope['publicDividerThickness']) == (0.5, 2, 1)
    for key in ['libraryRebuilt', 'nativeRasterAccepted', 'physicalInput', 'readerAcceptance', 'accepted']:
        assert scope[key] is False
    assert scope['sourceHelperAndLibraryOutsideLinuxRepository'] is True
    parent_inputs = json.loads((PARENT / 'probe-inputs.json').read_text())
    parent_observations = json.loads((PARENT / 'observations.json').read_text())
    parent_images = json.loads((PARENT / 'images.json').read_text())
    images = read('images.json'); assert len(images) == 36
    dimensions = {}
    for stored in {r['stored'] for r in images.values()}:
        path = CAPSULE / stored
        assert path.parent == CAPSULE / 'images' and sha(path.read_bytes()) == path.stem
        with Image.open(path) as image:
            image.load(); assert image.format == 'PNG'
            assert sha(image.info['icc_profile']) == parent_inputs['captureProfileSha256']
            dimensions[stored] = image.size
    assert set(dimensions) == {str(p.relative_to(CAPSULE)) for p in (CAPSULE / 'images').glob('*.png')}
    previous_helper = parent_inputs['helperSha256']
    for version in [1, 2, 3]:
        inputs = read(f'v{version}/inputs.json')
        assert inputs['reference'] == scope['reference'] == parent_inputs['reference']
        assert inputs['libraryRebuilt'] is inputs['physicalInput'] is inputs['accepted'] is False
        assert inputs['libraryObjectSha256'] == parent_inputs['objectSha256']
        assert inputs['parentHelperSha256'] == previous_helper
        previous_helper = inputs['helperSha256']
        assert read(f'v{version}/compile-command.json')['exitCode'] == read(f'v{version}/capture-command.json')['exitCode'] == 0
        audit = read(f'v{version}/audit.json')
        assert audit['all12ControlsByteIdentical'] is True and audit['accepted'] is False
        assert len(audit['controls']) == 12 and all(r['identical'] for r in audit['controls'])
        observations = read(f'observations-v{version}.json')
        assert observations['accepted'] is observations['physicalInput'] is observations['libraryRebuilt'] is False
        records = observations['records']; assert len(records) == 4
        assert {(r['dark'], r['initial']) for r in records} == {(False, False), (False, True), (True, False), (True, True)}
        for row in records:
            old = next(r for r in parent_observations['records'] if (r['dark'], r['initial']) == (row['dark'], row['initial']))
            assert row['resolvedInputs'] == old['resolvedInputs']
            for key in ['requests', 'navigation', 'pending', 'bodyFramesFromGlobal', 'lastLayoutFrames', 'arrangedSubviews']:
                assert row['state'][key] == old['state'][key]
            for kind in ['before', 'after', 'chrome']:
                capture = row['state'][kind]; image = images[f'v{version}/' + capture['path']]
                assert image['sha256'] == Path(image['stored']).stem == parent_images[capture['path']]['sha256'] == capture['sha256']
                raw = (CAPSULE / image['stored']).read_bytes()
                assert len(raw) == image['bytes'] and raw == (PARENT / parent_images[capture['path']]['stored']).read_bytes()
                assert dimensions[image['stored']] == (capture['width'], capture['height'])
            views = row['state']['nativeHierarchy']
            divider = next(v for v in views if v['class'] == 'NSSplitDividerView')
            assert divider['hiddenByAncestor'] == (not row['initial'])
            assert divider['hostFrame'] == dict(x=299.5, y=0, width=0.5, height=500)
            if row['initial']:
                shadow = next(v for v in views if v['class'] == '_NSSplitViewShadowView' and not v['hiddenByAncestor'])
                assert shadow['hostFrame'] == dict(x=300, y=0, width=12, height=500)
                pockets = [v for v in views if v['class'] == 'NSScrollPocket' and not v['hiddenByAncestor']]
                assert sorted(v['hostFrame']['width'] for v in pockets) == [300, 540]
                assert all(v['hostFrame']['height'] == 52 for v in pockets)
            if version >= 2:
                properties = row['state']['dividerProperties']
                assert properties['thickness'] == 1 and properties['windowKey'] is False
                expected_rgb = [1, 1, 1] if version == 2 or row['dark'] else [0, 0, 0]
                assert properties['sRGB'] == expected_rgb + [25 / 255]
            if version == 3:
                assert properties['style'] == 2
                assert properties['resolutionContext'] == 'effectiveAppearance.performAsCurrentDrawingAppearance'
                assert row['state']['darkWindowDividerProperties'] == properties
    subprocess.run([sys.executable, str(ROOT / 'scripts/generate-admin-divider-witnesses.py'), '--check'], check=True)
    print('AdminShell materials: 36 unchanged control images; source divider geometry/appearance projected; glass, pockets, shadows and raster pending')


if __name__ == '__main__':
    verify()
