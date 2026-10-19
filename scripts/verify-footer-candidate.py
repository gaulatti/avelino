#!/usr/bin/env python3
"""Decode the footer layout checkpoint while leaving mirror acceptance pending."""
import hashlib
import itertools
import json
from pathlib import Path
import re

from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
CAPSULE=ROOT/'evidence/development/footer-layout-20261019'
NATIVE=ROOT/'evidence/reference-investigations/footer-slots-20261019'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changed_pixels(before,after):
    with Image.open(before) as a,Image.open(after) as b:
        a,b=a.convert('RGBA'),b.convert('RGBA')
        assert a.size==b.size
        delta=ImageChops.difference(a,b)
        mask=delta.getchannel('R')
        for channel in ['G','B','A']:mask=ImageChops.lighter(mask,delta.getchannel(channel))
        return a.width*a.height-mask.histogram()[0]


def verify():
    read=lambda name:json.loads((CAPSULE/name).read_text())
    files=read('files.json')
    assert set(files)=={str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p!=CAPSULE/'files.json'}
    for name,row in files.items():
        path=Path(name)
        assert not path.is_absolute() and '..' not in path.parts
        assert digest(CAPSULE/path)==row['sha256'] and (CAPSULE/path).stat().st_size==row['bytes'],name
    result=read('result.json')
    assert result['exitCode']==0 and result['sourceProfiles']==result['componentTestProfiles']==120
    assert all(result[key] is False for key in ['physicalDisplay','nativeWindowInput','readerAcceptance','accepted','fullMirrorAccepted'])
    for path in (CAPSULE/'implementation-inputs').rglob('*'):
        if path.is_file():assert digest(path)==digest(ROOT/path.relative_to(CAPSULE/'implementation-inputs'))
    source=json.loads((NATIVE/'captures.json').read_text())
    assert source['reference']==result['sourcePin']=='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    comparisons={row['source']:row for row in read('provenance/v4/comparison.json')['results']}
    assert len(source['captures'])==len(comparisons)==120
    exact=0
    for row in source['captures']:
        path=CAPSULE/'captures'/row['path']
        metadata=json.loads(Path(str(path)+'.json').read_text())
        record=comparisons[row['path']]
        assert digest(path)==record['sha256']
        assert metadata['qt']=='6.8.3' and metadata['dpr']==row['dpr'] and metadata['platform']=='offscreen'
        for name,frame in row['frames'].items():
            actual=metadata['footerFrames'][name]
            assert all(abs(actual[axis]-value)<=1e-6 for axis,value in frame.items()),(row['path'],name)
        changed=changed_pixels(NATIVE/row['path'],path)
        assert changed==record['changedPixels'] and record['geometryPassed']
        exact+=changed==0
    assert exact==result['catalogExactPixels']==44 and result['catalogGeometryPassed']==120
    for dpr in [1,2]:
        text=(CAPSULE/f'logs/v3/footer-dpr{dpr}.log.txt').read_text()
        assert len(re.findall(r'PASS\s+:.*::test_source_frames\(',text))==60
        assert re.search(r'Totals:\s+\d+ passed,\s+0 failed',text)
        text=(CAPSULE/f'logs/v3/composition-dpr{dpr}.log.txt').read_text()
        assert re.search(r'Totals:\s+\d+ passed,\s+0 failed',text)
    commands=read('provenance/v4/commands.json')
    assert all(row['exitCode']==0 for row in commands) and len(commands)==132
    assert [row['name'] for row in commands[:3]]==['fresh-consumer-configure','fresh-consumer-build','runtime-source-absence']
    installed=[row for row in commands if row['name'].startswith('installed-composition-') and row['name']!='installed-composition-display']
    assert len(installed)==result['sourceFreeConsumerContexts']==8
    assert commands[-1]['name']=='installed-composition-display'
    sessions=[p for p in (CAPSULE/'display').glob('*.json') if p.name!='environment.json']
    assert len(sessions)==result['virtualCompositionDisplayContexts']==8
    contexts=set(itertools.product(['xcb','wayland'],['software','opengl'],['standard','scaled']))
    assert {tuple(p.stem.removeprefix('composition-').split('-')) for p in sessions}==contexts
    for path in sessions:
        row=json.loads(path.read_text())
        assert row['compositionChecks']==row['focusResizeChecks']=='passed'
        assert row['physicalDisplay'] is row['hardwareAcceleration'] is False
        assert digest(path.with_suffix('.png'))==row['windowCaptureSha256']
        assert digest(path.parent/row['sessionCapture'])==row['sessionCaptureSha256']
    legacy=read('provenance/v4/legacy-comparison.json')
    assert len(legacy['rows'])==result['legacyCases']==24
    assert legacy['compiledVsPrototypeByteIdentical']==result['compiledVsPrototypeByteIdentical']==120
    improved=worsened=lost=0
    for row in legacy['rows']:
        source_path=ROOT/'evidence/reference-proposals/composition-20261012-v1'/row['legacy']
        before=changed_pixels(source_path,CAPSULE/'legacy-before'/row['legacy'])
        after=changed_pixels(source_path,CAPSULE/'captures'/row['candidate'])
        assert (before,after)==(row['beforeChangedPixels'],row['afterChangedPixels'])
        improved+=after<before;worsened+=after>before;lost+=before==0 and after!=0
    assert improved==result['legacyPixelImproved']==12
    assert worsened==result['legacyPixelWorsened']==2 and lost==result['legacyExactPassesLost']==0
    print('Footer candidate:120 native layouts,44 exact images,8 source-free consumer and8 virtual display contexts;2 legacy light/DPR1 text cases increase by4 changed pixels. Mirror acceptance pending')


if __name__=='__main__':verify()
