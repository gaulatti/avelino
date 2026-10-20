#!/usr/bin/env python3
"""Verify native DateRangePicker observations without accepting Linux parity."""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/date-range-20261018'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = read('investigation.json')
    assert report['accepted'] is False and report['reference'] == REFERENCE
    assert report['status'] == 'native investigation; Linux implementation pending'
    assert report['expectedImagesChanged'] is False and report['tolerance'] == 'none'
    assert report['approvedExceptions'] == [] and report['desktopCandidateCoverage'] == [76, 80]
    assert report['acceptedDesktopEntries'] == 0
    files = read('files.json')
    assert set(files) == {str(path.relative_to(DIRECTORY)) for path in DIRECTORY.rglob('*')
        if path.is_file() and path.name != 'files.json'}
    for name, row in files.items():
        path = DIRECTORY / name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name
    environment = read('environment.json')
    assert '27.0' in environment['macOS'] and '26A428' in environment['macOS']
    assert environment['sdk'] == '27.0' and environment['architecture'] == 'arm64'
    identity = read('provenance/source-identity.json')
    hero = json.loads((ROOT / 'evidence/reference-investigations/hero-carousel-20261018/provenance/source-identity.json').read_text())
    source = {row['path']: row['sha256'] for row in identity['fullSourceFiles']}
    assert len(source) == 89 and source == {row['path']: row['sha256'] for row in hero['files']}
    assert len(identity['scopedFiles']) == 53
    assert all(source[row['path']] == row['sha256'] for row in identity['scopedFiles'])
    fixtures = read('fixtures.json')
    by_id = {row['id']: {k: v for k, v in row.items() if v is not None} for row in fixtures}
    assert len(fixtures) == len(by_id) == report['summary']['fixtures'] == 48
    contexts = set(itertools.product(by_id, ['light', 'dark'], [1, 1.5], [1, 2]))
    captures = read('output/captures.json')
    rows = captures['rows']
    assert captures['accepted'] is False and captures['reference'] == REFERENCE
    assert len(rows) == len(contexts) == report['summary']['closedContexts'] == 384
    assert {(row['configuration']['id'], row['appearance'], row['textScale'], row['dpr']) for row in rows} == contexts

    def controls(state):
        # Paths describe the helper's wrapper hierarchy; retain all native control
        # values and geometry, and preserve the complete raw paths in the record.
        return [{key: value for key, value in picker.items() if key != 'path'}
            for picker in state['nativeControls']['datePickers']]

    image_names = set()
    for row in rows:
        assert row['configuration'] == by_id[row['configuration']['id']] and row['modes'] == [0, 1, 2]
        images = [(DIRECTORY / 'output' / name).read_bytes() for name in row['paths']]
        image_names.update(row['paths'])
        assert len(images) == 3 and images[0] == images[1] == images[2]
        assert row['publicLiteralIdentical'] is row['publicProbedIdentical'] is True
        assert all(struct.unpack('>II', raw[16:24]) == (640 * row['dpr'], 400 * row['dpr']) for raw in images)
        public, probed, literal = row['states']
        assert public['model'] == probed['model'] == literal['model']
        assert controls(public) == controls(probed) == controls(literal)
        assert all(probed['frames'][name] == literal['frames'][name] for name in ['picker', 'caller'])
        for state in row['states']:
            assert state['windowVisible'] is True and state['windowKey'] is state['applicationActive'] is False
            assert state['backingDpr'] == 2 and state['accessibility']['truncated'] is False
            assert state['model']['requests'] == [] and state['model']['pending'] == {}
            assert len(controls(state)) == 2
            for endpoint, picker in zip(['start', 'end'], controls(state)):
                value = state['model'][endpoint]
                if 'lower' in row['configuration']:
                    value = max(row['configuration']['lower'], min(row['configuration']['upper'], value))
                assert picker['date'] == value
    assert image_names == {path.name for path in (DIRECTORY / 'output').glob('*.png')}
    assert len(image_names) == report['summary']['closedImages'] == 1152
    sizing = read('sizing-output/sizing.json')
    assert sizing['accepted'] is False and sizing['reference'] == REFERENCE and len(sizing['rows']) == 384
    assert {(row['configuration']['id'], row['appearance'], row['textScale'], row['dpr']) for row in sizing['rows']} == contexts
    queries = 0
    for row in sizing['rows']:
        assert row['configuration'] == by_id[row['configuration']['id']]
        modes = row['modes']
        assert [mode['mode'] for mode in modes] == [0, 1, 2]
        assert modes[0]['proposals'] == modes[1]['proposals'] == modes[2]['proposals']
        for mode in modes:
            assert len(mode['proposals']) == 15
            assert mode['backingDpr'] == 2 and mode['windowKey'] is mode['applicationActive'] is False
            queries += len(mode['proposals'])
    assert queries == report['summary']['sizingQueries'] == 17280
    histories = read('history-output/histories.json')
    assert histories['accepted'] is False and histories['reference'] == REFERENCE
    assert [mode['mode'] for mode in histories['modes']] == [0, 1, 2]
    comparisons = []
    history_images = set()
    instances = [[1, 2]] * 3 + [[3, 4]] * 2 + [[5, 6]] * 9 + [[7, 8], [9, 10], [11, 12]]
    for ordinal, steps in enumerate(zip(*(mode['steps'] for mode in histories['modes']))):
        assert len({row['step'] for row in steps}) == 1
        images = [(DIRECTORY / 'history-output' / row['path']).read_bytes() for row in steps]
        history_images.update(row['path'] for row in steps)
        checks = dict(step=steps[0]['step'], pixelsEqual=images[0] == images[1] == images[2],
            modelEqual=steps[0]['state']['model'] == steps[1]['state']['model'] == steps[2]['state']['model'],
            nativeControlsEqual=controls(steps[0]['state']) == controls(steps[1]['state']) == controls(steps[2]['state']),
            nativeInstancesEqual=steps[0]['nativeInstances'] == steps[1]['nativeInstances'] == steps[2]['nativeInstances'])
        assert all(value is True for key, value in checks.items() if key != 'step')
        comparisons.append(checks)
        for row in steps:
            assert [value['instance'] for value in row['nativeInstances']] == instances[ordinal]
            model = row['state']['model']
            assert model['requests'] == [] and model['wrapperInstances'] == ([1] * 14 + [2, 3, 4])[ordinal]
    assert len(comparisons) == report['summary']['typedHistorySteps'] == 17
    assert read('history-branch-comparison.json')['results'] == comparisons
    assert len(history_images) == report['summary']['typedHistoryImages'] == 51
    assert history_images == {path.name for path in (DIRECTORY / 'history-output').glob('*.png')}
    replay = read('source-only-replay/comparison.json')
    assert replay['accepted'] is replay['independentMachine'] is False
    assert replay['exactFiles'] == len(replay['files']) == report['summary']['sourceOnlyExactReplayFiles'] == 1206
    assert replay['sourceFilesUnchanged'] == 89
    for name, checksum in replay['files'].items():
        assert digest(DIRECTORY / name) == checksum, name
    assert read('source-only-replay/replay-result.json')['exitCode'] == 0
    artifact = read('source-only-replay/artifact.json')
    assert artifact == report['sourceOnlyArtifact'] and artifact['compiledOutputs'] is False
    assert artifact['pinnedSourceFiles'] == 89 and artifact['independentMachineAvailability'] == 'pending'
    package = read('source-only-replay/package-files.json')
    assert len(package) + 1 == artifact['files'] == 99
    assert {name.removeprefix('reference/'): row['sha256'] for name, row in package.items() if name.startswith('reference/')} == source
    helpers = read('provenance/helper-files.json')
    for filename, attempt in [('DateCommon.swift', 'native-v3'), ('DateMain.swift', 'native-v3'),
            ('DateSizing.swift', 'native-v3'), ('DateHistory.swift', 'history-v1')]:
        assert package['tool/' + filename]['sha256'] == helpers[attempt]['tool/' + filename]['sha256']
    assert read('attempts/native-v1/pilot-output-result.json')['exitCode'] == -5
    assert read('attempts/native-v1/pilot-sizing-result.json')['exitCode'] == -5
    assert b'unable to find bundle named Sabella_Sabella' in gzip.decompress((DIRECTORY / 'attempts/native-v1/pilot-output.log.gz').read_bytes())
    assert read('attempts/native-v4/history-commands.json')[0]['exitCode'] == 1
    for name in ['capture-result.json', 'sizing-result.json']:
        assert read('attempts/native-v3/' + name)['exitCode'] == 0
    for attempt in ['native-v2', 'native-v3', 'native-v4', 'history-v1', 'interactive-v1', 'interactive-v2']:
        assert all(row['exitCode'] == 0 for row in read('attempts/' + attempt + '/commands.json'))
    for attempt in ['interactive-v1', 'interactive-v2']:
        prefix = 'attempts/' + attempt + '/'
        assert read(prefix + 'termination.json')['processAbsent'] is True
        journal = read(prefix + 'output/journal.json')
        assert journal['accepted'] is False and journal['actions'] == [] and journal['records']
        for row in journal['records']:
            state = row['state']
            assert state['model']['requests'] == [] and state['windowKey'] is state['applicationActive'] is False
            assert (DIRECTORY / prefix / 'output' / row['image']).is_file()
    assert read('attempts/interactive-v2/launch-observation.json')['nativeInputObserved'] is False
    final = read('attempts/interactive-v2/output/journal.json')['records'][-1]['state']

    def labels(value):
        return ([value['label']] if 'label' in value else []) + [label
            for child in value.get('children', []) for label in labels(child)]

    assert all(label in labels(final['windows'][0]['accessibility']['tree']) for label in ['From', 'To'])
    assert report['summary']['nativeOsInputObserved'] is report['summary']['independentMachine'] is False
    print('Native DateRangePicker: 384 closed contexts, 17280 sizing queries, 17 matching typed history steps and exact 1206-file source replay; native input and Linux acceptance pending')


if __name__ == '__main__':
    verify()
