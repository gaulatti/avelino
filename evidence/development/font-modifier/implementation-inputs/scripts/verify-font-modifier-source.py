#!/usr/bin/env python3
"""Audit the native font-modifier corpus without accepting Linux parity."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/font-modifier-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
SOURCE_SHA256 = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
ARCHIVE_SHA256 = 'a4c4723f86124a6231c0e64fedf9eccdd014f038fd1af030200644fd4e65d5ce'
INPUTS = {
    'README.md': '26d52151c64c4a61b597bd6074040ce05c74983adddfe89c1dc1f5746be54f58',
    'reference-source.tar': SOURCE_SHA256,
    'replay.py': 'fe227980de468207dc6af4c640e83da56a92c738b06971863e9dac8a1976a150',
    'tool/CaptureMain.swift': '1588bfa45542ac1abddf3c385877e0a379e73d47b32b5270b1f036f1754a9848',
    'tool/Common.swift': 'f90c5a8eaf37a04945436c51d7e0dbd065198e16c602d211c9dddc616e924a27',
}
FAMILIES = ['primary', 'secondary', 'mono']
WEIGHTS = ['ultraLight', 'thin', 'light', 'regular', 'medium', 'semibold', 'bold', 'heavy', 'black']
SIZES = [0.0, .11, .49, .5, 1.0, 12.25, 12.49, 12.5, 13.0, 13.5, 14.49, 14.5, 16.5, 24.0, 48.0]
CONTENTS = ['empty-view', 'zero', 'rectangle', 'hidden', 'own-font', 'system-font', 'nil-font',
            'red', 'bold', 'italic', 'attributed', 'nested-font', 'inner-scale', 'scaled-subtree',
            'multi', 'vstack', 'hstack']
POSTSCRIPT = {
    'primary': dict(zip(WEIGHTS, ['EncodeSans-' + suffix for suffix in
                                 ['Th', 'XLt', 'Lt', 'Regular', 'Md', 'SmBold', 'Bold', 'XBd', 'Black']])),
    'secondary': dict(zip(WEIGHTS, ['LibreFranklin-' + suffix for suffix in
                                   ['Thin', 'ExtraLight', 'Light', 'Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black']])),
    'mono': dict(zip(WEIGHTS, ['.AppleSystemUIFontMonospaced-' + suffix for suffix in
                              ['Light', 'Light', 'Light', 'Regular', 'Medium', 'Semibold', 'Bold', 'Heavy', 'Heavy']])),
}


def configurations():
    result = {}

    def add(name, **updates):
        result[name] = dict(fixture=name, family='primary', weight='regular', size=14, content='text',
                            text='Keep edition', parentLayout='zstack', offer=None, parentFont=False,
                            outerSystem=False, outerFontModifier=False, rtl=False, width=640, height=400)
        result[name].update(updates)

    for family, weight in itertools.product(FAMILIES, WEIGHTS):
        add(f'{family}-{weight}', family=family, weight=weight)
    for family, size in itertools.product(FAMILIES, SIZES):
        add(f'size-{family}-{size}', family=family, size=size)
    for content in CONTENTS:
        add('content-' + content, content=content)
    for name, text in [('empty', ''), ('lines', 'Keep edition\nReview result'),
                       ('long', 'Keep the selected edition available for review and verify its delivery settings.'),
                       ('unicode', 'Café é Å 𝟙'), ('bidi', 'الإصدار العربية עברית')]:
        add('text-' + name, text=text)
    for width in [0, 40, 80, 160, 400, 800]:
        add(f'offer-{width}', offer=width)
    add('rtl', rtl=True)
    add('parent-font32', parentFont=True)
    add('outer-system32', outerSystem=True)
    add('outer-font-modifier32', outerFontModifier=True)
    for parent in ['hstack', 'vstack']:
        add('parent-' + parent, parentLayout=parent)
        add('multi-parent-' + parent, parentLayout=parent, content='multi')
    assert len(result) == 108
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['referenceRevision'] == REFERENCE and report['accepted'] is False
    assert report['linuxImplementation'] == 'pending'
    assert report['approvedExceptions'] == [] and report['expectedImagesChanged'] is False
    for gate in ['physicalDisplayAcceptance', 'screenReaderAcceptance', 'nativeAccessibilityAcceptance',
                 'negativeNonfiniteSizeAcceptance', 'independentMachineAvailability',
                 'firstBaselineAcceptance', 'dynamicTypeAndLegibilityAcceptance']:
        assert report[gate] == 'pending', gate
    assert report['baselineScope'] == 'Centered layouts never requested the first-baseline guide; all baseline maps are empty and untrusted'
    files = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert files == set(report['files']) | {'investigation.json'}, 'Missing or extra evidence'
    for name, expected in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == expected, name
    inputs, build, provenance = (read(name) for name in ['inputs.json', 'source-build-result.json', 'tooling-provenance.json'])
    assert inputs['reference'] == build['reference'] == provenance['reference'] == REFERENCE
    assert inputs['files']['reference-source.tar'] == build['sourceArchiveSha256'] == SOURCE_SHA256
    assert inputs['files'] == INPUTS
    assert inputs['compiledInputs'] == provenance['compiledInputs'] == []
    assert build['sourceFilesUnchanged'] == 89 and build['libraryBuiltFromSources'] is True
    assert build['prebuiltLibraryInputs'] is False
    assert provenance['accepted'] is False and provenance['independentMachineAvailability'] == 'pending'
    assert provenance['sourceOnlyReplayArchiveSha256'] == ARCHIVE_SHA256
    assert provenance['sourceOnlyReplayMembers'] == sorted([*inputs['files'], 'inputs.json'])
    archive = Path(provenance['sourceOnlyReplayArchive'])
    if archive.exists():
        assert digest(archive) == ARCHIVE_SHA256
        with tarfile.open(archive) as source:
            assert sorted(m.name for m in source) == provenance['sourceOnlyReplayMembers']
            for name, expected in inputs['files'].items():
                assert hashlib.sha256(source.extractfile(name).read()).hexdigest() == expected

    corpus = read('captures/captures.json')
    assert corpus['reference'] == REFERENCE and corpus['fixtures'] == 108 and corpus['peakWindows'] == 1
    configs = configurations()
    identity = lambda row: (row['configuration']['fixture'], row['appearance'], row['textScale'], row['dpr'])
    rows = corpus['captures']
    lookup = {identity(row): row for row in rows}
    assert len(rows) == len(lookup) == report['closedGroups'] == 864
    assert set(lookup) == set(itertools.product(configs, ['light', 'dark'], [1, 1.5], [1, 2]))
    used_pngs = set()

    def image(name, dpr):
        relative = 'captures/' + name
        assert relative in files and relative.endswith('.png')
        used_pngs.add(relative)
        data = (directory / relative).read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II', data[16:24]) == (640 * dpr, 400 * dpr)
        return data

    def state(value):
        assert value['windowVisible'] and not value['windowKey'] and not value['applicationActive']
        assert value['backingDpr'] == 2
        for parts in value['partInstances'].values():
            assert parts == sorted(parts, key=lambda p: [p[k] for k in ['x', 'y', 'width', 'height']])
            for part in parts:
                assert set(part) == {'x', 'y', 'width', 'height'}
                assert all(math.isfinite(v) for v in part.values())
                assert part['width'] >= 0 and part['height'] >= 0
        assert value['baselines'] == {}, 'Centered layouts did not produce baseline evidence'

    def source_parts(config, observed, scale):
        parts = observed['partInstances']
        empty = config['content'] == 'empty-view'
        assert observed['appearances'] == observed['callerInstances'] == (0 if empty else 1)
        assert observed['disappearances'] == 0
        if empty:
            assert parts == observed['ambientFontsAtProbe'] == {}
            return
        multiple = config['content'] == 'multi'
        keys = {'first', 'second', 'styled', 'root'} if multiple else {'label', 'styled', 'root'}
        if config['content'] in ['hstack', 'vstack']:
            keys.update(['first', 'second'])
        if config['parentLayout'] != 'zstack':
            keys.update(['leading', 'trailing', 'parent'])
        assert set(parts) == set(observed['ambientFontsAtProbe']) == keys
        for key in keys:
            assert len(parts[key]) == (2 if multiple and key in ['styled', 'root'] else 1)
        emitted = sorted(parts['first'] + parts['second'], key=lambda p: [p[k] for k in ['x', 'y', 'width', 'height']]) if multiple else parts['label']
        assert parts['styled'] == emitted, 'Font modifier added a layout wrapper'
        for root, child in zip(parts['root'], parts['styled']):
            assert root['height'] == child['height'] and root['y'] == child['y']
            if config['offer'] is None:
                assert root == child
            else:
                assert root['width'] == config['offer']
                assert root['x'] + root['width'] / 2 == child['x'] + child['width'] / 2
        if config['parentLayout'] == 'zstack':
            assert all(p['x'] + p['width']/2 == 320 and p['y'] + p['height']/2 == 200 for p in parts['root'])
        else:
            participants = parts['leading'] + parts['root'] + parts['trailing']
            parent = parts['parent'][0]
            horizontal = config['parentLayout'] == 'hstack'
            ordered = sorted(participants, key=lambda p: p['x'] if horizontal else p['y'])
            axis, extent, other = ('x', 'width', 'height') if horizontal else ('y', 'height', 'width')
            assert parent[extent] == sum(p[extent] for p in ordered) + 11 * (len(ordered)-1)
            assert parent[other] == max(p[other] for p in ordered)
            assert ordered[0][axis] == parent[axis]
            assert all(a[axis] + a[extent] + 11 == b[axis] for a, b in zip(ordered, ordered[1:]))
            assert parent['x'] + parent['width']/2 == 320 and parent['y'] + parent['height']/2 == 200
        ambient_family, ambient_size, ambient_weight = config['family'], config['size'] * scale, config['weight']
        if config['content'] in ['nested-font', 'scaled-subtree']:
            ambient_family, ambient_size, ambient_weight = 'secondary', 19 * (2 if config['content'] == 'scaled-subtree' else scale), 'bold'
        expected_size = (ambient_size or 12) if ambient_family == 'mono' else (math.floor(ambient_size + .5) or 12)
        for key in ['first', 'second'] if multiple or config['content'] in ['hstack', 'vstack'] else ['label']:
            font = observed['ambientFontsAtProbe'][key]
            assert font['postScriptName'] == POSTSCRIPT[ambient_family][ambient_weight]
            assert font['resolvedPointSize'] == font['ctPointSize'] == expected_size

    for row in rows:
        config = row['configuration']
        assert config == configs[config['fixture']]
        assert row['publicProbedIdentical'] is True and row['publicWitnessIdentical'] is True
        assert len(row['paths']) == len(row['states']) == 3
        assert len({image(name, row['dpr']) for name in row['paths']}) == 1, 'Probe or witness changed public pixels'
        assert row['states'][1] == row['states'][2], 'Source-expression witness changed observed state'
        for observed in row['states']:
            state(observed)
        assert row['states'][0]['partInstances'] == row['states'][0]['baselines'] == row['states'][0]['ambientFontsAtProbe'] == {}
        source_parts(config, row['states'][1], row['textScale'])
        if config['fixture'] in ['parent-font32', 'outer-system32', 'outer-font-modifier32', 'content-inner-scale']:
            base = lookup[('primary-regular', row['appearance'], row['textScale'], row['dpr'])]
            assert image(row['paths'][0], row['dpr']) == image(base['paths'][0], row['dpr'])
        if config['content'] in ['own-font', 'system-font', 'nil-font', 'scaled-subtree']:
            base = lookup[(config['fixture'], row['appearance'], 1, row['dpr'])]
            assert image(row['paths'][0], row['dpr']) == image(base['paths'][0], row['dpr'])
            assert row['states'][1]['partInstances'] == base['states'][1]['partInstances']

    histories = corpus['histories']
    indexed = {(r['content'], r['dpr'], r['mode']): r for r in histories}
    assert len(histories) == len(indexed) == report['updateHistories'] == 24
    assert set(indexed) == set(itertools.product(['text', 'own-font', 'nested-font', 'multi'], [1, 2], [0, 1, 2]))
    for (content, dpr, mode), history in indexed.items():
        steps = history['steps']
        assert [s['step'] for s in steps] == list(range(7))
        for step in steps:
            state(step['state'])
            image(step['path'], dpr)
        for step in range(7):
            expected = dict(configs['primary-regular'], fixture='history-' + content, content=content)
            if step in [2, 3, 4, 5]:
                expected['family'] = 'secondary'
            if step in [3, 4, 5]:
                expected['size'] = 19.5
            if step in [4, 5]:
                expected['weight'] = 'black'
            assert steps[step]['configuration'] == expected
            assert steps[step]['textScale'] == (1.5 if step in [1, 2, 3, 4] else 1)
            other = indexed[(content, dpr, 0)]['steps'][step]
            assert image(steps[step]['path'], dpr) == image(other['path'], dpr)
            if mode:
                assert steps[step]['state'] == indexed[(content, dpr, 1)]['steps'][step]['state']
                source_parts(steps[step]['configuration'], steps[step]['state'], steps[step]['textScale'])
            assert steps[step]['state']['appearances'] == steps[step]['state']['callerInstances'] == 1
            assert steps[step]['state']['disappearances'] == 0
            if content == 'own-font':
                assert image(steps[step]['path'], dpr) == image(steps[0]['path'], dpr)
        assert image(steps[0]['path'], dpr) == image(steps[-1]['path'], dpr), 'Restoring source inputs changed pixels'

    assert used_pngs == {name for name in files if name.startswith('captures/') and name.endswith('.png')}
    assert len(used_pngs) == 2760
    replay = read('clean-replay.json')
    assert replay['files'] == replay['identicalFiles'] == len(replay['outputs']) == 2761
    assert replay['sourceOnlyRebuild'] is True
    assert {r['file'] for r in replay['outputs']} == {name.removeprefix('captures/') for name in files if name.startswith('captures/')}
    replay_build = read('replay-build/source-build-result.json')
    assert replay_build == build
    for row in replay['outputs']:
        assert row['identical'] is True and row['originalSha256'] == row['replaySha256'] == digest(directory / 'captures' / row['file'])
    return dict(closedGroups=864, updateHistories=24, sourceReplayFiles=2761, accepted=False)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
