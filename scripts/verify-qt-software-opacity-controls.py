#!/usr/bin/env python3
"""Audit raw SDK graphics controls without accepting a Qt patch or Linux API."""
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/qt-software-opacity-controls-20261019'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    read = lambda name: json.loads((CAPSULE / name).read_text())
    files = read('files.json')
    assert set(files) == {
        str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*')
        if p.is_file() and p != CAPSULE / 'files.json'
    }
    for name, row in files.items():
        path = CAPSULE / name
        assert digest(path) == row['sha256'] and path.stat().st_size == row['bytes'], name

    result = read('result.json')
    assert result['accepted'] is False and result['acceptedDesktopEntries'] == 0
    assert result['desktopCandidates'] == 76 and result['originalSdk']
    assert not result['sourcePatchValidated'] and not result['supportedToolchainIntegrationChanged']
    assert not result['physicalDisplay'] and not result['nativeAcceptance'] and not result['completeMatrixPassed']
    assert result['qt'] == '6.8.3' and result['architecture'] == 'aarch64-linux-gnu'
    assert result['passedProfiles'] == ['xcb-dpr1', 'xcb-dpr2']
    assert result['failedProfiles'] == ['wayland-dpr1'] and result['unrunProfiles'] == ['wayland-dpr2']
    assert read('command.json')['exitCode'] == 1

    features = read('sdk/features.json')
    assert len(features) == result['effectiveFeatureHeaders'] == 7
    assert sum(len(row['sdk']) for row in features) == result['effectiveFeatureDefinitions'] == 49
    assert result['effectiveQmlJit']
    assert next(row['sdk']['QT_FEATURE_qml_jit'] for row in features if 'QT_FEATURE_qml_jit' in row['sdk']) == '1'
    macro_lines = (CAPSULE / 'sdk/sdk-effective-macros.log').read_text().splitlines()
    assert '#define QT_FEATURE_qml_jit 1' in macro_lines
    preprocessing = read('sdk/sdk-feature-preprocessor.json')
    assert preprocessing['target'] == result['architecture']
    assert '-dM' in preprocessing['command'] and '#include <QtCore/qglobal.h>' in preprocessing['input']
    identity = read('sdk/identity.json')
    assert identity['qt'] == '6.8.3' and not identity['sourceBuildOverlay'] and not identity['interposition']
    assert len(identity['quickLibrarySha256']) == len(identity['qmlLibrarySha256']) == 64
    addition = read('sdk/sdk-addition.json')
    assert addition['changedExistingFiles'] == [] and len(addition['newFiles']) == 44
    prerequisite = read('sdk/prerequisites.json')
    assert prerequisite['changed'] == prerequisite['removed'] == []
    assert set(prerequisite['added']) == {'libvulkan-dev'}

    profiles = {'xcb-dpr1': (1, 0), 'xcb-dpr2': (2, 0), 'wayland-dpr1': (1, 9)}
    assert result['profiles'] == len(profiles) == 3
    assert {path.parent.name for path in (CAPSULE / 'output').glob('*/result.json')} == set(profiles)
    opacity_frames = canvas_frames = opacity_failures = 0
    for name, (dpr, expected_failures) in profiles.items():
        directory = CAPSULE / 'output' / name
        record = json.loads((directory / 'result.json').read_text())
        assert record['qt'] == '6.8.3' and record['platform'] == name.split('-')[0]
        assert record['graphicsApi'] == 1 and record['dpr'] == dpr
        assert record['windowColor'] == '#ff102030' and not record['physicalDisplay']
        rows = record['frames']
        assert len(rows) == 30
        assert {(row['clipped'], row['shift'], row['sample']) for row in rows} == {
            (clipped, shift, sample) for clipped in [False, True]
            for shift in [0, 0.25, 0.5, 0.75, 1] for sample in range(3)
        }
        previous = {}; failures = 0
        for row in rows:
            path = directory / row['capture']; assert digest(path) == row['sha256']
            with Image.open(path) as source:
                image = source.convert('RGBA')
            assert image.size == (160 * dpr, 100 * dpr)
            alpha = image.getchannel('A')
            nonopaque = image.width * image.height - alpha.histogram()[255]
            bbox = alpha.point(lambda value: 255 if value != 255 else 0).getbbox()
            bounds = [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]] if bbox else [0, 0, 0, 0]
            expected = (23, 105, 219, 255) if row['clipped'] else (51, 68, 85, 255)
            painted = sum(pixel == expected for pixel in image.get_flattened_data())
            key = (row['clipped'], row['shift']); pixels = image.tobytes()
            stable = key not in previous or previous[key] == pixels; previous[key] = pixels
            assert nonopaque == row['nonOpaquePixels'] and bounds == row['bounds']
            assert painted == row['paintedPixels'] and painted > 0
            assert stable == row['stable']
            failures += bool(nonopaque or not painted or not stable)
        assert failures == record['failedFrames'] == expected_failures
        assert record['canvasRuntimeChecksPassed'] and len(record['canvasFrames']) == 3
        assert {row['sample'] for row in record['canvasFrames']} == {0, 1, 2}
        previous_canvas = None
        for row in record['canvasFrames']:
            path = directory / row['capture']; assert digest(path) == row['sha256']
            with Image.open(path) as source:
                image = source.convert('RGBA')
            assert image.size == (64 * dpr, 40 * dpr)
            assert set(image.get_flattened_data()) == {(23, 105, 219, 255)}
            pixels = image.tobytes()
            assert previous_canvas is None or previous_canvas == pixels
            previous_canvas = pixels
            assert row['passed'] and row['stable'] and row['paintedPixels'] == image.width * image.height
        opacity_frames += len(rows); canvas_frames += len(record['canvasFrames']); opacity_failures += failures
    assert opacity_frames == result['opacityFrames'] == 90
    assert canvas_frames == result['canvasFrames'] == 9
    assert opacity_failures == result['failedOpacityFrames'] == 9
    assert not (CAPSULE / 'output/wayland-dpr2').exists()
    print('SDK controls:90 raw opacity frames,9 Canvas2D frames;9 Wayland alpha failures;49 effective SDK features; patch and parity acceptance pending')


if __name__ == '__main__':
    verify()
