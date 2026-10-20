#!/usr/bin/env python3
"""Verify the pinned window capture context over the full native admin matrix."""
import hashlib
import io
import itertools
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/reference-investigations/admin-shell-pinned-matrix-20261020'
PRIOR = ROOT / 'evidence/reference-investigations/admin-shell-20261020/run-v3/output'
ORIGINAL = ROOT / 'evidence/reference-investigations/desktop-shell-host-20261019/run-v2/output'
PROFILE = 'afe1e8628a1aaa5b7de0bb8984deabf259713fdb8d28a89e3e1c8f4c1d83eab5'


def read(name):
    return json.loads((CAPSULE / name).read_text())


def digest(content):
    return hashlib.sha256(content).hexdigest()


def verify_members():
    files = read('files.json')
    actual = {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*')
              if p.is_file() and p != CAPSULE / 'files.json'}
    assert set(files) == actual
    relative = CAPSULE.relative_to(ROOT)
    expected = {str(relative / name) for name in files} | {str(relative / 'files.json')}
    entries = subprocess.check_output(['git', 'ls-files', '--stage', '-z', '--', str(relative)], cwd=ROOT)
    staged = {}
    for entry in filter(None, entries.split(b'\0')):
        metadata, name = entry.split(b'\t', 1)
        mode, object_id, stage = metadata.split()
        assert stage == b'0' and mode in [b'100644', b'100755']
        staged[name.decode()] = object_id.decode()
    assert set(staged) == expected, 'Every retained member must be in the Git index'
    objects = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                             input=('\n'.join(staged.values()) + '\n').encode(),
                             stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(objects.stdout)
    for name, object_id in staged.items():
        header = stream.readline().split()
        assert header[0].decode() == object_id and header[1] == b'blob'
        content = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and content == (ROOT / name).read_bytes(), name
        if name != str(relative / 'files.json'):
            assert digest(content) == files[str(Path(name).relative_to(relative))], name
    assert not stream.read()


