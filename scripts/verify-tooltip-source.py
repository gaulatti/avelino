#!/usr/bin/env python3
"""Audit closed Tooltip and native help observations without accepting Linux parity."""
import hashlib
import itertools
import json
from pathlib import Path
import struct
import tarfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/tooltip-20261016'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
SOURCE_SHA256 = '4fd5cf743fd13c12f375c65a4a711d7210e6fb9d4639225737b391eb498f784c'
ARCHIVE_SHA256 = '25e65515bd19c88f9ba5b1546a5e3d2ac1cdfd59e726af00d2322c25ea645a39'
FIXTURES = set('''default hint-empty hint-long hint-lines hint-unicode hint-bidi
content-rectangle content-zero content-empty content-hidden content-wide content-text
content-inherited content-multi content-vstack content-hstack content-wide-button
disabled rtl parent-font32 parent-red'''.split())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(directory=DIRECTORY):
    directory = Path(directory)
    read = lambda name: json.loads((directory / name).read_text())
    report = read('investigation.json')
    assert report['referenceRevision'] == REFERENCE and report['accepted'] is False
    assert report['linuxImplementation'] == 'pending'
    assert report['approvedExceptions'] == [] and report['expectedImagesChanged'] is False
    assert report['physicalInputAcceptance'] == report['screenReaderAcceptance'] == 'pending'
    assert report['nativePopupAcceptance'] == 'pending'
    files = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert files == set(report['files']) | {'investigation.json'}, 'Missing or extra native evidence'
    for name, expected in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory / name) == expected, name
    inputs, build, provenance = (read(name) for name in ['inputs.json', 'source-build-result.json', 'tooling-provenance.json'])
    assert inputs['reference'] == build['reference'] == provenance['reference'] == REFERENCE
    assert set(inputs['files']) == {'reference-source.tar','tool/Common.swift','tool/CaptureMain.swift','replay.py'}
    assert inputs['files']['reference-source.tar'] == build['sourceArchiveSha256'] == SOURCE_SHA256
    assert inputs['compiledInputs'] == provenance['compiledInputs'] == []
    assert build['sourceFilesUnchanged'] == 89 and build['libraryBuiltFromSources'] is True
    assert build['prebuiltLibraryInputs'] is False
    assert provenance['independentMachineAvailability'] == 'pending'
    assert provenance['sourceOnlyReplayArchiveSha256'] == ARCHIVE_SHA256
    assert provenance['sourceOnlyReplayMembers'] == sorted([*inputs['files'],'inputs.json'])
    archive = Path(provenance['sourceOnlyReplayArchive'])
    if archive.exists():
        assert digest(archive) == ARCHIVE_SHA256
        with tarfile.open(archive) as source:
            assert sorted(m.name for m in source.getmembers()) == provenance['sourceOnlyReplayMembers']
            for name, expected in inputs['files'].items():
                assert hashlib.sha256(source.extractfile(name).read()).hexdigest() == expected
    native_inputs = read('native-inputs.json')
    assert native_inputs['reference'] == REFERENCE and native_inputs['compiledInputs'] == []
    assert native_inputs['files']['reference-source.tar'] == SOURCE_SHA256
    assert set(native_inputs['files']) == {'reference-source.tar','replay.py','README.md',
                                           'v1/Probe.swift','v1/Info.plist','v2/Probe.swift','v2/Info.plist'}
    assert provenance['activeSourceArchiveSha256'] == '810513e431df9bd8d0a22f74c13857bdd912d694c2516c0fb20fc9501afcdd66'
    assert provenance['activeSourceMembers'] == sorted([*native_inputs['files'],'inputs.json'])
    native_archive = Path(provenance['activeSourceArchive'])
    if native_archive.exists():
        assert digest(native_archive) == provenance['activeSourceArchiveSha256']
        with tarfile.open(native_archive) as source:
            assert sorted(m.name for m in source) == provenance['activeSourceMembers']
            for name, expected in native_inputs['files'].items():
                assert hashlib.sha256(source.extractfile(name).read()).hexdigest() == expected
    active_build = read('active-clean-build/source-build-result.json')
    assert active_build['reference'] == REFERENCE and active_build['sourceFilesUnchanged'] == 89
    assert active_build['libraryBuiltFromSources'] is True and active_build['prebuiltLibraryInputs'] is False
    assert active_build['compiledProbeModes'] == ['v1','v2'] and active_build['automaticPixelReplay'] is False
    corpus = read('closed/captures.json')
    assert corpus['reference'] == REFERENCE and corpus['fixtures'] == 21 and corpus['peakWindows'] == 1
    rows = corpus['captures']
    identity = lambda r:(r['configuration']['fixture'],r['appearance'],r['textScale'],r['dpr'])
    lookup = {identity(r):r for r in rows}
    assert len(rows) == len(lookup) == report['closedCases'] == 168
    assert set(lookup) == set(itertools.product(FIXTURES,['light','dark'],[1,1.5],[1,2]))
    used_pngs = set()
    for row in rows:
        assert all(row[k] is True for k in ['publicProbedIdentical','publicWitnessIdentical','publicUnwrappedIdentical'])
        assert len(row['paths']) == len(row['states']) == 4
        images = []
        for name in row['paths']:
            used_pngs.add('closed/'+name)
            image = (directory/'closed'/name).read_bytes(); images.append(image)
            assert image[:8] == b'\x89PNG\r\n\x1a\n'
            assert struct.unpack('>II',image[16:24]) == (640*row['dpr'],400*row['dpr'])
        assert len(set(images)) == 1
        assert row['states'][1] == row['states'][2], 'Witness must preserve all observed state'
        for s in row['states']:
            assert not s['applicationActive'] and not s['windowKey']
            assert s['windowVisible'] and s['backingDpr'] == 2
            assert s['calls'] == [] and s['count'] == 0 and s['disappears'] == 0
            assert s['mountValues'] == ([0] if row['configuration']['content']=='button' else [])
        parts = row['states'][1]['parts']
        if row['configuration']['content']=='empty':
            assert parts == {}
        else:
            frame = parts['root']
            assert frame['x']+frame['width']/2 == 320 and frame['y']+frame['height']/2 == 200
            children = [f for key,f in parts.items() if key!='root']
            assert frame['width'] == max(c['width'] for c in children)
            assert frame['height'] == max(c['height'] for c in children)
            assert all(c['x']+c['width']/2 == 320 and c['y']+c['height']/2 == 200 for c in children)
        fixture = row['configuration']['fixture']
        if fixture.startswith('hint-'):
            base = lookup[('default',row['appearance'],row['textScale'],row['dpr'])]
            assert images[0] == (directory/'closed'/base['paths'][0]).read_bytes(), 'Help text cannot change closed pixels'
    assert used_pngs == {n for n in files if n.startswith('closed/') and n.endswith('.png')}
    for fixture,dimensions in {'content-zero':(0,0),'content-hidden':(200,80),'content-wide':(800,80),
                               'content-multi':(72,44),'content-vstack':(72,65),'content-hstack':(136,44),'content-wide-button':(828,80)}.items():
        frame = lookup[(fixture,'light',1,1)]['states'][1]['parts']['root']
        assert (frame['width'],frame['height']) == dimensions
    replay = read('clean-replay.json')
    assert replay['files'] == replay['identicalFiles'] == len(replay['outputs']) == 673
    assert replay['sourceOnlyRebuild'] is True
    assert {r['file'] for r in replay['outputs']} == {n.removeprefix('closed/') for n in files if n.startswith('closed/')}
    for r in replay['outputs']:
        assert r['identical'] is True and r['originalSha256'] == r['replaySha256'] == digest(directory/'closed'/r['file'])
    hint = read('native-v1/hint-update.json')
    assert hint['accepted'] is False and hint['beforeCount'] == hint['afterCount'] == 1
    assert hint['mountValues'] == [0] and hint['disappears'] == 0
    assert hint['beforeHint'] == 'Publishes the selected edition' and hint['afterHint'] == 'Reviews the published edition'
    assert hint['sameBodyPixelsAndFile'] is True
    assert hint['beforeSha256'] == hint['afterSha256'] == digest(directory/'native-v1'/hint['beforeCapture']) == digest(directory/'native-v1'/hint['afterCapture'])
    before,after = (read('native-v2/'+n) for n in ['state-before-live-hint.json','state-after-live-hint-capture.json'])
    assert before['hint'] == hint['beforeHint'] and after['hint'] == hint['afterHint']
    for s in [before,after]:
        assert s['applicationActive'] is True and s['calls'] == [] and s['count'] == 0
        assert s['mountValues'] == [0] and s['disappears'] == 0
        assert any(e['type'] == 8 for e in s['mouseEvents']), 'Real entry must have been observed'
        panels = [w for w in s['windows'] if w['class']=='NSToolTipPanel' and w['visible']]
        assert len(panels) == 1
        w = panels[0]
        assert w['frame']['width'] == 171 and w['frame']['height'] == 21 and w['backingDpr'] == 2
        assert not w['key'] and not w['main'] and w['level'] == 103
        assert [v['class'] for v in w['views']] == ['NSVisualEffectView','NSCustomToolTipDrawView']
        assert 'no compositor or screen-reader equivalence claim' in s['captureScope']
    original = directory/'native-v2/auto-aux-window49094-content.png'
    updated = directory/'native-v2/capture-2-window49094-content.png'
    assert original.read_bytes() == updated.read_bytes(), 'Visible native tooltip kept its prior text in this observation'
    assert struct.unpack('>II',original.read_bytes()[16:24]) == (342,42)
    assert report['shownHintUpdate'] == 'existing panel pixels unchanged; accessibility hint changed independently'
    assert read('diagnostics/popup-v4/classification.json')['nativePopupAcceptance'] == 'excluded'
    metrics = read('native-metrics.json')
    assert metrics['pointSize'] == 11 and metrics['fontRedistributionApproval'] is False
    return dict(closedCases=168,closedReplayFiles=673,nativePanelCases=1,accepted=False)

if __name__ == '__main__':
    print(json.dumps(verify(),indent=2))
