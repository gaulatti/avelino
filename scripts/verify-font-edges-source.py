#!/usr/bin/env python3
"""Audit finite-negative font inputs against unchanged public zero-size cases."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import struct
import tarfile

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/font-edges-20261016'
spec=importlib.util.spec_from_file_location('font_edge_contexts',ROOT/'scripts/verify-font-modifier-source.py')
contexts=importlib.util.module_from_spec(spec);spec.loader.exec_module(contexts)
INPUTS={
    'README.md':'549cf431e9ca2c71bcfb6047783808782a69c189e84a08f64be595b2d70f6f43',
    'reference-source.tar':contexts.SOURCE_SHA256,
    'replay.py':'2ee5d65d93c4dd29fc64b4b7ce51ab88df9b809293e24213b6f11a2e0b7e22c8',
    'tool/CaptureMain.swift':'a31b3432875bb14cd8807866786109c403e484296e4b8d4b816a74f9ec0f0d82',
    'tool/Common.swift':contexts.INPUTS['tool/Common.swift'],
}
ARCHIVE_SHA256='e6c15e72d08a9cb5193b83ff9e0d0200d3c10bfc8f57b814ba37b9b7811fa8f2'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(directory=DIRECTORY):
    directory=Path(directory);read=lambda name:json.loads((directory/name).read_text())
    report=read('investigation.json')
    assert report['referenceRevision']==contexts.REFERENCE and report['accepted'] is False
    for gate in ['linuxImplementation','nonfiniteTextLayoutAcceptance','otherWeightCombinationsAcceptance',
                 'physicalDisplayAcceptance','screenReaderAcceptance']:assert report[gate]=='pending'
    assert report['expectedImagesChanged'] is False and report['approvedExceptions']==[]
    assert report['baselineScope']=='Centered layouts provide no baseline measurements'
    files={p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    assert files==set(report['files'])|{'investigation.json'}
    for name,sha in report['files'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert digest(directory/name)==sha,name
    inputs,build,provenance=(read(name) for name in ['inputs.json','source-build-result.json','tooling-provenance.json'])
    assert inputs['reference']==build['reference']==provenance['reference']==contexts.REFERENCE
    assert inputs['files']==INPUTS and inputs['compiledInputs']==provenance['compiledInputs']==[]
    assert build['sourceArchiveSha256']==contexts.SOURCE_SHA256 and build['sourceFilesUnchanged']==89
    assert build['libraryBuiltFromSources'] is True and build['prebuiltLibraryInputs'] is False
    assert read('replay-build/source-build-result.json')==build
    assert provenance['sourceOnlyReplayArchiveSha256']==ARCHIVE_SHA256
    assert provenance['sourceOnlyReplayMembers']==sorted([*INPUTS,'inputs.json'])
    assert provenance['accepted'] is False and provenance['independentMachineAvailability']=='pending'
    archive=Path(provenance['sourceOnlyReplayArchive'])
    if archive.exists():
        assert digest(archive)==ARCHIVE_SHA256
        with tarfile.open(archive) as source:
            assert sorted(m.name for m in source)==provenance['sourceOnlyReplayMembers']
            for name,sha in INPUTS.items():assert hashlib.sha256(source.extractfile(name).read()).hexdigest()==sha
    corpus=read('captures/captures.json');assert corpus['reference']==contexts.REFERENCE and corpus['fixtures']==9
    rows=corpus['captures'];identity=lambda r:(r['configuration']['family'],r['configuration']['size'],r['appearance'],r['textScale'],r['dpr'])
    indexed={identity(r):r for r in rows}
    assert len(rows)==len(indexed)==report['groups']==72
    assert set(indexed)==set(itertools.product(contexts.FAMILIES,[-14,-.5,-.11],['light','dark'],[1,1.5],[1,2]))
    original=json.loads((contexts.DIRECTORY/'captures/captures.json').read_text())
    zero={(r['configuration']['family'],r['appearance'],r['textScale'],r['dpr']):r for r in original['captures'] if r['configuration']['fixture'].startswith('size-') and r['configuration']['size']==0}
    used=set()
    for row in rows:
        f=row['configuration'];base=zero[(f['family'],row['appearance'],row['textScale'],row['dpr'])]
        expected=dict(base['configuration'],size=f['size'],fixture=f"size-{f['family']}-{float(f['size'])}")
        assert f==expected
        assert row['publicProbedIdentical'] is True and row['publicWitnessIdentical'] is True
        assert len(row['paths'])==len(row['states'])==3
        assert row['states']==base['states'],'Negative size changed observed zero-size behavior'
        assert row['states'][1]['ambientFontsAtProbe']['label']['resolvedPointSize']==12
        for mode,name in enumerate(row['paths']):
            relative='captures/'+name;used.add(relative);data=(directory/relative).read_bytes()
            assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(640*row['dpr'],400*row['dpr'])
            assert data==(contexts.DIRECTORY/'captures'/base['paths'][mode]).read_bytes()
    assert used=={name for name in files if name.startswith('captures/') and name.endswith('.png')} and len(used)==216
    replay=read('clean-replay.json');assert replay['sourceOnlyRebuild'] is True
    assert replay['files']==replay['identicalFiles']==len(replay['outputs'])==report['sourceReplayFiles']==217
    assert {r['file'] for r in replay['outputs']}=={name.removeprefix('captures/') for name in files if name.startswith('captures/')}
    for row in replay['outputs']:assert row['identical'] is True and row['originalSha256']==row['replaySha256']==digest(directory/'captures'/row['file'])
    return dict(groups=72,zeroSizeImageMatches=216,sourceReplayFiles=217,accepted=False)

if __name__=='__main__':print(json.dumps(verify(),indent=2))
