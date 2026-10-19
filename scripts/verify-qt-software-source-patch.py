#!/usr/bin/env python3
"""Decode the paired source-built Qt controls without accepting mirror parity."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/qt-software-source-patch-20261019'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((CAPSULE / name).read_text())


def rgba(path):
    with Image.open(path) as source:
        return source.convert('RGBA')


def profiles(label, expected):
    base = CAPSULE / 'regression' / label
    assert {p.parent.name for p in base.glob('*/result.json')} == set(expected)
    opacity_count = canvas_count = failed_count = 0
    for name, failed in expected.items():
        dpr = int(name[-1])
        directory = base / name
        record = json.loads((directory / 'result.json').read_text())
        assert record['qt'] == '6.8.3' and record['platform'] == name.split('-')[0]
        assert record['dpr'] == dpr and record['graphicsApi'] == 1
        assert record['windowColor'] == '#ff102030' and not record['physicalDisplay']
        assert len(record['frames']) == 30
        assert {(r['clipped'], r['shift'], r['sample']) for r in record['frames']} == {
            (clipped, shift, sample) for clipped in [False, True]
            for shift in [0, 0.25, 0.5, 0.75, 1] for sample in range(3)
        }
        previous = {}; failures = 0
        for row in record['frames']:
            path = directory / row['capture']; assert digest(path) == row['sha256']
            image = rgba(path); assert image.size == (160 * dpr, 100 * dpr)
            alpha = image.getchannel('A')
            nonopaque = image.width * image.height - alpha.histogram()[255]
            bbox = alpha.point(lambda value: 255 if value != 255 else 0).getbbox()
            bounds = [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]] if bbox else [0, 0, 0, 0]
            color = (23, 105, 219, 255) if row['clipped'] else (51, 68, 85, 255)
            painted = sum(pixel == color for pixel in image.get_flattened_data())
            key = row['clipped'], row['shift']; pixels = image.tobytes()
            stable = key not in previous or previous[key] == pixels; previous[key] = pixels
            assert nonopaque == row['nonOpaquePixels'] and bounds == row['bounds']
            assert painted == row['paintedPixels'] and painted > 0 and stable == row['stable']
            failures += bool(nonopaque or not painted or not stable)
        assert failures == record['failedFrames'] == failed
        assert record['canvasRuntimeChecksPassed'] and len(record['canvasFrames']) == 3
        assert {row['sample'] for row in record['canvasFrames']} == {0, 1, 2}
        previous_canvas = None
        for row in record['canvasFrames']:
            path = directory / row['capture']; assert digest(path) == row['sha256']
            image = rgba(path); assert image.size == (64 * dpr, 40 * dpr)
            assert set(image.get_flattened_data()) == {(23, 105, 219, 255)}
            pixels = image.tobytes()
            assert previous_canvas is None or previous_canvas == pixels; previous_canvas = pixels
            assert row['passed'] and row['stable'] and row['paintedPixels'] == image.width * image.height
        opacity_count += len(record['frames']); canvas_count += len(record['canvasFrames']); failed_count += failures
    return opacity_count, canvas_count, failed_count


def verify():
    files = read('files.json')
    assert set(files) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*')
                          if p.is_file() and p != CAPSULE / 'files.json'}
    for name, row in files.items():
        path = CAPSULE / name
        assert digest(path) == row['sha256'] and path.stat().st_size == row['bytes'], name
    result = read('result.json')
    assert not result['accepted'] and result['sourcePatchValidated']
    assert not result['supportedToolchainInstallerValidated'] and not result['fullMirrorAccepted']
    assert result['acceptedDesktopEntries'] == 0 and result['desktopCandidates'] == 76
    assert not result['physicalDisplay'] and not result['nativeAcceptance']
    assert result['qt'] == '6.8.3' and result['architecture'] == 'aarch64-linux-gnu'
    assert result['consumerUnchangedBetweenRuns'] and result['consumerSha256'] == 'eaf7e51252607ecdd6cc5aa5b428ceb192c0a681bb07e2c04b3b0dcfaa9c3aac'
    assert not result['sdkQmlLibrariesReplaced']
    assert result['baselineOverlayLibraries'] == result['patchedOverlayLibraries'] == ['libQt6Quick.so.6.8.3']
    assert read('provenance/baseline-build-jit-v3-result.json')['exitCode'] == 0
    features = read('provenance/effective-features.json')
    assert features['effectiveQmlJit'] == 'ON' and not features['sourcePatched']
    assert features['featureHeaders'] == result['effectiveFeatureHeaders'] == 7
    assert features['featureDefinitions'] == result['effectiveFeatureDefinitions'] == 49
    assert sum(len(r['sdk']) for r in features['features']) == 49
    assert all(r['matches'] and {k: 'ON' if v == '1' else 'OFF' for k, v in r['sdk'].items()} == r['source'] for r in features['features'])
    assert result['effectiveQmlJit']
    for label in ['baseline-jit', 'patched-jit']:
        lib = read('provenance/' + label + '-library.json')
        assert lib['runtimePath'] == '$ORIGIN'
        assert len(lib['sourceSha256']) == len(lib['installedSha256']) == 64
        linkage = (CAPSULE / ('provenance/' + label + '-linkage.log')).read_text()
        assert 'libQt6Qml.so.6 => /opt/qt/lib/' in linkage
        assert 'undefined symbol' not in linkage and 'not found' not in linkage and '/qt-build/' not in linkage
    commands = read('provenance/pipeline-v4-commands.json')
    assert [(r['name'], r['exitCode']) for r in commands] == [
        ('baseline-jit-stage', 0), ('baseline-jit-regression', 1), ('baseline-jit-date-profile', 1),
        ('apply-source-patch', 0), ('patched-jit-build', 0), ('patched-jit-stage', 0),
        ('patched-jit-regression', 0), ('patched-jit-date-profile', 0)]
    assert '--fuzz=0' in commands[3]['command'] and '--forward' in commands[3]['command']
    assert read('provenance/pipeline-v4-result.json')['sourcePatchValidated']
    assert digest(CAPSULE / 'source/qt-software-opacity.patch') == result['sourcePatchSha256'] == digest(ROOT / 'tools/qt-software-opacity.patch')
    assert result['sourceArchiveSha256'] == '1f03a2b8f5588b4face7da87926e9b2c1372b3a32157c52df07a75067a9db1af'
    assert digest(CAPSULE / 'source/before.cpp') == '0585433e2b972e48d407e18ef18960fec043d4b54be19ce42531a957dd9e6fb3'
    before = (CAPSULE / 'source/before.cpp').read_bytes()
    after = (CAPSULE / 'source/after.cpp').read_bytes()
    assert before.count(b'    if (m_opacity < 1.0f)\n') == 1
    assert after == before.replace(b'    if (m_opacity < 1.0f)\n',
        b'    // Fractional bounds have fringe pixels outside the opaque inset. Keep\n'
        b'    // these nodes in alpha dirty-region propagation so a backing store that\n'
        b'    // clears its update region also repaints the content below those fringes.\n'
        b'    if (m_opacity < 1.0f || m_boundingRectMin != m_boundingRectMax)\n')
    for name in ['qt-software-opacity.cpp', 'check-qt-software-opacity.sh']:
        assert digest(CAPSULE / 'fixture' / name) == digest(ROOT / 'tools' / name)
    assert profiles('baseline-jit', {'xcb-dpr1': 0, 'xcb-dpr2': 0, 'wayland-dpr1': 9}) == (
        result['baselineOpacityFrames'], result['baselineCanvasFrames'], result['baselineFailedOpacityFrames']) == (90, 9, 9)
    assert profiles('patched-jit', {name: 0 for name in ['xcb-dpr1', 'xcb-dpr2', 'wayland-dpr1', 'wayland-dpr2']}) == (
        result['patchedOpacityFrames'], result['patchedCanvasFrames'], 0) == (120, 12, 0)
    patched = read('regression/patched-jit/result.json')
    assert patched['frames'] == 120 and patched['canvasFrames'] == 12
    baseline_dir = CAPSULE / 'date/baseline-jit'; patched_dir = CAPSULE / 'date/patched-jit'
    failure = read('date/baseline-jit/wayland-software-scaled-failed.json')
    assert failure['sameState'] and failure['sameModel'] and not failure['samePixels']
    assert failure['before'] == failure['after'] and failure['beforeModel'] == failure['afterModel']
    assert (failure['sourceCase'], failure['endpoint'], failure['callerRtl']) == ('arabic-year', 'end', False)
    before = rgba(baseline_dir / 'wayland-software-scaled-failed-before.png')
    after = rgba(baseline_dir / 'wayland-software-scaled-failed-after.png')
    difference = ImageChops.difference(before, after); mask = difference.getchannel('R')
    for channel in ['G', 'B', 'A']: mask = ImageChops.lighter(mask, difference.getchannel(channel))
    assert before.size == after.size == (1280, 800) and mask.getbbox() == (765, 384, 766, 418)
    changed = [(a, b) for a, b in zip(before.get_flattened_data(), after.get_flattened_data()) if a != b]
    assert len(changed) == 12 and set(changed) == {((0, 0, 0, 0), (34, 34, 34, 255))}
    report = read('date/patched-jit/wayland-software-scaled.json')
    assert report['accepted'] is False and report['structuralChecks'] == 'passed'
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['visualAcceptance'] == report['readerPhysicalAcceptance'] == 'pending'
    literal = report['literalInput']; assert len(literal) == result['literalChecks'] == 16
    assert {(r['sourceCase'], r['endpoint'], r['callerRtl']) for r in literal} == {
        (name, endpoint, rtl) for name in ['hebrew-day', 'hebrew-month', 'english-month', 'arabic-year']
        for endpoint in ['start', 'end'] for rtl in [False, True]}
    assert all(r['samePixels'] and r['before'] == r['after'] for r in literal)
    assert sum(r['nativeValueCompared'] for r in literal) == 8
    for row in literal:
        name = f"wayland-software-scaled-literal-{row['sourceCase']}-{row['endpoint']}-rtl{int(row['callerRtl'])}.png"
        image = rgba(patched_dir / name)
        assert image.size == (1280, 800) and image.getchannel('A').getextrema() == (255, 255)
    cold = read('provenance/pipeline-v4-cold-comparison.json')
    expected_names = {'wayland-software-scaled-' + r['configuration']['id'] + '.png'
                      for group in ['closed', 'chinese'] for r in report[group]}
    assert len(report['closed']) == 48 and len(report['chinese']) == 36
    assert {r['name'] for r in cold['rows']} == expected_names and len(cold['rows']) == 84
    for row in cold['rows']:
        a = baseline_dir / row['name']; b = patched_dir / row['name']
        assert a.read_bytes() == b.read_bytes() and digest(a) == row['before'] == row['after']
        assert row['identical'] and rgba(a).tobytes() == rgba(b).tobytes()
    assert cold['coldComparisons'] == cold['coldByteIdentical'] == result['coldCaptures'] == result['coldByteIdentical'] == 84
    print('Source Qt patch:90 red-control opacity frames,9 Canvas2D;120 green opacity frames,12 Canvas2D;16 literal checks;84 byte-identical cold captures. Toolchain and mirror acceptance pending')


if __name__ == '__main__':
    verify()
