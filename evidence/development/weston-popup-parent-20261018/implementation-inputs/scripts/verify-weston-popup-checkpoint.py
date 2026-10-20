#!/usr/bin/env python3
"""Audit the compositor dependency fix without granting mirror acceptance."""
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/weston-popup-parent-20261018'


def verify():
    read = lambda name: json.loads((CAPSULE / name).read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = read('files.json')
    assert set(manifest) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p != CAPSULE / 'files.json'}
    for name, row in manifest.items():
        path = CAPSULE / name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name
    result = read('result.json')
    assert result['accepted'] is False and result['acceptedDesktopEntries'] == 0
    assert result['referencePinsChanged'] is False and result['approvedExceptions'] == []
    assert result['deterministicPopupOrderFixed'] is True
    assert result['completeDisplayGatePassed'] is False and result['completeDisplayGateStatus'] == 'running when sealed'
    assert result['priorFileInputFailureResolved'] is False
    spec = read('source-specs.json')
    for name, value in spec['changedFiles'].items():
        assert digest(CAPSULE / 'implementation-inputs' / name) == value
    parent = ROOT / 'evidence/development/navigation-cjk-metrics-20261018'
    assert digest(parent / 'files.json') == spec['parentManifestSha256']
    previous = json.loads((parent / 'source-specs.json').read_text())
    assert spec['coreFiles'] == previous['coreFiles'] and len(spec['coreFiles']) == 604
    assert spec['consumerFiles'] == previous['consumerFiles'] and len(spec['consumerFiles']) == 149
    assert not (set(spec['changedFiles']) & set(spec['coreFiles']))
    assert (CAPSULE / 'historical-verification.log').read_text().count('mirror acceptance pending') == 1
    red = read('protocol/sanitizer-retry.json')
    assert red['exitCode'] == 6
    assert next(r for r in read('protocol/commands.json') if r['name'] == 'original-release')['exitCode'] == 6
    assert 'Segmentation fault' in (CAPSULE / 'protocol/original-release.log').read_text()
    fault = (CAPSULE / 'protocol/original-sanitizer-v2/weston-client.log').read_text()
    assert 'runtime error: member access within null pointer' in fault
    assert 'weston_desktop_surface_update_view_position' in fault and 'surface.c:117' in fault
    original = (CAPSULE / 'asan/original-surface.c').read_text()
    patched = (CAPSULE / 'asan/patched-surface.c').read_text()
    expected_patch = ''.join(difflib.unified_diff(original.splitlines(True), patched.splitlines(True), fromfile='a/libweston/desktop/surface.c', tofile='b/libweston/desktop/surface.c'))
    patch = CAPSULE / 'implementation-inputs/tools/weston-popup-parent.patch'
    assert patch.read_text() == expected_patch
    candidate = read('asan/inputs.json')
    assert candidate['changedSourceFiles'] == ['libweston/desktop/surface.c']
    assert digest(patch) == candidate['patchSha256']
    assert digest(CAPSULE / 'asan/original-surface.c') == candidate['originalSurfaceSha256']
    assert digest(CAPSULE / 'asan/patched-surface.c') == candidate['modifiedSurfaceSha256']
    assert read('asan/result.json')['exitCode'] == read('asan/result.json')['containerExitCode'] == 0
    assert 'desktop_surface.c.o' in (CAPSULE / 'asan/build.log').read_text()
    assert read('protocol/candidate-visible-result.json')['exitCode'] == 0
    visible = CAPSULE / 'protocol/candidate-sanitizer-visible-v2'
    ready = json.loads((visible / 'ready.json').read_text())
    assert ready['parentCommitsBeforeFirstPopupCommit'] == 1 and ready['popupConfigured'] and ready['popupFrame']
    with Image.open(visible / 'session.png') as image:
        assert image.size == (640, 480)
        counts = Counter(image.convert('RGB').getdata())
    assert counts[(211, 47, 47)] == 400 and counts[(25, 118, 210)] == 9600
    trace = (visible / 'weston-client.log').read_text()
    assert 'runtime error:' not in trace and 'ERROR: AddressSanitizer' not in trace
    assert read('protocol/early-capture-exclusion.json')['excluded'] is True
    toolchain = read('toolchain/result.json')
    assert toolchain['exitCode'] == 0
    assert read('toolchain-download-failure/result.json')['exitCode'] == 1
    assert 'TimeoutError' in (CAPSULE / 'toolchain-download-failure/build.log').read_text()
    inputs = read('toolchain/inputs.json')
    assert inputs['archiveSha256'] == candidate['sourceReleaseSha256'] == '66252c9c5bbc45ab402e2518b76e6d824f09ebc1d0040ee2f51b096a1bc585b1'
    for name, value in inputs['files'].items():
        assert digest(CAPSULE / 'toolchain/source-inputs' / name) == value == spec['changedFiles'][name]
    unchanged = read('toolchain/unchanged-qt-fonts.json')
    assert unchanged['identical'] and unchanged['records'][0]['environment'] == unchanged['records'][1]['environment']
    assert unchanged['records'][1]['environment']['qtVersion'] == '6.8.3'
    assert len(unchanged['records'][1]['environment']['fontFiles']) == 4
    installed = read('toolchain/installed-evidence/popup-parent-regression/result.json')
    assert installed['status'] == 'passed' and installed['popupPixels'] == 400 and installed['parentPixels'] == 9600
    assert installed['clientSourceSha256'] == digest(CAPSULE / 'implementation-inputs/tools/weston-popup-order.c')
    assert digest(CAPSULE / 'toolchain/installed-evidence/weston-popup-parent.patch') == digest(patch)
    display = read('display-startup/inputs.json')
    assert display['imageId'] == toolchain['imageId'] and display['patchSha256'] == digest(patch)
    assert display['consumerFiles'] == spec['consumerFiles']
    assert display['consumerSha256'] == json.loads((parent / 'package/inputs.json').read_text())['consumerSha256']
    assert digest(CAPSULE / 'display-startup/check.sh') == display['scriptSha256'] == previous['liveScripts']['scripts/check-display-sessions.sh']
    assert read('file-input-diagnostic/result.json')['exitCode'] == 0
    assert read('file-input-diagnostic/result.json')['diagnosticOnly'] is True
    print('Weston dependency checkpoint: deterministic stock crash retained; patched sanitizer and release images render popup400/parent9600 pixels; Qt/font bytes unchanged; full304-record display gate pending; mirror acceptance pending')


if __name__ == '__main__':
    verify()
