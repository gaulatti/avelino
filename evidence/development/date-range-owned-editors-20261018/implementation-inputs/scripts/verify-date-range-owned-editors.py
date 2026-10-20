#!/usr/bin/env python3
"""Verify the owned-editor checkpoint without granting mirror acceptance."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/date-range-owned-editors-20261018'


def verify():
    read = lambda name: json.loads((CAPSULE / name).read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = read('files.json')
    assert set(manifest) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p != CAPSULE / 'files.json'}
    for name, row in manifest.items():
        path = CAPSULE / name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name
    result = read('result.json')
    assert result['accepted'] is False and result['desktopCandidates'] == 76 and result['acceptedDesktopEntries'] == 0
    assert result['strictRasterMatches'] == 0 and result['nativeModelMatches'] == 384 and result['nativeGeometryMatches'] == 8
    for name in ['qt/date-range-qt-v12', 'package', 'catalog', 'display', 'relocated-regression']:
        assert read(name + '/result.json')['exitCode'] == 0
        assert all(row['exitCode'] == 0 for row in read(name + '/commands.json'))
    assert read('attempts/display-v1/result.json')['exitCode'] == 1
    assert 'module "Avelino" is not installed' in (CAPSULE / 'attempts/display-v1/display.log').read_text()
    replay = read('package/replay.json')
    assert replay['exactFiles'] == 560 and replay['differentFiles'] == []
    comparisons = {row['fixture']: row for row in read('strict/comparison.json')['results']}
    assert len(comparisons) == 384
    observations = models = geometry = 0
    for appearance in ['light', 'dark']:
        for scale in ['1', '1.5']:
            for dpr in [1, 2]:
                prefix = f'{appearance}-text{scale}-dpr{dpr}'
                report = read(f'package/output/{prefix}.json')
                assert report['accepted'] is False and len(report['closed']) == 48 and len(report['input']) == 3
                assert report['appearance'] == appearance and report['textScale'] == float(scale) and report['dpr'] == dpr
                for row in report['closed']:
                    actual, native = row['actual'], row['native']
                    same_model = actual['model'] == native['model'] and actual['displayed'] == native['displayed']
                    frames = dict(actual['frames']); frames.pop('arrow')
                    same_geometry = frames == native['frames']
                    assert row['modelMatches'] == same_model and row['geometryMatches'] == same_geometry
                    assert actual['model']['requests'] == []
                    models += same_model; geometry += same_geometry; observations += 1
                    name = prefix + '-' + row['configuration']['id'] + '.png'
                    comparison = comparisons[name]
                    expected = ROOT / 'evidence/reference-investigations/date-range-20261018/output' / native['referenceCapture']
                    candidate = CAPSULE / 'package/output' / name
                    assert digest(expected) == comparison['referenceSHA256'] and digest(candidate) == comparison['candidateSHA256']
                    with Image.open(expected) as image: source = image.copy()
                    with Image.open(candidate) as image: target = image.copy()
                    assert source.size == target.size and 'error' not in comparison
                    delta = ImageChops.difference(source.convert('RGB'), target.convert('RGB'))
                    alpha = ImageChops.difference(source.convert('RGBA').getchannel('A'), target.convert('RGBA').getchannel('A'))
                    same_pixels = delta.getbbox() is None and alpha.getbbox() is None
                    assert not same_pixels and comparison['status'] == 'failed'
                gallery = read(f'package/output/gallery-{prefix}.json')
                assert len(gallery['gallery']) == 17 and gallery['accepted'] is False
    assert (observations, models, geometry) == (384, 384, 8)
    for protocol in ['xcb', 'wayland']:
        for backend in ['software', 'opengl']:
            for configuration in ['standard', 'scaled']:
                report = read(f'display/output/{protocol}-{backend}-{configuration}.json')
                assert report['accepted'] is False and report['platform'] == protocol
                assert report['graphicsApi'] == (1 if backend == 'software' else 3)
                assert len(report['closed']) == 48 and len(report['input']) == 3 and report['modelMatches'] == 48
                session = report['displaySession']
                assert session['physicalDisplay'] is False and session['hardwareAcceleration'] is False and session['physicalInput'] is False
                assert digest(CAPSULE / 'display/output' / session['sessionCapture']) == session['sessionCaptureSha256']
    catalog = read('catalog/output/result.json')
    assert len(catalog['captures']) == 4 and catalog['accepted'] is False
    print('DateRangePicker owned editors: 384 exact models, 8 exact geometries, 384 raster failures, 8 relocated package/gallery and 8 virtual display profiles; candidate and mirror acceptance pending')


if __name__ == '__main__':
    verify()
