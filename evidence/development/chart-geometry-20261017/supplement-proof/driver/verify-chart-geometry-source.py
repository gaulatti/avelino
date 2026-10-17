#!/usr/bin/env python3
"""Check supplemental chart geometry without changing the canonical reference."""
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/chart-geometry-20261017'
REFERENCE='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate_report(value):
    assert value['reference']==REFERENCE and value['accepted'] is False
    assert value['status']=='supplemental native geometry investigation; no baseline approval'
    assert value['expectedImagesChanged'] is False and value['approvedExceptions']==[] and value['tolerance']=='none'
    assert (value['contexts'],value['configurations'],value['images'],value['freshSourceReplayExactFiles'])==(125,45,500,503)
    assert value['actualBackingDpr']==2 and value['requestedDprs']==[1,1.25,1.5,1.75,2,2.5,3]
    assert value['remainingAcceptance']==['nativeFractionalFontLayout','nativeGeometryAndRaster','physicalDisplaysInput','readers','independentMachineReplay']
    assert value['sourceOnlyArtifact']['files']==9 and value['sourceOnlyArtifact']['containsPinnedSourceFiles']==89
    assert value['sourceOnlyArtifact']['downloadAvailability']=='pending independent-machine replay'
def contexts(directory=DIRECTORY):
    directory=Path(directory);projection=json.loads((directory/'projection.json').read_text());assert projection['reference']==REFERENCE and projection['accepted'] is False
    rows=[]
    for group,count in [('scales',49),('tiny',60),('categories',16)]:
        source=json.loads((directory/group/'captures.json').read_text())['rows'];assert len(source)==count
        for row in source:
            assert row['appearance']=='light' and row['textScale']==1 and row['modes']==[0,1,2,3]
            assert row['publicProbedIdentical'] and row['publicLiteralIdentical']
            assert row['states'][1]['frame']==row['states'][2]['frame']==row['states'][3]['frame']
            assert row['states'][1]['metrics']==row['states'][2]['metrics']==row['states'][3]['metrics']
            for state in row['states']:
                assert state['appearances']==state['wrapperInstances']==1 and state['disappearances']==0
                assert state['applicationActive'] is False and state['windowKey'] is False and state['backingDpr']==2
            images=[directory/group/name for name in row['paths']]
            assert images[0].read_bytes()==images[1].read_bytes()==images[2].read_bytes()
            for image in images:assert struct.unpack('>II',image.read_bytes()[16:24])==(640*row['dpr'],400*row['dpr'])
            rows.append(dict(group=group,configuration=row['configuration'],appearance=row['appearance'],textScale=row['textScale'],dpr=row['dpr'],paths=row['paths'],frame=row['states'][1]['frame'],metrics=row['states'][1]['metrics']))
    assert rows==projection['contexts'] and len(rows)==125
    assert len({r['configuration']['id'] for r in rows})==45
    return rows
def verify(directory=DIRECTORY):
    directory=Path(directory);read=lambda n:json.loads((directory/n).read_text());report=read('investigation.json');validate_report(report)
    assert set(report['files'])=={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name not in ['investigation.json','README.md']}
    for name,value in report['files'].items():assert digest(directory/name)==value,name
    rows=contexts(directory)
    identity=json.loads((ROOT/'evidence/reference-investigations/charts-20261017/source-identity.json').read_text())
    assert read('provenance/initial-inputs.json')['sourceFiles']=={r['path']:r['sha256'] for r in identity['files']}
    assert read('provenance/fresh-inputs.json')['files']['reference-source.tar']==identity['fullArchiveSha256']
    assert read('provenance/fresh-result.json')['prebuiltLibraryInputs'] is False and read('provenance/fresh-result.json')['sourceFilesUnchanged']==89
    assert read('provenance/fresh-execution-result.json')['exitCode']==0
    commands=read('provenance/fresh-commands.json');assert len(commands)==5 and all(r['exitCode']==0 for r in commands)
    replay=read('replay.json');assert replay['accepted'] is False and replay['prebuiltLibraryInputs'] is False and replay['sourceFilesUnchanged']==89
    assert len(replay['files'])==503
    for row in replay['files']:assert row['status']=='passed' and row['firstSha256']==row['replaySha256']==digest(directory/row['path'])
    assert len(report['canonicalPublicImagesUnchanged'])==14
    for row in report['canonicalPublicImagesUnchanged']:assert digest(ROOT/row['previous'])==digest(directory/row['current'])==row['sha256']
    print('Supplemental native charts: 125 contexts / 500 PNGs / 503 exact source replay outputs; requested scales remain separate from physical evidence')
    return report
if __name__=='__main__':verify()
