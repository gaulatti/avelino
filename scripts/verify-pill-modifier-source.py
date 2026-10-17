#!/usr/bin/env python3
"""Audit native pill observations, meaningful histories and the unchanged-source replay."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/pill-modifier-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
STEPS = ['initial', 'text', 'appearance', 'text-scale', 'direction', 'restore']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configuration(value):
    return dict(value, offer=value.get('offer'), lineLimit=value.get('lineLimit'))


def context(row):
    return row['configuration']['id'], row['appearance'], row['textScale'], row['dpr']


def wrapper(state):
    assert (state['appearances'], state['disappearances'], state['wrapperInstances']) == (1, 0, 1)
    assert state['actions'] == 0
    assert state['windowVisible'] is True and state['windowKey'] is False
    assert state['applicationActive'] is False and state['backingDpr'] == 2
    assert set(state['guides']) == set(state['guideQueries'])
    for key, frames in state['parts'].items():
        assert key in ['root', 'styled', 'label', 'parent', 'reference', 'leading', 'trailing']
        assert len(frames) == 1
        frame = frames[0]
        assert set(frame) == {'x', 'y', 'width', 'height'}
        assert all(math.isfinite(value) for value in frame.values())
        assert frame['width'] >= 0 and frame['height'] >= 0
    for key, guide in state['guides'].items():
        frame = state['parts'][key][0]
        queries = {tuple(float(n) for n in value.split(',')) for value in state['guideQueries'][key]}
        assert all(len(value) == 3 and all(math.isfinite(n) for n in value) for value in queries)
        assert (frame['width'], frame['height'], guide) in queries


def verify(directory=DIRECTORY):
    from PIL import Image
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['reference'] == REFERENCE and report['accepted'] is False
    assert report['status'] == 'source-investigation; Linux implementation pending'
    assert report['expectedImagesChanged'] is False and report['approvedExceptions'] == []
    assert report['tolerance'] == 'none'
    assert report['remainingAcceptance'] == ['LinuxImplementation', 'nativeRasterFontsSymbols',
                                               'nativeInputTiming', 'physicalDisplaysInput', 'readers',
                                               'independentMachineReplayAvailability']
    assert set(report['files']) == {str(p.relative_to(directory)) for p in directory.rglob('*')
                                   if p.is_file() and p.name not in ['investigation.json', 'README.md']}
    for name, checksum in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == checksum, name
    all_rows = {}
    images = set()
    seen_names = set()
    baseline_groups = 0
    for folder, fixture_file, count in [('closed', 'fixtures.json', 91), ('empty', 'fixtures-empty.json', 20)]:
        fixtures = read(fixture_file)
        assert len(fixtures) == count and len({f['id'] for f in fixtures}) == count
        by_id = {f['id']: f for f in fixtures}
        data = read(folder + '/captures.json')
        assert data['complete'] is True and data['pilot'] is False and data['accepted'] is False
        assert data['reference'] == REFERENCE and data['fixtures'] == count
        assert len(data['captures']) == count * 8
        expected = set(itertools.product(by_id, ['light', 'dark'], [1, 1.5], [1, 2]))
        observed = set()
        for row in data['captures']:
            key = context(row)
            assert key not in observed and key not in all_rows
            observed.add(key)
            all_rows[key] = row
            fixture = configuration(row['configuration'])
            assert fixture == by_id[key[0]]
            assert len(row['paths']) == len(row['states']) == 4
            assert row['publicProbedIdentical'] is True and row['publicWitnessIdentical'] is True
            pngs = []
            for mode, (name, state) in enumerate(zip(row['paths'], row['states'])):
                assert name.endswith(f'-mode{mode}.png') and name not in seen_names
                seen_names.add(name)
                path = directory / folder / name
                with Image.open(path) as image:
                    assert image.size == (640 * row['dpr'], 400 * row['dpr'])
                pngs.append(path.read_bytes())
                images.add(folder + '/' + name)
                wrapper(state)
            assert pngs[0] == pngs[1] == pngs[2]
            plain, public, witness, bare = row['states']
            assert plain['parts'] == plain['guides'] == plain['guideQueries'] == {}
            assert {k: v for k, v in witness['parts'].items() if k != 'label'} == public['parts']
            label, styled = witness['parts']['label'][0], public['parts']['styled'][0]
            assert (styled['width'], styled['height']) == (label['width'] + 14, label['height'] + 8)
            assert (label['x'], label['y']) == (styled['x'] + 7, styled['y'] + 4)
            if fixture['parentLayout'] == 'baseline':
                baseline_groups += 1
                marker = public['parts']['reference'][0]
                assert (marker['width'], marker['height']) == (3, 30)
                assert set(public['guides']) == {'root', 'styled', 'reference'}
                assert public['guides']['styled'] == public['guides']['root'] == witness['guides']['label'] + 4
                root = public['parts']['root'][0]
                assert root['y'] + public['guides']['root'] == marker['y'] + 30
            else:
                assert public['guides'] == witness['guides'] == bare['guides'] == {}
            if fixture['text'] == '':
                assert (label['width'], label['height'], styled['width'], styled['height']) == (0, 14, 14, 22)
            if fixture['style'] in ['primary19', 'secondary19', 'mono3', 'mono32', 'system32', 'attributed']:
                own = bare['parts']['label'][0]
                assert (label['width'], label['height']) == (own['width'], own['height'])
        assert observed == expected
        assert {p.name for p in (directory / folder).glob('*.png')} == {name for r in data['captures'] for name in r['paths']}
    assert len(all_rows) == 888 and baseline_groups == 440
    scale_pairs = 0
    for key, row in all_rows.items():
        if key[2] != 1:
            continue
        scaled = all_rows[(key[0], key[1], 1.5, key[3])]
        folder = 'empty' if key[0].startswith(('empty-', 'baseline-empty-')) else 'closed'
        assert (directory / folder / row['paths'][0]).read_bytes() == (directory / folder / scaled['paths'][0]).read_bytes()
        scale_pairs += 1
    histories = read('histories/histories.json')
    assert histories['complete'] is True and histories['accepted'] is False and histories['reference'] == REFERENCE
    assert histories['fixtures'] == 7 and len(histories['histories']) == 56
    names = {'default', 'style-primary19', 'style-concat', 'offer-80', 'baseline-default',
             'baseline-style-primary19', 'baseline-style-concat'}
    observed_histories = set()
    for row in histories['histories']:
        key = context(row)
        assert key not in observed_histories
        observed_histories.add(key)
        assert [s['step'] for s in row['steps']] == STEPS
        fixture = configuration(row['configuration'])
        initial, text, theme, scale, direction, final = row['steps']
        for i, step in enumerate(row['steps']):
            assert step['publicProbedIdentical'] is True and step['publicWitnessIdentical'] is True
            assert len(step['paths']) == len(step['states']) == 3
            pngs = []
            for mode, (name, state) in enumerate(zip(step['paths'], step['states'])):
                wrapper(state)
                assert name.endswith(f'-step{i}-mode{mode}.png')
                path = directory / 'histories' / name
                images.add('histories/' + name)
                with Image.open(path) as image:
                    assert image.size == (640 * row['dpr'], 400 * row['dpr'])
                pngs.append(path.read_bytes())
                expected_fixture = dict(fixture)
                if i in [1, 2, 3, 4]:
                    expected_fixture['text'] += ' revised'
                if i == 4:
                    expected_fixture['rtl'] = not fixture['rtl']
                assert configuration(state['configuration']) == expected_fixture
                assert state['appearance'] == (('light' if row['appearance'] == 'dark' else 'dark') if i in [2, 3, 4] else row['appearance'])
                assert state['textScale'] == ((1.5 if row['textScale'] == 1 else 1) if i in [3, 4] else row['textScale'])
            assert pngs[0] == pngs[1] == pngs[2]
        # An input value changing in JSON is insufficient: the complete native view must change.
        first = directory / 'histories' / initial['paths'][0]
        changed = directory / 'histories' / text['paths'][0]
        with Image.open(first) as a, Image.open(changed) as b:
            assert a.convert('RGBA').tobytes() != b.convert('RGBA').tobytes()
        assert final['restoredInitialPixels'] is True
        for mode in range(3):
            assert (directory / 'histories' / final['paths'][mode]).read_bytes() == (directory / 'histories' / initial['paths'][mode]).read_bytes()
            assert final['states'][mode]['parts'] == initial['states'][mode]['parts']
            assert final['states'][mode]['guides'] == initial['states'][mode]['guides']
            assert (directory / 'histories' / scale['paths'][mode]).read_bytes() == (directory / 'histories' / theme['paths'][mode]).read_bytes()
    assert observed_histories == set(itertools.product(names, ['light', 'dark'], [1, 1.5], [1, 2]))
    assert {p.name for p in (directory / 'histories').glob('*.png')} == {n for r in histories['histories'] for s in r['steps'] for n in s['paths']}
    assert len(images) == 4560
    replay = read('clean-replay-comparison.json')
    assert replay['accepted'] is False and replay['identical'] is True and replay['files'] == 4563
    expected_outputs = images | {'closed/captures.json', 'empty/captures.json', 'histories/histories.json'}
    assert set(replay['hashes']) == expected_outputs
    for name, checksum in replay['hashes'].items():
        assert digest(directory / name) == checksum
    audit = read('source-audit.json')
    assert audit['sourceFilesUnchanged'] == 89 and audit['pinnedFilesUnchanged'] == 53
    expected_source = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']['files']
    assert all(audit['files'][r['path']] == r['sha256'] for r in expected_source)
    assert len(audit['files']) == 89
    for name in ['native-commands.json', 'clean-replay/commands.json']:
        commands = read(name)
        assert all(r['exitCode'] == 0 for r in commands)
    clean = read('clean-replay/commands.json')
    assert clean[0]['command'][:2] == ['swift', 'build']
    assert len(clean) == 6
    assert read('clean-replay/source-build-result.json')['prebuiltLibraryInputs'] is False
    api = read('api/results.json')
    assert [r['exitCode'] for r in api] == [0, 1, 1]
    assert [r['expectedExitCode'] for r in api] == [0, 1, 1]
    assert "cannot find 'BleeckerPillModifier' in scope" in (directory / 'api/private-type.swift.log').read_text()
    assert "has no member 'bleeckerPill'" in (directory / 'api/non-text.swift.log').read_text()
    diagnostics = read('diagnostic-comparison.json')
    assert diagnostics['accepted'] is False and diagnostics['originalReplayFiles'] == 4419
    assert diagnostics['closedAndEmptyImagesUnchanged'] == 3552
    assert diagnostics['unaffectedHistoryImagesUnchanged'] == 720
    assert diagnostics['originalConcatTextTraceEffective'] is False
    manifest = read('diagnostics-manifest.json')
    with tarfile.open(directory / 'diagnostics.tar.gz') as stream:
        members = stream.getmembers()
        assert len(members) == len(manifest) and {m.name for m in members} == set(manifest)
        for member in members:
            assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            raw = stream.extractfile(member).read()
            assert len(raw) == manifest[member.name]['bytes']
            assert hashlib.sha256(raw).hexdigest() == manifest[member.name]['sha256']
        original = json.loads(stream.extractfile('original-history/histories.json').read())
        corrected = {context(r): r for r in histories['histories']}
        unchanged = ineffective = 0
        for row in original['histories']:
            current = corrected[context(row)]
            if row['configuration']['id'] == 'style-concat':
                for mode in range(3):
                    before = stream.extractfile('original-history/' + row['steps'][0]['paths'][mode]).read()
                    after = stream.extractfile('original-history/' + row['steps'][1]['paths'][mode]).read()
                    assert before == after
                    ineffective += 1
                continue
            assert row == current
            for step in row['steps']:
                for name in step['paths']:
                    assert stream.extractfile('original-history/' + name).read() == (directory / 'histories' / name).read_bytes()
                    unchanged += 1
        assert (unchanged, ineffective) == (720, 24)
    summary = dict(closedFixtures=111, closedContexts=888, firstBaselineContexts=440,
                   historyFixtures=7, histories=56, historySteps=336, images=4560,
                   cleanReplayFiles=4563, textScalePublicPairsUnchanged=scale_pairs)
    assert summary == report['summary']
    return summary


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
