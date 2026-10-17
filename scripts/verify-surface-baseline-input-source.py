#!/usr/bin/env python3
"""Audit native surface guide/input observations without accepting Linux parity."""
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import struct
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/surface-baseline-input-20261016'
spec = importlib.util.spec_from_file_location('surface_baseline_contexts', ROOT / 'scripts/verify-surface-modifier-source.py')
contexts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contexts)
REFERENCE = contexts.REFERENCE
ARCHIVE_SHA256 = 'f96f59a0551ddd8793344949ca75c677e0a364475a0746ac44ecf1ad1bd80cdb'
INPUTS = {'README.md': '86eb626f08bc89df114fded33a2ee90643dd3d04b26e41ecc52905f9b099df75',
 'reference-source.tar': '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c',
 'replay.py': '8cdb63749e0c6076c0eb5df4d6bf64c1ee9542d1248acc00d592c8ec2299c8dc',
 'tool/BaselineMain.swift': 'd546c38e03a6067123345e95c67c657d5a20e1c8b5f76e128681097943cb8d72',
 'tool/Common.swift': '68ac3466cfcc8a79fb87198562b8da270a98ea486524cc61404eb59e5a3a9e45',
 'tool/InputMain.swift': 'f07010121ca8743956ca69fdbc585cfda800b010dc301260b06f3870dd3d7274'}
MODES = ['public-unprobed', 'public-probed', 'literal-body-probed', 'bare-probed',
         'clip-only-probed', 'border-overlay-only-probed', 'literal-body-border-hit-testing-disabled-probed']
PENDING = ['linuxBaselines', 'linuxInput', 'raster', 'physicalDisplay', 'physicalInput', 'reader',
           'independentMachineArchive', 'nonfiniteInputs']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configurations():
    result = {name: dict(value, baselineParent=True, disabled=False, guide=None)
              for name, value in contexts.configurations().items()}
    for guide in [-5, 0, 42]:
        result[f'guide-{guide}'] = dict(result['default'], fixture=f'guide-{guide}', content='guide', guide=guide)
    assert len(result) == 55
    return result


def input_configurations():
    result = {}
    for content, radius, disabled in itertools.product(['input-filled', 'input-clear', 'input-overflow'],
                                                       [None, -12, 0, 12, 48, 500], [False, True]):
        name = f'{content}-radius{radius if radius is not None else "default"}-{"disabled" if disabled else "enabled"}'
        result[name] = dict(contexts.configurations()['default'], fixture=name, content=content,
                            radius=radius, resolvedRadius=12 if radius is None else radius,
                            baselineParent=False, disabled=disabled, guide=None)
    return result


def identity(row):
    return row['configuration']['fixture'], row['appearance'], row['textScale'], row['dpr']


def finite_rectangle(value):
    assert set(value) == {'x', 'y', 'width', 'height'}
    assert all(type(v) in [int, float] and math.isfinite(v) for v in value.values())
    assert value['width'] >= 0 and value['height'] >= 0


def guide_projection(row):
    """Keep exact size associations, unmatched proposals and unrequested guides explicit."""
    state = row['states'][1]
    result = {}
    for key, frames in state['partInstances'].items():
        queries = state['guideQueries'].get(key, [])
        associations = []
        used = []
        for frame in frames:
            matching = [q for q in queries if (q['width'], q['height']) == (frame['width'], frame['height'])]
            used.extend(matching)
            values = sorted({q['value'] for q in matching})
            associations.append(dict(frame=frame, values=values,
                                     status='unique' if len(values) == 1 else 'unrequested' if not values else 'ambiguous'))
        result[key] = dict(frames=associations, unmatchedQueries=[q for q in queries if q not in used])
    return dict(context=list(identity(row)), parts=result)


