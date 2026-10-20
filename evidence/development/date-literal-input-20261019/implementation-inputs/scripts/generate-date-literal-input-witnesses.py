#!/usr/bin/env python3
"""Verify bounded native input captures and derive Qt regression profiles."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
CAPSULE=ROOT/'evidence/reference-investigations/date-range-literal-input-20261018'
OUTPUT=ROOT/'tests/components/date_literal_cases.js'
CONSUMER=ROOT/'tests/consumer/native-date-literal-input-witnesses.json'


def verify():
    read=lambda name:json.loads((CAPSULE/name).read_text())
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    manifest=read('files.json')
    assert set(manifest)=={str(p.relative_to(CAPSULE))for p in CAPSULE.rglob('*')if p.is_file()and p!=CAPSULE/'files.json'}
    for name,row in manifest.items():
        path=CAPSULE/name;assert path.stat().st_size==row['bytes']and digest(path)==row['sha256'],name
    provenance=read('provenance.json')
    assert provenance['reference']=='fe8a1d462fbd793d883fb92086a16aa2947e32c9'and not provenance['accepted']
    assert not provenance['sourceChanged']and not provenance['independentNativeRebuild']
    assert provenance['executableSha256']==provenance['packagedExecutableSha256']
    assert provenance['compilerExitCode']==0 and provenance['backingDpr']==2 and provenance['swiftUiDisplayScale']==1
    source=ROOT/provenance['sourceVerificationRecord'];assert digest(source)==provenance['sourceVerificationSha256']
    assert json.loads(source.read_text())['freshProducerSourcesUnchanged']
    assert provenance['libraryObjectSha256']==read('helper-inputs.json')['objectSha256']
    rows={p.stem:read(p.name)for p in CAPSULE.glob('[0-9][0-9]-*.json')};assert len(rows)==15
    for name,row in rows.items():
        assert row['reference']==provenance['reference']and not row['accepted']
        assert row['windowKey']and row['applicationActive']and len(row['windows'])==1
        assert row['configuration']['owner']=='echo'and not row['configuration']['rtl']
        image=CAPSULE/(name+'.png');assert digest(image)==row['imageSha256']
        raw=image.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'and struct.unpack('>II',raw[16:24])==(1280,800)
    cases=read('cases.json');assert len(cases)==4
    assert [row['nativeCase']for row in cases]==['hebrew-day','hebrew-month','english-month','arabic-year']
    for case,days in zip(cases,[1,30,31,365]):
        before,literal,up=[rows[n]for n in case['observations']]
        assert before['configuration']['locale']==case['locale']and before['configuration']['calendar']==case['calendar']
        assert before['model']==literal['model']and before['imageSha256']==literal['imageSha256']
        assert up['model']['start']==case['nativeStartAfterUp']==literal['model']['start']+days*86400
        assert up['model']['end']==before['model']['end']
        assert len(up['model']['requests'])==len(before['model']['requests'])+1
        last=up['model']['requests'][-1]
        assert last['endpoint']=='start'and last['requested']==up['model']['start']and last['previousStart']==before['model']['start']
    before,focused,up=[rows[n]for n in ['13-initial-unfocused','14-initial-literal-focus','15-initial-literal-up-year']]
    assert before['focus']['class']=='NSWindow'and 'DatePicker'in focused['focus']['class']
    assert before['model']==focused['model']and len(focused['model']['requests'])==0
    assert before['imageSha256']!=focused['imageSha256']
    assert len(up['model']['requests'])==1 and up['model']['start']==1743264000.625
    assert read('bare-app-transport.json')['excludedFromOsInputEvidence']
    stability=ROOT/'evidence/reference-investigations/date-range-selected-field-stability-20261019'
    stable_manifest=json.loads((stability/'files.json').read_text())
    assert set(stable_manifest)=={str(p.relative_to(stability))for p in stability.rglob('*')if p.is_file()and p!=stability/'files.json'}
    for name,row in stable_manifest.items():
        path=stability/name;assert path.stat().st_size==row['bytes']and digest(path)==row['sha256']
    stable=json.loads((stability/'observations.json').read_text())
    assert not stable['accepted']and stable['reference']==provenance['reference']
    assert stable['parentManifestSha256']==digest(CAPSULE/'files.json')
    assert stable['rawJournalSha256']==next(row['sha256']for row in provenance['rawJournals']if row['path'].endswith('/output-v2/journal.json'))
    assert stable['totalFrames']==106 and len(stable['samples'])==4
    for sample in stable['samples']:
        assert sample['frames']==len(sample['receipts'])and sample['seconds']>=8
        before=rows[sample['first']];assert before['model']==sample['model']
        assert all(row['sha256']==before['imageSha256']and row['bytes']==(CAPSULE/(sample['first']+'.png')).stat().st_size for row in sample['receipts'])
    profiles=[{k:v for k,v in row.items()if k!='observations'}for row in cases]
    javascript='.pragma library\n// Derived from the sealed native date-literal input histories; no raster acceptance.\nvar profiles = '+json.dumps(profiles,ensure_ascii=False,indent=2)+';\n'
    consumer=json.dumps(dict(reference=provenance['reference'],accepted=False,profiles=profiles,scope='Four bounded native retained-selection histories; Qt endpoint/mirroring/DPR extensions are invariants, not native acceptance'),ensure_ascii=False,indent=2)+'\n'
    return {OUTPUT:javascript,CONSUMER:consumer}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for output,expected in verify().items():
        if args.check:assert output.read_text()==expected
        else:output.write_text(expected)
    print('Native literal input:15 source observations,4 retained-selection histories,106 stable selected-field captures and initial-focus boundary verified; Qt profiles derived; acceptance pending')
