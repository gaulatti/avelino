#!/usr/bin/env python3
"""Verify native surface evidence without accepting a Linux implementation."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/surface-modifier-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
SOURCE_SHA256 = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
ARCHIVE_SHA256 = '8231f9c3aa6d771d92e33ac4ab78bf38d4da6268265799efb1ead14ac380641a'
INPUTS = {
    'reference-source.tar': SOURCE_SHA256,
    'replay.py': 'b2796cd6d9d04399d0ecba9ededa5d7e573a04ce7267e21ccd1deba426e687cc',
    'README.md': 'fad4cecc699c93b6fdac9a90d52865c8b47ac982eb2f7f502d509245216ccddf',
    'tool/Common.swift': 'eef1055a3761f2c2640c3a241b8ccb3042b4765e4b3fcacb16366870706d8da3',
    'tool/CaptureMain.swift': '810bfd7ff84f7f970013f283dddee5abead4ce307972caeced40ebb90e6a6fe2',
}
RADII = [-12.0, -1.0, 0.0, .11, .49, .5, 1.0, 3.0, 7.0, 12.0, 14.0, 24.0, 60.0, 500.0]
CONTENTS = ['rectangle', 'fractional', 'opaque', 'overflow', 'hidden', 'empty', 'zero', 'wide',
            'text', 'own-font', 'system-font', 'red', 'button', 'multi', 'hstack', 'vstack']
HISTORY_CONTENTS = ['clear', 'opaque', 'button', 'multi', 'hstack']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configurations():
    rows = {}

    def add(name, **values):
        row = dict(fixture=name, radius=None, resolvedRadius=12, content='clear', parentLayout='zstack',
                   text='Review edition', offer=None, rtl=False, parentFont=False, parentRed=False,
                   width=640, height=400)
        row.update(values)
        row['resolvedRadius'] = row['radius'] if row['radius'] is not None else 12
        rows[name] = row

    add('default')
    for radius in RADII:
        add(f'radius-{radius}', radius=radius)
    for content in CONTENTS:
        add('content-' + content, content=content)
    for offer in [0, 1, 40, 80, 160, 400, 800]:
        add(f'offer-{offer}', offer=offer)
    for name, text in [('empty', ''), ('lines', 'Review edition\nKeep result'),
                       ('long', 'Review the selected edition and verify its complete delivery settings.'),
                       ('unicode', 'Café é Å 𝟙'), ('bidi', 'الإصدار العربية עברית')]:
        add('text-' + name, content='text', text=text)
    add('rtl', content='opaque', rtl=True)
    add('parent-font32', content='text', parentFont=True)
    add('parent-red', content='text', parentRed=True)
    for layout in ['hstack', 'vstack']:
        add('parent-' + layout, parentLayout=layout)
        add('multi-parent-' + layout, parentLayout=layout, content='multi')
        add('text-parent-' + layout, parentLayout=layout, content='text')
    assert len(rows) == 52
    return rows


def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['accepted'] is False and report['reference'] == REFERENCE
    assert report['baselineScope'] == 'Centered layouts did not request text baselines; empty maps do not accept baseline behavior'
    assert report['acceptanceGates'] == {name: 'pending' for name in [
        'linux', 'nativeFirstBaselineLayouts', 'physicalDisplay', 'physicalInput',
        'reader', 'nonfiniteInputs', 'independentMachineArchive']}
    files = report['files']
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual == set(files) | {'investigation.json'}
    assert all(digest(directory / name) == expected for name, expected in files.items())
    inputs, provenance = read('inputs.json'), read('tooling-provenance.json')
    assert inputs['reference'] == provenance['reference'] == REFERENCE
    assert inputs['files'] == INPUTS and inputs['prebuiltLibraryInputs'] is False
    assert provenance['accepted'] is False and provenance['compiledInputs'] == []
    assert provenance['sourceOnlyReplayArchiveSha256'] == ARCHIVE_SHA256
    assert set(provenance['sourceOnlyReplayMembers']) == set(INPUTS) | {'inputs.json'}
    assert provenance['independentMachineAvailability'] == 'pending'
    archive = Path(provenance['sourceOnlyReplayArchive'])
    if archive.exists():
        assert digest(archive) == ARCHIVE_SHA256
        with tarfile.open(archive) as source:
            assert set(m.name for m in source) == set(INPUTS) | {'inputs.json'}
            for name, expected in INPUTS.items():
                assert hashlib.sha256(source.extractfile(name).read()).hexdigest() == expected
    for name in ['source-build-result.json', 'replay-build/source-build-result.json']:
        build = read(name)
        assert build['reference'] == REFERENCE and build['sourceFilesUnchanged'] == 89
        assert build['sourceArchiveSha256'] == SOURCE_SHA256
        assert build['libraryBuiltFromSources'] is True and build['prebuiltLibraryInputs'] is False

    api = read('api-check/result.json')
    assert api['accepted'] is False and api['reference'] == REFERENCE
    assert api['sourceArchiveSha256'] == SOURCE_SHA256
    assert api['moduleOrigin'] == 'Unchanged-source capture replay build'
    assert set(api['cases']) == {'public-type', 'public-view-extension', 'direct-initializer'}
    assert api['cases']['public-type']['exitCode'] == api['cases']['public-view-extension']['exitCode'] == 0
    assert api['cases']['direct-initializer']['exitCode'] != 0
    assert "inaccessible due to 'internal' protection level" in (directory / 'api-check/direct-initializer.log').read_text()
    assert {name: value['sourceSha256'] for name, value in api['cases'].items()} == {
        'public-type': '10caad195ffe6a5d7010353c4fe580ce9a083c1ca522d37366e71f5c7cf9c847',
        'public-view-extension': '3d9dfcf790ade5f5c2a93ed7f3f3882d77219222830ecabf85d02dc40dee3395',
        'direct-initializer': 'b015795c085b2105c59e38c33eedc1be5cea4ea9f8f4190fec6cf0126048ce42',
    }
    api_provenance = read('api-check/provenance.json')
    assert api_provenance['accepted'] is False
    assert api_provenance['archiveSha256'] == 'daf7fd1e39da4aa1ffa48e5cbfb2f8fcd63d7cba8e2b73b43bae66bff02e36f8'
    assert api_provenance['files'] == {
        'README.md': '4d42ae894adb3d8a1a3eb18d5fe91e0a006a3799c253abbd5586b0ddff1807d0',
        'audit.py': 'd7e0f6a6277a76b8e4d3751396c06d611c1986cd4a3b279a703fe19680a20c0b',
    }
    api_archive = Path(api_provenance['archive'])
    if api_archive.exists():
        assert digest(api_archive) == api_provenance['archiveSha256']
        with tarfile.open(api_archive) as source:
            assert set(m.name for m in source) == set(api_provenance['files'])
            for name, expected in api_provenance['files'].items():
                assert hashlib.sha256(source.extractfile(name).read()).hexdigest() == expected

    corpus = read('captures/captures.json')
    assert corpus['reference'] == REFERENCE and corpus['fixtures'] == 52 and corpus['peakWindows'] == 1
    configs = configurations()
    identity = lambda row: (row['configuration']['fixture'], row['appearance'], row['textScale'], row['dpr'])
    lookup = {identity(row): row for row in corpus['captures']}
    assert len(lookup) == len(corpus['captures']) == report['closedGroups'] == 416
    assert set(lookup) == set(itertools.product(configs, ['light', 'dark'], [1, 1.5], [1, 2]))
    used = set()

    def image(name, dpr):
        relative = 'captures/' + name
        assert relative in files and relative.endswith('.png')
        used.add(relative)
        data = (directory / relative).read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II', data[16:24]) == (640 * dpr, 400 * dpr)
        return data

    def state(value, config, probed=True):
        empty = config['content'] == 'empty'
        assert value['windowVisible'] and not value['windowKey'] and not value['applicationActive']
        assert value['backingDpr'] == 2
        assert value['appearances'] == value['callerInstances'] == (0 if empty else 1)
        assert value['disappearances'] == value['actions'] == value['counter'] == 0
        assert value['baselines'] == {}, 'Centered captures do not supply baseline measurements'
        parts = value['partInstances']
        if empty or not probed:
            assert parts == {}
            return
        multiple = config['content'] == 'multi'
        keys = {'first', 'second', 'styled', 'root'} if multiple else {'caller', 'styled', 'root'}
        if config['content'] in ['hstack', 'vstack']:
            keys.update(['first', 'second'])
        if config['parentLayout'] != 'zstack':
            keys.update(['leading', 'trailing', 'parent'])
        assert set(parts) == keys
        for key, values in parts.items():
            assert len(values) == (2 if multiple and key in ['styled', 'root'] else 1)
            assert values == sorted(values, key=lambda p: [p[k] for k in ['x', 'y', 'width', 'height']])
            for frame in values:
                assert set(frame) == {'x', 'y', 'width', 'height'}
                assert all(math.isfinite(v) for v in frame.values())
                assert frame['width'] >= 0 and frame['height'] >= 0
        emitted = sorted(parts['first'] + parts['second'], key=lambda p: [p[k] for k in ['x', 'y', 'width', 'height']]) if multiple else parts['caller']
        assert parts['styled'] == emitted, 'Surface modifier must decorate each flat caller separately'
        for outer, inner in zip(parts['root'], parts['styled']):
            assert outer['height'] == inner['height'] and outer['y'] == inner['y']
            assert outer['x'] + outer['width']/2 == inner['x'] + inner['width']/2
            assert outer['width'] == (inner['width'] if config['offer'] is None else config['offer'])

    for key, row in lookup.items():
        config = configs[key[0]]
        assert row['configuration'] == config
        assert row['publicProbedIdentical'] and row['publicWitnessIdentical']
        assert len(row['states']) == len(row['paths']) == 4
        images = [image(path, key[3]) for path in row['paths']]
        assert images[0] == images[1] == images[2]
        assert row['publicBareIdentical'] == (images[0] == images[3])
        for index, observed in enumerate(row['states']):
            state(observed, config, index != 0)
        assert row['states'][1] == row['states'][2] == row['states'][3]
    histories = corpus['histories']
    history_lookup = {(r['content'], r['dpr'], r['mode']): r for r in histories}
    assert len(histories) == len(history_lookup) == report['updateHistories'] == 30
    assert set(history_lookup) == set(itertools.product(HISTORY_CONTENTS, [1, 2], [0, 1, 2]))
    for (content, dpr, mode), history in history_lookup.items():
        steps = history['steps']
        assert [step['step'] for step in steps] == list(range(6))
        for step in steps:
            index = step['step'];config = dict(configs['default'], fixture='history-' + content, content=content)
            if index in [1, 2, 3, 4]:
                config['radius'] = 0 if index == 1 else 48
                config['resolvedRadius'] = config['radius']
            assert step['configuration'] == config
            assert step['appearance'] == ('dark' if index in [3, 4] else 'light')
            assert step['textScale'] == (1.5 if index == 4 else 1)
            state(step['state'], config, mode != 0)
            image(step['path'], dpr)
        assert image(steps[0]['path'], dpr) == image(steps[5]['path'], dpr)
        assert steps[0]['state'] == steps[5]['state']
        for index in range(6):
            witness = history_lookup[(content, dpr, 2)]['steps'][index]
            assert image(steps[index]['path'], dpr) == image(witness['path'], dpr)
    assert used == {name for name in files if name.startswith('captures/') and name.endswith('.png')}
    replay = read('clean-replay.json')
    assert replay['accepted'] is False and replay['sourceBuiltFromUnchangedInputs'] is True
    expected_outputs = {name.removeprefix('captures/') for name in files if name.startswith('captures/')}
    assert len(replay['outputs']) == 1845 and {row['file'] for row in replay['outputs']} == expected_outputs
    for row in replay['outputs']:
        assert row['originalSha256'] == row['replaySha256'] == files['captures/' + row['file']]
    return dict(closedGroups=416, updateHistories=30, sourceReplayFiles=1845, accepted=False)


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