def sample_points(area):
    x, y, w, h = (area[key] for key in ['x', 'y', 'width', 'height'])
    points = []

    def add(a, b):
        if (a, b) not in points:
            points.append((a, b))

    add(x+w/2, y+h/2)
    for d in [-1, 0, .1, .5, 1, 2, 4, 8, 12, 16]:
        for a, b in [(x+d, y+d), (x+w-d, y+d), (x+d, y+h-d), (x+w-d, y+h-d),
                     (x+d, y+h/2), (x+w-d, y+h/2), (x+w/2, y+d), (x+w/2, y+h-d)]:
            add(a, b)
    for a in [-41, -40, -39, -20, -1, 0, 40, 80, 81, 100, 119, 120, 121]:
        add(x+a, y+h/2)
    for b in [-29, -28, -27, -14, -1, 0, 22, 44, 45, 58, 71, 72, 73]:
        add(x+w/2, y+b)
    return points


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['reference'] == REFERENCE and report['accepted'] is False
    assert report['expectedImagesChanged'] is False and report['approvedExceptions'] == []
    assert report['acceptanceGates'] == dict.fromkeys(PENDING, 'pending')
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert actual == set(report['files']) | {'investigation.json'}
    for name, expected in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == expected, name
    inputs, provenance = read('inputs.json'), read('tooling-provenance.json')
    assert inputs['reference'] == provenance['reference'] == REFERENCE
    assert inputs['files'] == provenance['inputs'] == INPUTS
    assert inputs['prebuiltLibraryInputs'] is False
    assert provenance['accepted'] is False and provenance['compiledInputs'] == []
    assert provenance['sourceOnlyReplayArchiveSha256'] == ARCHIVE_SHA256
    assert provenance['sourceOnlyReplayMembers'] == sorted([*INPUTS, 'inputs.json'])
    assert provenance['independentMachineAvailability'] == 'pending'
    archive = Path(provenance['sourceOnlyReplayArchive'])
    if archive.exists():
        assert digest(archive) == ARCHIVE_SHA256
        with tarfile.open(archive) as source:
            assert sorted(m.name for m in source) == provenance['sourceOnlyReplayMembers']
            for name, expected in INPUTS.items():
                assert hashlib.sha256(source.extractfile(name).read()).hexdigest() == expected
            assert json.loads(source.extractfile('inputs.json').read()) == inputs
    for prefix in ['', 'replay-build/']:
        build = read(prefix + 'source-build-result.json')
        assert build['reference'] == REFERENCE and build['sourceFilesUnchanged'] == 89
        assert build['sourceArchiveSha256'] == contexts.SOURCE_SHA256
        assert build['libraryBuiltFromSources'] is True and build['prebuiltLibraryInputs'] is False
        commands = read(prefix + 'commands.json')
        assert [r['log'] for r in commands] == ['library-build.log', 'baseline-build.log', 'baseline-run.log', 'input-build.log', 'input-run.log']
        for command in commands:
            assert command['exitCode'] == 0 and command['durationSeconds'] > 0
            assert prefix+command['log'] in report['files']
            assert isinstance(command['command'], list) and all(isinstance(v, str) for v in command['command'])
    used = set()

    def images(row, prefix, count):
        assert len(row['paths']) == len(set(row['paths'])) == count
        result = []
        for name in row['paths']:
            assert Path(name).name == name and name.endswith('.png')
            name = prefix + '/' + name
            assert name in report['files'] and name not in used
            used.add(name)
            data = (directory/name).read_bytes()
            assert data[:8] == b'\x89PNG\r\n\x1a\n'
            assert struct.unpack('>II', data[16:24]) == (640*row['dpr'], 400*row['dpr'])
            result.append(data)
        assert row['publicProbedIdentical'] is True and result[0] == result[1], 'Probe changes public pixels'
        assert row['publicWitnessIdentical'] is True and result[0] == result[2], 'Body witness changes public pixels'
        return result

    def states(values):
        for index, state in enumerate(values):
            assert state['actions'] == state['counter'] == state['disappearances'] == 0
            assert state['windowVisible'] is True and state['windowKey'] is state['applicationActive'] is False
            assert state['backingDpr'] == 2
            for frames in state['partInstances'].values():
                for frame in frames:
                    finite_rectangle(frame)
            if not index:
                assert state['partInstances'] == state['baselines'] == state['guideQueries'] == {}
        assert values[1] == values[2], 'Witness changes observed geometry/guides/state'

    baseline = read('baseline/baselines.json')
    assert baseline['reference'] == REFERENCE and baseline['complete'] is True and baseline['pilot'] is False
    assert baseline['fixtures'] == 55 and baseline['peakWindows'] == 1
    rows = baseline['captures']
    configs = configurations()
    assert len(rows) == len({identity(row) for row in rows}) == 440
    assert {identity(row) for row in rows} == set(itertools.product(configs, ['light', 'dark'], [1, 1.5], [1, 2]))
    projection = []
    for row in rows:
        assert row['configuration'] == configs[row['configuration']['fixture']]
        pngs = images(row, 'baseline', 4)
        assert row['publicBareIdentical'] is (pngs[0] == pngs[3])
        assert len(row['states']) == 4
        states(row['states'])
        measured = row['states'][1]
        assert 'baselineParent' not in measured['guideQueries']
        assert set(measured['baselines']) == set(measured['guideQueries'])
        for state in row['states']:
            empty = row['configuration']['content'] == 'empty'
            assert state['appearances'] == state['callerInstances'] == (0 if empty else 1)
        assert measured['partInstances'] == row['states'][3]['partInstances']
        for key, queries in measured['guideQueries'].items():
            assert queries and key in measured['partInstances']
            assert all(set(q) == {'width', 'height', 'value'} and all(math.isfinite(v) for v in q.values()) for q in queries)
        if row['configuration']['parentLayout'] != 'zstack':
            assert set(measured['guideQueries']) == {'parent', 'reference'}, 'Nested child guide was made explicit'
        marker = measured['partInstances']['reference'][0]
        assert marker['width'] == 3 and marker['height'] == 30
        assert measured['guideQueries']['reference'] == [dict(width=3, height=30, value=30)]
        parent = measured['partInstances']['baselineParent'][0]
        assert parent['x']+parent['width']/2 == 320 and parent['y']+parent['height']/2 == 200
        mapped = guide_projection(row)
        for key in measured['guideQueries']:
            assert all(part['status'] == 'unique' for part in mapped['parts'][key]['frames'])
        if row['configuration']['parentLayout'] == 'zstack':
            for part in mapped['parts'].get('root', {}).get('frames', []):
                assert part['status'] == 'unique'
                assert part['frame']['y']+part['values'][0] == marker['y']+30
        else:
            part = mapped['parts']['parent']['frames'][0]
            assert part['values'][0]+part['frame']['y'] == marker['y']+30
        if row['configuration']['guide'] is not None:
            assert mapped['parts']['caller']['frames'][0]['values'] == [row['configuration']['guide']]
        if row['configuration']['content'] == 'multi':
            assert len(measured['partInstances']['root']) == 2
            assert len(mapped['parts']['root']['frames']) == 2
        projection.append(mapped)
    assert read('guide-projection.json') == projection

    corpus = read('input/input.json')
    assert corpus['reference'] == REFERENCE and corpus['complete'] is True and corpus['pilot'] is False
    assert corpus['settleAfterMouseUpSeconds'] == .001 and corpus['modes'] == MODES
    assert corpus['peakWindows'] == 7
    configs = input_configurations()
    rows = corpus['profiles']
    assert len(rows) == len({identity(row) for row in rows}) == 288
    assert {identity(row) for row in rows} == set(itertools.product(configs, ['light', 'dark'], [1, 1.5], [1, 2]))
    total_samples = blocked = outside = 0
    for row in rows:
        assert row['configuration'] == configs[row['configuration']['fixture']]
        pngs = images(row, 'input', 7)
        assert pngs[0] == pngs[6], 'Disabling only border hit testing changed paint'
        assert len(row['initialStates']) == len(row['finalStates']) == len(row['samples']) == 7
        states(row['initialStates'])
        assert all(s == row['initialStates'][1] for s in row['initialStates'][1:])
        area = row['callerFrame']; finite_rectangle(area)
        overflow = row['configuration']['content'] == 'input-overflow'
        expected_area = dict(x=280, y=178, width=80, height=44) if overflow else dict(x=272, y=168, width=96, height=64)
        assert area == expected_area
        assert row['initialStates'][1]['partInstances']['caller'] == [area]
        points = sample_points(area)
        activations = []
        for mode, samples in enumerate(row['samples']):
            assert [(s['point']['x'], s['point']['y']) for s in samples] == points
            last = 0
            values = []
            for sample in samples:
                px, py = sample['point']['x'], sample['point']['y']
                inside = area['x'] <= px < area['x']+area['width'] and area['y'] <= py < area['y']+area['height']
                assert sample['insideCallerFrame'] is inside
                assert sample['beforeDown'] == sample['afterDown'] == last
                assert sample['activated'] in [0, 1]
                assert sample['afterUp'] == sample['afterSettle'] == last+sample['activated']
                last = sample['afterSettle']; values.append(sample['activated'])
            assert values[0] == (0 if row['configuration']['disabled'] else 1), 'Center activation/disabled behavior failed'
            if row['configuration']['disabled']:
                assert not any(values)
            final = dict(row['finalStates'][mode]); assert final.pop('actions') == last
            initial = dict(row['initialStates'][mode]); initial.pop('actions')
            assert final == initial, 'Synthetic clicks changed caller identity/layout/state'
            activations.append(values); total_samples += len(samples)
        assert activations[0] == activations[1] == activations[2] == activations[5], 'Border-only diagnostic does not reproduce public hit map'
        assert activations[3] == activations[4] == activations[6], 'Clip changes bare hit area or pass-through border still blocks'
        blocked += sum(a == 0 and b == 1 for a, b in zip(activations[0], activations[3]))
        outside += sum(s['activated'] for s in row['samples'][0] if not s['insideCallerFrame'])
    assert used == {name for name in report['files'] if name.endswith('.png') and name.split('/')[0] in ['baseline', 'input']}
    replay = read('clean-replay.json')
    outputs = {name for name in report['files'] if name.startswith(('baseline/', 'input/'))}
    assert replay['sourceOnlyRebuild'] is True and replay['files'] == replay['identicalFiles'] == len(outputs) == 3778
    assert {r['file'] for r in replay['outputs']} == outputs and len(replay['outputs']) == len(outputs)
    for value in replay['outputs']:
        assert value['identical'] is True
        assert value['originalSha256'] == value['replaySha256'] == digest(directory/value['file'])
    summary = dict(baselineGroups=440, inputProfiles=288, inputSamples=total_samples,
                   borderBlockedSamples=blocked, publicHitsOutsideCallerFrame=outside,
                   sourceReplayFiles=3778, accepted=False)
    assert report['summary'] == summary
    attempts = ['original-build', 'original-replay-build', 'corrected-build', 'corrected-replay-build']
    assert set(report['diagnosticArchives']) == {'diagnostics/original-baseline.tar.gz', 'diagnostics/pilots.tar.gz',
        *[f'diagnostics/partial-input-{name}.tar.gz' for name in attempts]}
    archived = {}
    for name, entry in report['diagnosticArchives'].items():
        assert digest(directory/name) == entry['sha256']
        with tarfile.open(directory/name) as source:
            members = source.getmembers()
            assert len(members) == len(entry['members']) and {m.name for m in members} == set(entry['members'])
            assert all(m.isfile() and Path(m.name).suffix in ['.json', '.png', '.log'] for m in members)
            assert all(not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in members)
            assert sum(m.size for m in members) < 64*1024*1024
            for member in members:
                data = source.extractfile(member).read()
                assert hashlib.sha256(data).hexdigest() == entry['members'][member.name]
                archived[(name, member.name)] = data
    original_archive = 'diagnostics/original-baseline.tar.gz'
    original = json.loads(archived[(original_archive, 'baselines.json')])
    assert len(original['captures']) == 440
    failure_names = {'parent-hstack', 'parent-vstack', 'multi-parent-vstack', 'text-parent-vstack'}
    expected_failures = set(itertools.product(failure_names, ['light', 'dark'], [1, 1.5], [1, 2]))
    failures, correction_rows = set(), []
    for before, after in zip(original['captures'], baseline['captures']):
        assert identity(before) == identity(after) and before['paths'] == after['paths']
        data = [archived[(original_archive, p)] for p in before['paths']]
        same = data[0] == data[1]
        assert before['publicProbedIdentical'] is same and before['publicWitnessIdentical'] is (data[0] == data[2])
        if not same:
            failures.add(identity(before))
        for mode, path in enumerate(before['paths']):
            fixed = (directory/'baseline'/path).read_bytes()
            identical = data[mode] == fixed
            assert identical is (mode == 0 or identity(before) not in expected_failures)
            correction_rows.append(dict(file='baseline/'+path, mode=mode,
                originalSha256=hashlib.sha256(data[mode]).hexdigest(), correctedSha256=hashlib.sha256(fixed).hexdigest(), identical=identical))
    assert failures == expected_failures
    correction = read('diagnostics/probe-correction.json')
    assert correction['accepted'] is False and correction['publicProbeFailures'] == 32
    assert {tuple(c) for c in correction['contexts']} == expected_failures and len(correction['contexts']) == 32
    assert correction['unchangedPublicImages'] == 440 and correction['changedProbedImages'] == 32
    assert correction['images'] == correction_rows
    for name, original_bytes in [('original-baseline-clean-replay.json', True), ('corrected-baseline-clean-replay.json', False)]:
        old_replay = read('diagnostics/'+name)
        assert old_replay['sourceOnlyRebuild'] is True
        assert old_replay['files'] == old_replay['identicalFiles'] == len(old_replay['outputs']) == 1761
        assert {r['file'] for r in old_replay['outputs']} == {p.removeprefix('baseline/') for p in outputs if p.startswith('baseline/')}
        for value in old_replay['outputs']:
            expected = (hashlib.sha256(archived[(original_archive, value['file'])]).hexdigest()
                        if original_bytes else digest(directory/'baseline'/value['file']))
            assert value['identical'] is True and value['originalSha256'] == value['replaySha256'] == expected
    old_provenance = read('diagnostics/original-build/tooling-provenance.json')
    assert old_provenance['sourceOnlyReplayArchiveSha256'] == 'e26d10b3eaab656bf62ca9508546e104faeb67edc3772fa8f686079295043695'
    assert old_provenance['accepted'] is False and old_provenance['compiledInputs'] == []
    resources = read('diagnostics/resource-attempts.json')
    assert resources['accepted'] is False
    assert [row['directory'] for row in resources['attempts']] == attempts
    for attempt in resources['attempts']:
        prefix = 'diagnostics/'+attempt['directory']+'/'
        commands, proof, termination = [read(prefix+n) for n in ['commands.json', 'source-audit.json', 'resource-termination.json']]
        assert [r['exitCode'] for r in commands] == [0, 0, 0, 0, -15]
        assert proof['reference'] == REFERENCE and proof['sourceArchiveSha256'] == contexts.SOURCE_SHA256
        assert proof['sourceFilesUnchanged'] == 89 and proof['libraryBuiltFromSources'] is True
        assert proof['prebuiltLibraryInputs'] is False and proof['baselineComplete'] is True
        assert proof['inputComplete'] is proof['captureComplete'] is False
        assert proof['nativeInputExitCode'] == -15 and proof['replayRunnerExitCode'] == 241
        assert termination['signal'] == 'SIGTERM' and termination['signalNumber'] == 15
        assert termination['inputCorpusComplete'] is False and termination['baselineOutputs'] == 1761
        assert attempt['inputComplete'] is False
        archive_name = attempt['partialInputArchive']
        assert archive_name == 'diagnostics/partial-input-'+attempt['directory']+'.tar.gz'
        members = report['diagnosticArchives'][archive_name]['members']
        assert attempt['partialInputImages'] == len(attempt['comparisons']) == len(members) > 0
        assert {r['file'] for r in attempt['comparisons']} == set(members)
        for value in attempt['comparisons']:
            assert Path(value['file']).suffix == '.png'
            partial = hashlib.sha256(archived[(archive_name, value['file'])]).hexdigest()
            final = digest(directory/'input'/value['file'])
            assert value['partialSha256'] == partial and value['finalSha256'] == final
            assert value['identical'] is (partial == final)
    pilot_archive = 'diagnostics/pilots.tar.gz'
    pilot_provenance = read('diagnostics/pilot-provenance.json')
    assert pilot_provenance['accepted'] is False and pilot_provenance['prebuiltLibraryInputs'] is True
    snapshots = pilot_provenance['sourceSnapshots']
    assert snapshots['accepted'] is False and snapshots['independentMachineAvailability'] == 'pending'
    assert snapshots['archiveSha256'] == '5fc5baa803b1db0ff4f8bb20f73e0a91d90b04f53ed6aa63d9dca86941bde251'
    assert len(snapshots['prebuiltLibraryInputs']) == 1
    expected_sources = {attempt+'/'+name: value for attempt, entry in pilot_provenance['attempts'].items()
                        for name, value in entry['sources'].items()}
    assert snapshots['members'] == expected_sources and len(expected_sources) == 9
    snapshot_archive = Path(snapshots['archive'])
    if snapshot_archive.exists():
        assert digest(snapshot_archive) == snapshots['archiveSha256']
        with tarfile.open(snapshot_archive) as source:
            assert {m.name for m in source} == set(expected_sources)
            assert all(hashlib.sha256(source.extractfile(n).read()).hexdigest() == h for n, h in expected_sources.items())
    for version, exits in [(1, [1]), (2, [0, 0, 0, 0]), (3, [0, 0])]:
        commands = json.loads(archived[(pilot_archive, f'diagnostic-pilot-v{version}/result.json')])
        assert [r['exitCode'] for r in commands] == exits
        assert all(r['diagnosticOnly'] is r['prebuiltLibraryInputs'] is True for r in commands)
    return summary


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
