#!/usr/bin/env python3
"""Verify the controlled native-window replay, preserving original captures."""
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/reference-investigations/admin-shell-context-20261020'
ORIGINAL = ROOT / 'evidence/reference-investigations/desktop-shell-host-20261019/run-v2/output'


def verify():
    read = lambda n: json.loads((CAPSULE / n).read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    files = read('files.json')
    assert set(files) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*')
                          if p.is_file() and p != CAPSULE / 'files.json'}
    relative = CAPSULE.relative_to(ROOT)
    tracked = set(subprocess.check_output(['git', 'ls-files', '--', str(relative)], cwd=ROOT, text=True).splitlines())
    assert tracked == {str(relative / n) for n in files} | {str(relative / 'files.json')}
    for name, checksum in files.items():
        assert sha(CAPSULE / name) == checksum, name
        staged = subprocess.check_output(['git', 'show', ':' + str(relative / name)], cwd=ROOT)
        assert hashlib.sha256(staged).hexdigest() == checksum, name
    assert subprocess.check_output(['git', 'show', ':' + str(relative / 'files.json')], cwd=ROOT) == (CAPSULE / 'files.json').read_bytes()
    reference = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    inputs, result = read('inputs.json'), read('result.json')
    assert inputs['reference'] == result['reference'] == reference['revision']
    assert inputs['sourceArchiveSha256'] == reference['sha256'] and inputs['pinnedSourceFiles'] == 53
    assert inputs['libraryObjectSha256'] == '0d98b215928f864cb6874be5426360db0861eb44a049af40e556aca9e319c025'
    assert inputs['helperSha256'] == result['helperSha256']
    assert inputs['reusedLibraryObject'] and not inputs['independentLibraryRebuild']
    assert result['exitCode'] == 0 and result['captures'] == 32
    assert all(result[k] is False for k in ['physicalInput', 'windowSessionObserved', 'accepted', 'fullMirrorAccepted'])
    assert read('compile-command.json')['exitCode'] == read('capture-command.json')['exitCode'] == 0
    data = read('output/measurements.json')
    assert data['reference'] == reference['revision'] and len(data['records']) == 16
    assert data['physicalInput'] is data['screenCapture'] is data['accepted'] is False
    profile_sha = inputs['captureProfileSha256']
    assert inputs['requestedWindowAppearance'] == 'NSAppearanceNameAqua'
    assert profile_sha == 'afe1e8628a1aaa5b7de0bb8984deabf259713fdb8d28a89e3e1c8f4c1d83eab5'
    seen = set()
    for row in data['records']:
        assert row['visible'] is row['key'] is False
        assert row['windowAppearance'] == 'NSAppearanceNameAqua'
        assert row['requestedCaptureProfileSha256'] == row['windowColorSpaceProfileSha256'] == profile_sha
        for suffix, checksum in [('.png', row['contentSha256']), ('-chrome.png', row['chromeSha256'])]:
            name = row['name'] + suffix
            actual, expected = CAPSULE / 'output' / name, ORIGINAL / name
            assert sha(actual) == checksum == sha(expected)
            assert actual.read_bytes() == expected.read_bytes()
            with Image.open(actual) as image:
                image.load()
                assert hashlib.sha256(image.info['icc_profile']).hexdigest() == profile_sha
            seen.add(name)
    assert seen == {p.name for p in (CAPSULE / 'output').glob('*.png')} and len(seen) == 32
    comparison = read('all-record-comparison.json')
    assert comparison['controls'] == comparison['pixelIdentities'] == comparison['byteIdentities'] == 32
    assert comparison['existingExpectedImagesChanged'] is comparison['physicalInput'] is comparison['accepted'] is False
    assert {r['path'] for r in comparison['rows']} == seen
    assert all(r['pixelIdentical'] and r['bytesIdentical'] and r['bounds'] is None for r in comparison['rows'])
    return dict(originalBodyAndChromeIdentities=32, explicitAppearance='NSAppearanceNameAqua',
                captureProfileSha256=profile_sha, expectedImagesChanged=False,
                independentLibraryRebuild=False, physicalInput=False, accepted=False)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
