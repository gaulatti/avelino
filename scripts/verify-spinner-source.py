#!/usr/bin/env python3
"""Validate actual native spinner geometry and controlled model-frame witnesses."""
import hashlib
import itertools
import json
import math
from pathlib import Path
import struct
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/spinner-20261015'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(directory=DIRECTORY):
    directory=Path(directory)
    report=json.loads((directory/'investigation.json').read_text())
    reference=json.loads((ROOT/'reference/source-manifest.json').read_text())['references']['desktop']
    assert report['accepted'] is False and report['existingExpectedImagesChanged'] is False
    assert report['reference']==reference['revision'] and report['nativeDprs']==[2]
    actual={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual==set(report['files'])|{'investigation.json'}
    for name,h in report['files'].items():
        path=Path(name);assert not path.is_absolute() and '..' not in path.parts
        assert digest(directory/path)==h,name
    data=json.loads((directory/'captures.json').read_text());assert data['reference']==reference['revision']
    captures=data['captures'];assert len(captures)==186
    for c in captures:
        assert c['source']==reference['revision'] and c['dpr']==2 and c['captureMethod'].startswith('NSHostingView.cacheDisplay')
        assert len(c['nativeProgressIndicators'])==1,'Missing actual native progress indicator'
        p=c['nativeProgressIndicators'][0];edge=16 if c['api']=='BleeckerButton' or c['size']=='sm' else 32
        assert p['class']=='NSProgressIndicator' and p['style']==1 and p['hidden'] is False and p['indeterminate'] is True
        assert p['width']==p['height']==edge,'Invalid source spinner size'
        animations=[a for layer in p['layers'] for a in layer['animations']]
        assert len(animations)==1
        a=animations[0]
        assert a['class']=='CAKeyframeAnimation' and a['duration']==0.8 and a['speed']==1 and a['valueCount']==24 and a['calculationMode']=='discrete' and a['keyPath']=='contentsRect','Invalid source native animation model'
        assert a['keyTimes']==[i/24 for i in range(25)]
        name=Path(c['path']);assert name.name==str(name)
        image=(directory/name).read_bytes();assert image[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',image[16:24])==(640,360)
    buttons=[c for c in captures if c['api']=='BleeckerButton']
    assert len(buttons)==112 and {(c['size'],c['variant'],c['appearance'],c['textScale']) for c in buttons}==set(itertools.product(['xs','sm','md','lg'],['primary','secondary','outline','subtle','ghost','link','destructive'],['light','dark'],[1,1.5]))
    phases=data['phases'];assert len(phases)==144
    assert {(p['size'],p['appearance'],p['index']) for p in phases}==set(itertools.product(['sm','md','lg'],['light','dark'],range(24)))
    for p in phases:
        base=directory/f"spinner-{p['size']}-default-inherited-{p['appearance']}.png"
        same=(directory/p['path']).read_bytes()==base.read_bytes()
        assert same is p['unmodifiedPngByteIdentical'],'False phase identity claim'
        if p['index']==0:assert same,'Native phase-zero instrumentation changed the source image'
    provenance=json.loads((directory/'tooling-provenance.json').read_text())
    assert provenance['referenceRevision']==reference['revision'] and provenance['referenceArchiveSha256']==reference['sha256']
    assert provenance['toolArtifact']['sha256']==report['sourceToolArtifact']
    assert provenance['cleanReplay']['filesCompared']==provenance['cleanReplay']['byteIdenticalFiles']==335 and provenance['cleanReplay']['changedFiles']==[]
    if directory.resolve()==DIRECTORY.resolve():
        assert (ROOT/'evidence/geometry/native-spinner.json').read_bytes()==(directory/'captures.json').read_bytes(),'Derived spinner geometry differs from source'
        values=[]
        c=next(c for c in captures if c['path']=='spinner-md-default-inherited-light.png');p=c['nativeProgressIndicators'][0]
        for index in range(24):
            with Image.open(directory/f'phase-md-light-{index}.png') as im:
                im=im.convert('RGB');row=[]
                for spoke in range(8):
                    angle=spoke*math.pi/4;x=math.floor(p['x']*2+32+math.sin(angle)*22);y=math.floor((180-p['y']-p['height'])*2+32-math.cos(angle)*22)
                    row.append(255-im.getpixel((x,y))[0])
                values.append(row)
        js=(ROOT/'src/Avelino/spinnerpresentation.js').read_text().split('var levels = ',1)[1]
        assert json.loads(js)==values,'Product opacity levels differ from measured source frame centers'
    return {'nativeContexts':186,'controlledFrames':144,'phaseZeroIdentityWitnesses':6,'byteIdenticalReplayFiles':335,'accepted':False}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
