#!/usr/bin/env python3
"""Validate public sidebar/brand source witnesses without accepting parity."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/sidebar-brand-20261015'
SIDEBAR_VARIANTS={'normal','intrinsic','narrow','very-narrow','empty','long','multiline','rtl','disabled','labelled-init','symbol-wide','symbol-short','parent-font20'}
LOCKUP_VARIANTS={'normal','intrinsic','narrow','very-narrow','empty','long','multiline','rtl','disabled','parent-font30'}
ACTIONS={'activate','repeat','disabled','outside-release','corner','blank-spacer','producer-title','producer-selection','caller-selection'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(directory=DIRECTORY):
    directory=Path(directory);report=json.loads((directory/'investigation.json').read_text())
    reference=json.loads((ROOT/'reference/source-manifest.json').read_text())['references']['desktop']
    assert report['accepted'] is False and report['existingExpectedImagesChanged'] is False
    assert report['reference']==reference['revision']
    actual={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual==set(report['files'])|{'investigation.json'},'Missing or extra sidebar/brand evidence'
    for name,h in report['files'].items():
        path=Path(name);assert not path.is_absolute() and '..' not in path.parts
        assert digest(directory/path)==h,name
    data=json.loads((directory/'captures.json').read_text());assert data['reference']==reference['revision']
    cases=data['captures'];assert len(cases)==416
    expected={'button-anchor'}|{'sidebar-'+state+'-'+variant for state in ['normal','selected'] for variant in SIDEBAR_VARIANTS}|{'brand-mark-size'+str(float(size)) for size in [0,1,13,25,32,64,64.5,120,256]}|{'brand-mark-'+v for v in ['default','wide-frame','narrow-frame','disabled','rtl','parent-font20']}|{'brand-lockup-'+v for v in LOCKUP_VARIANTS}
    assert {c['fixture'] for c in cases}==expected
    assert {(c['fixture'],c['appearance'],c['textScale'],c['dpr']) for c in cases}=={(f,*axes) for f in expected for axes in itertools.product(['light','dark'],[1,1.5],[1,2])},'Incomplete source sidebar/brand matrix'
    for c in cases:
        assert c['source']==reference['revision'] and c['captureMethod']=='SwiftUI.ImageRenderer/CoreGraphics'
        assert c['status']=='proposed reference candidate; no baseline approval' and c['environmentDisplayScale']==c['dpr']
        for key in ['path','instrumentedPath','layoutWitnessPath']:assert Path(c[key]).name==c[key] and c[key].endswith('.png')
        raw=(directory/c['path']).read_bytes()
        assert c['instrumentedPngByteIdentical'] is True and raw==(directory/c['instrumentedPath']).read_bytes(),'Source instrumentation identity failed'
        assert c['layoutWitnessPngByteIdentical'] is True and raw==(directory/c['layoutWitnessPath']).read_bytes(),'Source layout identity failed'
        frame=(240,96) if c['api']=='BleeckerButton' else (720,1000)
        assert (c['width'],c['height'])==frame
        assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==tuple(n*c['dpr'] for n in frame)
        for rect in [c['componentRect'],*c['layoutWitnessRects'].values()]:
            assert set(rect)=={'x','y','width','height'} and all(math.isfinite(n) for n in rect.values())
            assert rect['width']>=0 and rect['height']>=0
        assert c['componentSize']=={k:c['componentRect'][k] for k in ['width','height']}
        blank=c['api']=='BleeckerBrandMark' and float(c['size']) in {0,1}
        assert c['expectedEmpty'] is blank,'Source uniform case classification changed'
        with Image.open(directory/c['path']) as image:
            image=image.convert('RGBA');uniform=ImageChops.difference(image,Image.new('RGBA',image.size,image.getpixel((0,0)))).getbbox(alpha_only=False) is None
        assert uniform is blank,'Unexpected blank/nonblank source brand render'
        if c['api']=='BleeckerBrandMark':
            edge=float(c['size']);assert c['componentSize']=={'width':edge,'height':edge}
            assert c['expectedEmptyReason']==('zero source view' if edge==0 else 'native source has no visible coverage at one point in the recorded DPR1/2 contexts' if edge==1 else '')
        elif c['api']=='BleeckerSidebarItem':
            r=c['layoutWitnessRects'];assert set(r)=={'icon','title','spacer'}
            assert r['icon']['width']==20 and r['spacer']['width']>=8
            assert c['componentSize']['height']==max(40,r['icon']['height'],r['title']['height'])
            assert c['layoutWitnessFonts']['title']=={'pointSize':14,'postScriptName':'EncodeSans-Md'}
            if c['text']=='':assert (r['title']['width'],r['title']['height'])==(0,14)
            order=['spacer','title','icon'] if c['rtl'] else ['icon','title','spacer']
            for a,b in zip(order,order[1:]):assert r[b]['x']-r[a]['x']-r[a]['width']==12,'Sidebar source gap changed'
        elif c['api']=='BleeckerBrandLockup':
            r=c['layoutWitnessRects'];assert set(r)=={'mark','title'}
            assert (r['mark']['width'],r['mark']['height'])==(25,32)
            assert c['componentSize']['height']==max(32,r['title']['height'])
            assert c['layoutWitnessFonts']['title']=={'pointSize':20,'postScriptName':'EncodeSans-Bold'}
            left,right=(r['title'],r['mark']) if c['rtl'] else (r['mark'],r['title'])
            assert right['x']-left['x']-left['width']==16,'Brand lockup source gap changed'
    behavior=data['behavior'];assert len(behavior)==36
    assert {(b['initialSelected'],b['action'],b['textScale']) for b in behavior}==set(itertools.product([False,True],ACTIONS,[1,1.5]))
    for b in behavior:
        expected=0 if b['action'] in {'disabled','outside-release'} else 2 if b['action']=='repeat' else 1
        assert b['calls']==expected,'Source sidebar callback transition changed'
        changed=b['action'] in {'producer-selection','caller-selection'}
        assert b['selectedAfterAction'] is (not b['initialSelected'] if changed else b['initialSelected']),'Source sidebar selection ownership changed'
        assert b['titleAfterAction']==('Updated sidebar title' if b['action']=='producer-title' else 'Editions')
        assert b['nativeDpr']==2 and set(b['nativeWindowState'])=={'key','main','applicationActive'}
    provenance=json.loads((directory/'tooling-provenance.json').read_text())
    assert provenance['referenceRevision']==reference['revision'] and provenance['referenceArchiveSha256']==reference['sha256']
    assert provenance['toolArtifact']['sha256']==report['sourceToolArtifact'] and len(provenance['toolArtifact']['files'])==35
    replay=json.loads((directory/'clean-replay.json').read_text())
    assert replay['inputHashesVerified']==35 and replay['filesCompared']==replay['byteIdenticalFiles']==1249 and replay['changedFiles']==[],'Sidebar/brand source replay changed'
    assert len(replay['results'])==1249
    for r in replay['results']:
        assert Path(r['path']).name==r['path'] and r['byteIdentical'] is True
        assert r['sha256']==r['replaySha256']==digest(directory/r['path']),'Source replay file mismatch'
    assert digest(ROOT/'assets/brand/BleeckerLogo.png')=='3eadafd84a1f3b37261bad85b8a8e5512ed7aa9b3baae38aa8321cc3a6cbb9c2','Pinned brand asset changed'
    return {'captures':416,'publicInstrumentationIdentity':416,'layoutWitnessIdentity':416,'nativePointerCases':36,'byteIdenticalReplayFiles':1249,'uniformBrandCases':16,'accepted':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
