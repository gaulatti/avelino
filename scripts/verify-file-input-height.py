#!/usr/bin/env python3
"""Audit retained FileInput height execution; exact native failures stay failures."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/file-input-height-20261024'
PARENT = 'cc718b6bb34ffa2d670ac992c5d5a83b8656ba9b'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
IMAGE = 'sha256:8856f888b6e4477b4e1b600428285d94b52d4a7b3846e4acfb7975fd484d220b'
MODULE = '0a54314045973302ebc90855c35773dc3bd4dfc2cd8fb2660dcc453a3686ea94'
INSTALLED = 'bf830b10b28f406890a35a4c2b6854223c6b449caa46029cad300fbd0b5d5359'
CONSUMER = '674e12f00ae3ae01f5ee38e58e35a633141a2ff5d425fb7ba5b91c2b849d8da3'
DELTA = ['src/Avelino/BleeckerFileInput.qml', 'src/Avelino/buttonlabel.cpp', 'src/Avelino/buttonlabel.h',
         'tests/components/fileinput-fixture.qml', 'tests/components/fileinput-ui.cpp',
         'tests/consumer/FileInputCase.qml', 'tests/consumer/fileinputchecks.h']
OFFERS = [('unspecified', -1, -1), ('zero', 0, 0), ('width-zero', 0, -1), ('height-zero', -1, 0),
          ('square-100', 100, 100), ('width-30', 30, -1), ('width-90', 90, -1), ('width-150', 150, -1),
          ('width-300', 300, -1), ('width-512', 512, -1), ('wide-2000-1000', 2000, 1000),
          ('height-260', -1, 260), ('infinity', -1, -1), ('infinite-width', -1, 100), ('infinite-height', 100, -1)]
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


OLD = load('height_prior_evidence', ROOT / 'scripts/verify-path-assistive-lifetime.py')
Capsule = OLD.Capsule


def limits(value):
    assert value['sourceParent'] == PARENT
    for key, expected in [('uiChecksEachDpr', 62), ('componentChecks', [5910, 6138]), ('runtimeProfiles', 22),
                          ('nativeSizingResponses', 10368), ('nativePngs', 216), ('rasterPairs', 40), ('rasterExactPairs', 0)]:
        assert value[key] == expected, key
    for key in ['accepted', 'nativeReaderAccepted', 'physicalInputAccepted', 'physicalGpuAccepted',
                'independentMachineAccepted', 'expectedImagesChanged']:
        assert value[key] is False, key
    assert value['pixelTolerance'] == 0 and value['masks'] == value['approvedExceptions'] == []


def candidate(actual, executed):
    assert actual == executed, 'Current runtime differs from the executed candidate'


def environment(capsule):
    result = capsule.record('environment/controller/result.json')
    assert result['exitCode'] == 0 and result['imageId'] == IMAGE
    assert result['oldImageRestored'] is result['accepted'] is False
    assert result['defaultContextBefore'] == result['defaultContextAfter'] == 'default'
    assert all(x['exitCode'] == 0 for x in result['stages'])
    assert capsule.raw('environment/controller/qt-version.log').decode().strip() == '6.8.3'
    names = [n.removeprefix('environment/context/') for n in capsule.records if n.startswith('environment/context/')]
    assert len(names) == 14
    originals = OLD.HISTORY.git_files(PARENT, names)
    assert all(capsule.raw('environment/context/' + n) == raw for n, raw in originals.items())


def binding(capsule, value):
    assert value['sourceParent'] == PARENT and value['accepted'] is False
    assert value['runtimeDeltaPaths'] == DELTA
    assert value['consumerOverridePaths'] == ['tests/consumer/fileinputchecks.h']
    files = value['files']; library = value['libraryFiles']
    assert len(files) == len(library) == 581 and set(files) == set(library)
    prior = OLD.HISTORY.git_files(PARENT, sorted(files))
    reconstructed = {n: sha(raw) for n, raw in prior.items()}
    for name in DELTA:
        prefix = 'consumer3/implementation/' if name == DELTA[-1] else 'fix3/implementation/'
        reconstructed[name] = sha(capsule.raw(prefix + name))
    assert reconstructed == files
    source = capsule.record('fix3/controller/inputs.json')
    assert source['parent'] == PARENT and source['imageId'] == IMAGE
    assert {n: source['sourceFiles'][n] for n in library} == library
    assert {n for n in files if files[n] != library[n]} == {DELTA[-1]}
    consumer = capsule.record('consumer3/controller/inputs.json')
    assert consumer['changedFilesFromFreshConsumer1'] == ['fileinputchecks.h']
    assert consumer['incrementalIndependentBuild'] is True
    assert consumer['freshEmptyBuildDirectory'] is consumer['libraryProjectMounted'] is False
    assert all(files['tests/consumer/' + n] == h for n, h in consumer['consumerFiles'].items() if 'tests/consumer/' + n in files)


def inventory(capsule, current=False):
    before = json.loads(OLD.HISTORY.git_files(PARENT, ['docs/parity-inventory.json'])['docs/parity-inventory.json'])
    raw = capsule.raw('inventory/candidate.json'); after = json.loads(raw)
    old = OLD.PROTECTED.protected_fields(before); new = OLD.PROTECTED.protected_fields(after)
    assert len(old) == 31534 and len(new) == 31535
    assert all(new[k] == v for k, v in old.items())
    assert before['television'] == after['television'] and before['desktop']['acceptance'] == after['desktop']['acceptance']
    for a, b in zip(before['desktop']['entries'], after['desktop']['entries']):
        assert a['id'] == b['id'] and a['status'] == b['status']
        assert b['cases'][:len(a['cases'])] == a['cases']
    assert len(after['desktop']['entries']) == 80
    assert sum(e['status'] == 'verification-pending' for e in after['desktop']['entries']) == 78
    if current: assert (ROOT / 'docs/parity-inventory.json').read_bytes() == raw


def native_witnesses(capsule, historical):
    responses = pngs = reproduced = 0
    for group, contexts in [('sizing-output', 32), ('scale3-sizing-output', 16)]:
        value = capsule.record('native/' + group + '/sizing.json')
        assert value['reference'] == REFERENCE and value['accepted'] is False and len(value['rows']) == contexts
        for row in value['rows']:
            assert [m['mode'] for m in row['modes']] == [0, 1, 2]
            modes = row['modes']; proposals = modes[0]['proposals']
            assert len(proposals) == 72 and all(m['proposals'] == proposals for m in modes)
            responses += 3 * len(proposals)
            if group == 'sizing-output':
                old = next(x for x in historical['sizing'] if x['configuration']['id'] == row['configuration']['id']
                           and all(x[k] == row[k] for k in ['appearance', 'textScale', 'dpr']))
                assert all(proposals[k] == v for k, v in old['proposals'].items())
                reproduced += 3 * len(old['proposals'])
    for group, contexts in [('capture-output', 32), ('scale3-capture-output', 16),
                            ('zero-width-capture-output', 16), ('scale3-zero-width-capture-output', 8)]:
        value = capsule.record('native/' + group + '/captures.json')
        assert value['reference'] == REFERENCE and value['accepted'] is False and len(value['rows']) == contexts
        for row in value['rows']:
            assert [m['mode'] for m in row['modes']] == [0, 1, 2]
            modes = row['modes']; decoded = []
            for mode in modes:
                with Image.open(io.BytesIO(capsule.raw('native/' + group + '/' + mode['path']))) as im:
                    im.load(); decoded.append((im.size, im.convert('RGBA').tobytes()))
                pngs += 1
            assert decoded[0] == decoded[1] == decoded[2]
            assert modes[1]['state']['frames'] == modes[2]['state']['frames']
    assert responses == 10368 and pngs == 216 and reproduced == 1440
    native = capsule.record('native/controller/inputs.json')
    assert native['reference'] == REFERENCE
    assert native['sourceArchiveSha256'] == '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
    assert len(native['sourceFiles']) == 89
    assert native['freshLibraryBuild'] is True and native['prebuiltLibraryInputs'] is False
    completed = capsule.record('native/controller/result.json')
    assert completed['exitCode'] == 0 and completed['priorSizingStartupExitCode'] == -5
    assert 'unable to find bundle named Sabella_Sabella' in capsule.raw('native/controller/sizing.log').decode()
    assert capsule.record('native/controller/validation.json')['sourceFilesUnchanged'] == 89
    external = json.loads((capsule.directory / 'external-native-source.json').read_text())
    assert len(external['files']) == 7 and external['embeddedAppleSource'] is False and external['accepted'] is False


def proposals(report, historical):
    assert len(report['sizing']) == 32
    expected_rows = [x for x in historical['sizing'] if all(x[k] == report[k] for k in ['appearance', 'textScale', 'dpr'])]
    assert len(expected_rows) == 32
    assert {x['configuration']['id'] for x in report['sizing']} == {x['configuration']['id'] for x in expected_rows}
    total = matched = 0
    for row in report['sizing']:
        native = next(x for x in expected_rows if x['configuration']['id'] == row['configuration']['id'])
        assert row['nativeProposals'] == native['proposals'] and row['configuration'] == native['configuration']
        assert row['callerFrameOmitted'] is row['retainedControlSequence'] is True
        assert row['infinityAdapter'] == 'Unbounded Qt dimension (-1)'
        assert len(row['observations']) == 15 and len(row['qtProposals']) == 15
        row_matches = 0
        for observation, (name, width, height) in zip(row['observations'], OFFERS):
            assert observation['name'] == name and observation['qtOffer'] == {'width': width, 'height': height}
            assert observation['native'] == native['proposals'][name]
            assert observation['actual'] == row['qtProposals'][name]
            match = observation['actual'] == observation['native']
            assert observation['match'] is match
            row_matches += match
        assert row['total'] == 15 and row['matched'] == row_matches
        assert row['status'] == ('passed' if row_matches == 15 else 'failed')
        if row_matches < 15: assert row['configuration']['id'] in ['unicode-title', 'rtl']
        matched += row_matches; total += 15
    assert report['nativeDirectProposalCount'] == total == 480
    assert report['nativeDirectProposalMatches'] == matched < total
    assert report['nativeDirectProposalComparisonStatus'] == 'failed'


def report(value, profile, historical, protocol, backend):
    assert value['fixture'] == profile['fixture'] and value['structuralChecks'] == 'passed'
    assert value['platform'] == protocol and value['graphicsApi'] == (1 if backend == 'software' else 3)
    assert all(value[k] == profile[k] for k in ['appearance', 'textScale', 'dpr'])
    assert value['accepted'] is False
    if value['fixture'] == 'file-input':
        assert value['qt'] == '6.8.3'
        proposals(value, historical)
        assert len(value['closed']) == 32 and value['images'] == 49 and value['closedImages'] == 32
        frames = 0
        for row in value['closed']:
            same = row['frames'] == row['nativeFrames']
            assert row['nativeCompleteFramesMatch'] is same
            frames += same
        assert value['nativeCompleteFramesMatch'] == frames == 30
        assert value['nativeContractStatesMatch'] == 32 and value['nativeFrameComparisonStatus'] == 'failed'
        assert len(value['assistiveLifetime']) == 10 and len(value['assistiveSelectionCallbacks']) == 4
        assert all(x['calls'] == x['destroyed'] == 1 for x in value['assistiveLifetime'])
        assert all(x['calls'] == 1 and x['editNotifications'] == 0 for x in value['assistiveSelectionCallbacks'])
        assert value['nativeRasterAcceptance'] == value['physicalInputAcceptance'] == value['readerAcceptance'] == 'pending'
    else:
        assert value['strictObservationsMatch'] is False and len(value['assistiveInput']) == 6
        assert {(x['endpoint'], x['owner']) for x in value['assistiveInput']} == {(e, o) for e in ['start', 'end'] for o in ['echo', 'ignore', 'delay']}


def capture(value):
    assert value['exitCode'] == value['captureExitCode'] == 0
    assert value['acknowledgedAfterActualSessionCapture'] is True
    assert value['consumerSha256'] == CONSUMER and value['installedLibrarySha256'] == INSTALLED
    for k in ['sourceProjectsMounted', 'productBuildMounted', 'consumerBuildMounted', 'physicalInput', 'accepted']:
        assert value[k] is False


def raster_row(capsule, row):
    images = []
    for side in ['native', 'qt']:
        raw = capsule.raw(row[side + 'Record']); assert sha(raw) == row[side + 'Sha256']
        with Image.open(io.BytesIO(raw)) as im:
            im.load(); im = im.convert('RGBA'); assert im.getchannel('A').getextrema() == (255, 255)
            images.append(im)
    a, b = images; assert a.size == b.size
    difference = ImageChops.difference(a.convert('RGB'), b.convert('RGB'))
    pixels = difference.tobytes()
    count = sum(any(pixels[i:i+3]) for i in range(0, len(pixels), 3))
    bounds = difference.getbbox()
    assert row['pixels'] == a.width * a.height and row['differentPixels'] == count > 0
    assert row['differenceBounds'] == list(bounds) and row['exact'] is False


def verify(directory=DIRECTORY, current=False):
    capsule = OLD.manifest(directory)
    value = json.loads((directory / 'validation.json').read_text()); limits(value)
    runtime = json.loads((directory / 'runtime-binding.json').read_text()); binding(capsule, runtime)
    environment(capsule)
    inventory(capsule, current)
    if current: candidate({n: sha((ROOT / n).read_bytes()) for n in runtime['files']}, runtime['files'])
    historical = json.loads(OLD.HISTORY.git_files(PARENT, ['tests/consumer/native-file-input-witnesses.json'])['tests/consumer/native-file-input-witnesses.json'])
    native_witnesses(capsule, historical)
    assert capsule.record('baseline1/controller/result.json')['exitCode'] == 125
    assert capsule.record('baseline2/controller/result.json')['applicationExecuted'] is True
    assert capsule.record('fix1/controller/result.json')['exitCode'] == 0
    assert capsule.record('regressions/controller/result.json')['exitCode'] != 0
    assert capsule.record('fix2/controller/result.json')['exitCode'] != 0
    for dpr in [1, 2]:
        log = capsule.raw(f'baseline2/controller/zero-proposal-dpr{dpr}.log').decode()
        assert '4 passed, 2 failed, 0 skipped' in log and 'Expected' in log
        OLD.qt_log(capsule.raw(f'fix3/controller/full-ui-dpr{dpr}.log').decode(), 'FileInputUiTests', 62)
        count = [5910, 6138][dpr - 1]
        log = capsule.raw(f'package/controller/components-dpr{dpr}.log').decode()
        assert f'Totals: {count} passed, 0 failed, 0 skipped' in log
    package = capsule.record('package/controller/result.json')
    assert package['exitCode'] == 0 and package['completedStages'] == package['expectedStages'] == 7
    assert package['builtModuleUnchangedFromUi'] is package['sourceUnchanged'] is True
    assert package['uiModuleSha256'] == MODULE and len(package['installedFiles']) == 158
    assert package['installedFiles']['lib/qml/Avelino/libAvelino.so'] == INSTALLED
    assert capsule.record('package/controller/inputs.json')['freshConsumerBuild'] is True
    assert capsule.record('consumer2/controller/result.json')['exitCode'] == 1
    consumer = capsule.record('consumer3/controller/result.json')
    assert consumer['exitCode'] == 0 and consumer['consumerSha256'] == CONSUMER
    profiles = []; canonical = []
    for group, count in [('runtime', 4), ('display', 12), ('canonical', 6)]:
        done = capsule.record(group + '/controller/result.json'); inputs = capsule.record(group + '/controller/inputs.json')
        assert done['exitCode'] == 0 and done['profilesPassed'] == done['expectedProfiles'] == count
        assert done['consumerUnchanged'] is done['installedPrefixUnchanged'] is True
        assert inputs['installedFiles'] == package['installedFiles'] and inputs['consumerSha256'] == CONSUMER
        commands = capsule.record(group + '/controller/commands.json'); assert len(commands) == count
        for command in commands:
            assert command['exitCode'] == 0 and IMAGE in command['command']
            mounts = [command['command'][i + 1] for i, s in enumerate(command['command']) if s == '--mount']
            assert len(mounts) == 3
            assert any('target=/package/install,readonly' in m for m in mounts)
            assert any('/InstalledConsumer,target=/package/consumer-build/InstalledConsumer,readonly' in m for m in mounts)
            assert any('target=/probe' in m for m in mounts)
        names = sorted(n for n in capsule.records if n.startswith(group + '/output/') and n.endswith('/capture-result.json'))
        assert len(names) == count
        for name in names:
            result = capsule.record(name); capture(result); prefix = name.removesuffix('capture-result.json')
            protocol = 'xcb' if group == 'runtime' else result['profile']['protocol']
            backend = 'software' if group == 'runtime' else result['profile']['backend']
            observed = capsule.record(prefix + 'report.json'); report(observed, result['profile'], historical, protocol, backend)
            assert '/package/install/lib/qml/Avelino/libAvelino.so' in capsule.raw(prefix + 'loaded-library-maps.txt').decode()
            OLD.capture_image(capsule.raw(prefix + 'full-session.png'))
            profiles.append(result['profile'])
            if group != 'display' and observed['fixture'] == 'file-input':
                canonical.append({'record':prefix + 'report.json', **{k:observed[k] for k in ['appearance','textScale','dpr']},
                                  'framesMatched':observed['nativeCompleteFramesMatch'], 'proposalMatches':observed['nativeDirectProposalMatches'],
                                  'proposalCount':observed['nativeDirectProposalCount']})
    assert len(profiles) == 22
    assert {json.dumps(x, sort_keys=True) for x in canonical} == {json.dumps(x, sort_keys=True) for x in value['canonicalProfiles']}
    assert {(x['appearance'], x['textScale'], x['dpr']) for x in canonical} == {(a, s, d) for a in ['light','dark'] for s in [1,1.5] for d in [1,2]}
    raster = json.loads((directory / 'raster-comparison.json').read_text())
    assert raster['pairs'] == len(raster['rows']) == 40 and raster['exactPairs'] == 0
    assert raster['tolerance'] == 0 and raster['masks'] == raster['approvedExceptions'] == []
    assert raster['accepted'] is raster['expectedImagesChanged'] is False
    for row in raster['rows']: raster_row(capsule, row)
    print('FileInput height:124 UI +12048 broader checks;22 source-free profiles;3840 native proposals measured;0/40 exact raster pairs;acceptance pending')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--directory', type=Path, default=DIRECTORY); parser.add_argument('--current', action='store_true')
    args = parser.parse_args(); verify(args.directory, args.current)