def analyse():
    reference = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    provenance, inputs, result = read('provenance.json'), read('inputs.json'), read('result.json')
    assert reference['revision'] == provenance['reference'] == inputs['reference'] == result['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert reference['sha256'] == provenance['sourceArchiveSha256'] == inputs['sourceArchiveSha256']
    assert inputs['pinnedSourceFiles'] == provenance['pinnedSourceFiles'] == len(reference['files']) == 53
    assert inputs['libraryObjectSha256'] == provenance['libraryObjectSha256'] == '0d98b215928f864cb6874be5426360db0861eb44a049af40e556aca9e319c025'
    assert inputs['helperSha256'] == provenance['helperSha256'] == result['helperSha256']
    assert provenance['captureContext'] == dict(windowAppearance='NSAppearanceNameAqua', iccProfileSha256=PROFILE, ownedWindowsOnly=True)
    assert result['exitCode'] == 0 and result['captures'] == 1440
    assert inputs['captureProfileSha256'] == result['captureProfileSha256'] == PROFILE
    assert inputs['requestedWindowAppearance'] == result['requestedWindowAppearance'] == 'NSAppearanceNameAqua'
    assert inputs['reusedLibraryObject'] and provenance['reusedPinnedLibraryObject'] and result['reusedPinnedLibraryObject']
    for key in ['independentLibraryRebuild', 'independentMachineReplay', 'screenCapture', 'physicalInput',
                'expectedImagesChanged', 'referencePinsChanged', 'toolbarActivation', 'linuxCandidateAdded', 'accepted']:
        assert provenance[key] is False
    assert inputs['independentLibraryRebuild'] is False
    for key in ['physicalInput', 'windowSessionObserved', 'accepted', 'fullMirrorAccepted']:
        assert result[key] is False
    assert read('compile-command.json')['exitCode'] == read('capture-command.json')['exitCode'] == 0
    assert (CAPSULE / 'fixtures.json').read_bytes() == (PRIOR / 'fixtures.json').read_bytes()
    data, old = read('measurements.json'), json.loads((PRIOR / 'measurements.json').read_text())
    assert data['reference'] == reference['revision']
    for key in ['physicalInput', 'screenCapture', 'toolbarActionsPerformed', 'displayScaleOverride', 'accepted']:
        assert data[key] is False
    cases = {r['id'] for r in read('fixtures.json')}
    assert len(cases) == 20
    profiles = {(r['case'], r['dark'], r['initial'], r['measured']): r['state'] for r in data['profiles']}
    histories = {(r['owner'], r['initial'], r['measured']): r['states'] for r in data['histories']}
    assert len(data['profiles']) == len(profiles) == 160
    assert set(profiles) == set(itertools.product(cases, [False, True], [False, True], [False, True]))
    assert len(data['histories']) == len(histories) == 12
    assert set(histories) == set(itertools.product(['echo', 'ignore', 'delay'], [False, True], [False, True]))
    states = list(profiles.values()) + [s for h in histories.values() for s in h]
    old_states = [r['state'] for r in old['profiles']] + [s for h in old['histories'] for s in h['states']]
    assert len(states) == len(old_states) == 480
    index = read('images.json')
    dimensions, used = {}, set()
    for name in {r['stored'] for r in index.values()}:
        path = CAPSULE / name
        assert path.parent == CAPSULE / 'images' and path.suffix == '.png'
        content = path.read_bytes()
        assert digest(content) == path.stem
        with Image.open(io.BytesIO(content)) as image:
            image.load()
            assert image.format == 'PNG' and digest(image.info['icc_profile']) == PROFILE
            dimensions[name] = image.size
    assert set(dimensions) == {str(p.relative_to(CAPSULE)) for p in (CAPSULE / 'images').glob('*.png')}
    unchanged = ['step', 'navigation', 'requests', 'pending', 'lastLayoutFrames', 'bodyFramesFromGlobal',
                 'hostFrameInChrome', 'chromeBounds', 'chromeFlipped', 'hostOriginInWindowTop',
                 'arrangedSubviews', 'contentFrame', 'windowFrame', 'action']
    for row, prior in zip(states, old_states, strict=True):
        assert all(row[k] == prior[k] for k in unchanged)
        assert row['visible'] is row['key'] is False and row['backingScaleFactor'] == 2
        assert row['windowAppearance'] == 'NSAppearanceNameAqua'
        assert row['requestedCaptureProfileSha256'] == row['windowColorSpaceProfileSha256'] == PROFILE
        assert row['measurementByteIdentity'] and row['before']['sha256'] == row['after']['sha256']
        for kind in ['before', 'after', 'chrome']:
            description = row[kind]
            item = index[description['path']]
            assert description['sha256'] == item['sha256'] == Path(item['stored']).stem
            assert item['bytes'] == (CAPSULE / item['stored']).stat().st_size
            assert dimensions[item['stored']] == (description['width'], description['height'])
            assert description['bitsPerSample'] == 8 and description['hasAlpha']
            used.add(description['path'])
    assert len(used) == len(index) == 1440
    for case, dark, initial in itertools.product(cases, [False, True], [False, True]):
        a, b = profiles[case, dark, initial, False], profiles[case, dark, initial, True]
        assert a['before']['sha256'] == b['before']['sha256']
        assert all(a[k] == b[k] for k in ['navigation', 'requests', 'pending', 'arrangedSubviews'])
    for owner, initial in itertools.product(['echo', 'ignore', 'delay'], [False, True]):
        a, b = histories[owner, initial, False], histories[owner, initial, True]
        assert len(a) == len(b)
        for x, y in zip(a, b, strict=True):
            assert x['before']['sha256'] == y['before']['sha256']
            assert all(x[k] == y[k] for k in ['step', 'navigation', 'requests', 'pending', 'arrangedSubviews'])
    controls = []
    for case, width in [('standard', 840), ('narrow', 360)]:
        for initial in [False, True]:
            original = ORIGINAL / f'admin-w{width}-{str(initial).lower()}-bare.png'
            current = CAPSULE / index[profiles[case, False, initial, False]['before']['path']]['stored']
            assert original.read_bytes() == current.read_bytes()
            with Image.open(original) as a, Image.open(current) as b:
                assert ImageChops.difference(a.convert('RGBA'), b.convert('RGBA')).getbbox(alpha_only=False) is None
            controls.append(dict(case=case, initial=initial, byteIdentical=True, pixelIdentical=True))
    return dict(auditedStates=480, decodedCaptures=1440, layoutAndCallbacksUnchangedStates=480,
                observationIdentityPairs=480, staticProbeIdentityPairs=80, pairedOwnerHistories=6,
                profileSha256=PROFILE, requestedWindowAppearance='NSAppearanceNameAqua',
                originalControlComparisons=controls, physicalInput=False, toolbarActivation=False,
                independentLibraryRebuild=False, linuxParityAccepted=False, accepted=False)


if __name__ == '__main__':
    verify_members()
    summary = analyse()
    assert summary == read('audit.json')
    print(json.dumps(summary, indent=2))
