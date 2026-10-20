#!/usr/bin/env python3
"""Audit native AdminShell observations without accepting Linux parity."""
import hashlib
import io
import itertools
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/reference-investigations/admin-shell-20261020'
CASES = {'standard', 'empty-sidebar', 'empty-header', 'empty-content', 'all-empty',
         'fixed-content', 'zero-content', 'zero-sidebar', 'zero-header',
         'flex-sidebar', 'flex-header', 'short', 'short-fixed', 'narrow',
         'narrow-fixed', 'fractional', 'sidebar-180', 'sidebar-460',
         'breakpoint-1', 'breakpoint-10000'}


def read(name):
    return json.loads((CAPSULE / name).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyse():
    reference = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    provenance = read('provenance.json')
    assert reference['revision'] == provenance['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert provenance['sourceArchiveSha256'] == reference['sha256']
    assert provenance['reusedPinnedLibraryObject']
    for key in ['independentLibraryRebuild', 'independentReplay', 'physicalInput',
                'screenCapture', 'existingExpectedImagesChanged', 'sourcePinsChanged', 'accepted']:
        assert provenance[key] is False
    index = read('images.json')
    dimensions = {}
    for name in {row['stored'] for row in index.values()}:
        path = CAPSULE / name
        assert path.parent == CAPSULE / 'images' and path.suffix == '.png'
        assert digest(path) == path.stem
        with Image.open(path) as image:
            assert image.format == 'PNG'
            image.load()
            dimensions[name] = image.size
    assert set(dimensions) == {str(p.relative_to(CAPSULE)) for p in (CAPSULE / 'images').glob('*.png')}
    used = set()
    state_count = metadata_pairs = static_pairs = history_pairs = viewport_frames = 0
    datasets = {}

    def state(version, row):
        nonlocal state_count, metadata_pairs, viewport_frames
        state_count += 1
        assert row['visible'] is row['key'] is False
        assert row['backingScaleFactor'] == 2
        for kind in ['before', 'after', 'chrome']:
            description = row[kind]
            logical = f'run-v{version}/output/' + description['path']
            item = index[logical]
            assert item['sha256'] == description['sha256'] == Path(item['stored']).stem
            assert (CAPSULE / item['stored']).stat().st_size == item['bytes']
            assert dimensions[item['stored']] == (description['width'], description['height'])
            assert description['bitsPerSample'] == 8 and description['hasAlpha']
            used.add(logical)
        assert row['measurementByteIdentity']
        assert row['before']['sha256'] == row['after']['sha256']
        assert (row['before']['width'], row['before']['height']) == (
            row['contentFrame']['width'] * 2, row['contentFrame']['height'] * 2)
        metadata_pairs += 1
        if version == 3:
            host, chrome = row['hostFrameInChrome'], row['chromeBounds']
            origin = dict(x=host['x'] - chrome['x'],
                          y=host['y'] - chrome['y'] if row['chromeFlipped'] else
                          chrome['y'] + chrome['height'] - host['y'] - host['height'])
            assert origin == row['hostOriginInWindowTop']
            assert set(row['bodyFramesFromGlobal']) == set(row['lastLayoutFrames'])
            for key, spaces in row['lastLayoutFrames'].items():
                frame = dict(spaces['global'])
                frame['x'] -= origin['x']
                frame['y'] -= origin['y']
                assert frame == row['bodyFramesFromGlobal'][key]
                viewport_frames += 1
        for action in [row['action']] if row['action'] else []:
            assert action['mechanism'] == 'NSSplitView.setPosition'
            assert action['physicalInput'] is False

    for version in [1, 2, 3]:
        prefix = f'run-v{version}'
        inputs, result = read(prefix + '/inputs.json'), read(prefix + '/result.json')
        record = next(r for r in provenance['runs'] if r['version'] == version)
        assert inputs['helperSha256'] == record['helperSha256']
        assert inputs['reference'] == reference['revision']
        assert inputs['sourceArchiveSha256'] == reference['sha256'] and inputs['pinnedSourceFiles'] == 53
        assert inputs['libraryObjectSha256'] == '0d98b215928f864cb6874be5426360db0861eb44a049af40e556aca9e319c025'
        assert inputs['reusedLibraryObject'] and not inputs['independentLibraryRebuild']
        if version == 1:
            assert result['exitCode'] == 1 and 'ActorIsolatedCall' in (CAPSULE / prefix / 'compile.log').read_text()
            continue
        assert result['exitCode'] == 0 and result['helperSha256'] == record['helperSha256']
        data = read(prefix + '/output/measurements.json')
        assert data['reference'] == reference['revision']
        for key in ['physicalInput', 'screenCapture', 'toolbarActionsPerformed', 'displayScaleOverride', 'accepted']:
            assert data[key] is False
        assert len(data['profiles']) == 160 and len(data['histories']) == 12
        profiles = {(r['case'], r['dark'], r['initial'], r['measured']): r['state'] for r in data['profiles']}
        assert set(profiles) == set(itertools.product(CASES, [False, True], [False, True], [False, True]))
        for row in profiles.values():
            state(version, row)
        for case, dark, initial in itertools.product(CASES, [False, True], [False, True]):
            bare, measured = profiles[(case, dark, initial, False)], profiles[(case, dark, initial, True)]
            assert bare['before']['sha256'] == measured['before']['sha256']
            assert bare['navigation'] == measured['navigation'] and bare['requests'] == measured['requests']
            assert bare['arrangedSubviews'] == measured['arrangedSubviews']
            static_pairs += 1
        histories = {(r['owner'], r['initial'], r['measured']): r['states'] for r in data['histories']}
        assert set(histories) == set(itertools.product(['echo', 'ignore', 'delay'], [False, True], [False, True]))
        for rows in histories.values():
            for row in rows:
                state(version, row)
        for owner, initial in itertools.product(['echo', 'ignore', 'delay'], [False, True]):
            bare, measured = histories[(owner, initial, False)], histories[(owner, initial, True)]
            assert [r['step'] for r in bare] == [r['step'] for r in measured]
            for a, b in zip(bare, measured, strict=True):
                assert a['before']['sha256'] == b['before']['sha256']
                assert all(a[k] == b[k] for k in ['navigation', 'requests', 'pending', 'arrangedSubviews'])
            history_pairs += 1
        assert result['captures'] == sum(k.startswith(prefix + '/') for k in index)
        datasets[version] = profiles, histories
    for logical, image in index.items():
        if logical.startswith('run-v2/'):
            assert image['sha256'] == index[logical.replace('run-v2/', 'run-v3/', 1)]['sha256']
    profiles, histories = datasets[3]
    sample = lambda case, initial=True: profiles[(case, False, initial, True)]
    assert sample('narrow')['bodyFramesFromGlobal']['root'] == dict(x=-60, y=0, width=480, height=500)
    assert sample('short')['bodyFramesFromGlobal']['root'] == dict(x=0, y=-49, width=840, height=122)
    assert sample('short-fixed')['bodyFramesFromGlobal']['root']['height'] == 137
    assert 'content' not in sample('empty-content')['bodyFramesFromGlobal']
    assert sample('empty-content')['bodyFramesFromGlobal']['header']['y'] == 231.5
    assert sample('zero-content')['bodyFramesFromGlobal']['content']['width'] == 0
    assert sample('zero-content')['bodyFramesFromGlobal']['header']['y'] == 0
    assert sample('empty-sidebar')['arrangedSubviews'][0]['frame']['width'] == 144
    assert sample('sidebar-180')['arrangedSubviews'][0]['frame']['width'] == 212
    assert sample('sidebar-460')['arrangedSubviews'][0]['frame']['width'] == 460
    for dark, initial in itertools.product([False, True], [False, True]):
        standard = profiles[('standard', dark, initial, False)]['before']['sha256']
        assert all(profiles[(case, dark, initial, False)]['before']['sha256'] == standard
                   for case in ['breakpoint-1', 'breakpoint-10000'])
    for owner, initial in itertools.product(['echo', 'ignore', 'delay'], [False, True]):
        rows = histories[(owner, initial, True)]
        collapsed = next(r for r in rows if r['step'] == 'divider-0')
        assert collapsed['arrangedSubviews'][0]['collapsed']
        assert collapsed['navigation'] == (owner != 'echo')
        if owner == 'delay':
            assert collapsed['pending'] is False
        assert next(r for r in rows if r['step'] == 'divider-700')['arrangedSubviews'][0]['frame']['width'] == 420
    replay_command = read('immutable-host-replay/command.json')
    old_result = json.loads((ROOT / 'evidence/reference-investigations/desktop-shell-host-20261019/run-v2/result.json').read_text())
    assert replay_command['exitCode'] == 0 and replay_command['recompiled'] is False
    assert replay_command['binarySha256'] == old_result['executableSha256']
    replay = read('immutable-host-replay/output/measurements.json')
    assert replay['reference'] == reference['revision'] and len(replay['records']) == 16
    for row in replay['records']:
        assert row['visible'] is row['key'] is False
        for suffix, checksum in [('.png', row['contentSha256']), ('-chrome.png', row['chromeSha256'])]:
            logical = 'immutable-host-replay/output/' + row['name'] + suffix
            item = index[logical]
            assert item['sha256'] == checksum == Path(item['stored']).stem
            used.add(logical)
    assert used == set(index)
    prior_controls = prior_equal = 0
    replay_controls = 0
    comparisons = []
    original_profiles = set()
    current_profiles = set()
    old = ROOT / 'evidence/reference-investigations/desktop-shell-host-20261019/run-v2/output'
    for case, width in [('standard', 840), ('narrow', 360)]:
        for initial in [False, True]:
            expected = old / f'admin-w{width}-{str(initial).lower()}-bare.png'
            description = profiles[(case, False, initial, False)]['before']
            current = CAPSULE / index['run-v3/output/' + description['path']]['stored']
            replayed = CAPSULE / index['immutable-host-replay/output/' + expected.name]['stored']
            with Image.open(expected) as a, Image.open(current) as b, Image.open(replayed) as r:
                original_profiles.add(hashlib.sha256(a.info.get('icc_profile', b'')).hexdigest())
                current_profiles.add(hashlib.sha256(b.info.get('icc_profile', b'')).hexdigest())
                assert hashlib.sha256(b.info.get('icc_profile', b'')).digest() == hashlib.sha256(r.info.get('icc_profile', b'')).digest()
                original_difference = ImageChops.difference(a.convert('RGBA'), b.convert('RGBA'))
                replay_difference = ImageChops.difference(r.convert('RGBA'), b.convert('RGBA'))
                assert replay_difference.getbbox(alpha_only=False) is None
                same = original_difference.getbbox(alpha_only=False) is None
                comparisons.append(dict(case=case, initial=initial, samePixels=same))
                prior_equal += same
                replay_controls += 1
            prior_controls += 1
    assert original_profiles != current_profiles
    assert prior_equal == 0 and replay_controls == 4
    return dict(staticProfilesPerRun=160, pairedOwnerHistoriesPerRun=6,
                auditedStates=state_count, observationIdentityPairs=metadata_pairs,
                staticIdentityPairs=static_pairs, historyIdentityPairs=history_pairs,
                viewportFrames=viewport_frames, originalCapturePaths=len(index),
                exactPngBlobs=len(dimensions), originalControlsCompared=prior_controls,
                originalControlsPixelIdentical=prior_equal, originalVisualContinuityPassed=False,
                immutableBinaryReplayPixelIdentities=replay_controls, captureIccProfileChanged=True,
                physicalInput=False, toolbarActivation=False, independentReplay=False,
                linuxCandidateAdded=False, accepted=False)


def verify():
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
    assert set(staged) == expected, 'Every capsule member must be staged in Git'
    objects = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                             input=('\n'.join(staged.values()) + '\n').encode(),
                             stdout=subprocess.PIPE, check=True)
    stream = io.BytesIO(objects.stdout)
    for name, object_id in staged.items():
        header = stream.readline().split()
        assert header[0].decode() == object_id and header[1] == b'blob'
        content = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        assert content == (ROOT / name).read_bytes(), name
        if name != str(relative / 'files.json'):
            assert hashlib.sha256(content).hexdigest() == files[str(Path(name).relative_to(relative))], name
    assert not stream.read()
    result = analyse()
    assert result == read('result.json')
    return result


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
