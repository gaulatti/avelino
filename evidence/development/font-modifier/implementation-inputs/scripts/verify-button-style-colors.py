#!/usr/bin/env python3
"""Audit the source-only platform-color replay against all parent PNG samples."""
import hashlib
import json
import math
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/development/button-style/platform-colors'
SOURCE=ROOT/'evidence/reference-investigations/button-style-20261016'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(folder,name):return json.loads((folder/name).read_text())

def verify(directory=DIRECTORY):
    directory=Path(directory)
    assert {p.name for p in directory.iterdir()}=={'colors.json','inputs.json','provenance.json','replay-colors.json','replay-result.json','replay-build.log','result.json'}
    result=load(directory,'result.json');provenance=load(directory,'provenance.json');replay=load(directory,'replay-result.json')
    assert result['accepted'] is False and provenance['accepted'] is False
    assert result['sourceReference']=='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert provenance['compiledInputs']==replay['compiledInputs']==load(directory,'inputs.json')['compiledInputs']==[]
    assert provenance['members']==['inputs.json','Colors.swift','replay.py','README.md']
    assert provenance['sourceArchiveSha256']=='fdf396b832fe02496f9e7ace47b6c626b2cdd9e7a6aa84047061c9f43e3ad5f7'
    assert replay['sourceFilesVerified']==3 and replay['binaryRebuilt'] and replay['uiInteraction'] is False
    assert digest(directory/'colors.json')==digest(directory/'replay-colors.json')==result['colorsSha256']==replay['colorsSha256']
    assert result['colorReplayByteIdentical'] and result['pngSamples']==len(result['samples'])==64
    report=load(SOURCE,'investigation.json');assert digest(SOURCE/'captures/captures.json')==result['sourceCaptureMetadataSha256']==report['files']['captures/captures.json']
    rows={r['paths'][0]:r for r in load(SOURCE,'captures/captures.json')['captures'] if r['configuration']['parentLayout']!='zstack'}
    colors={(r['appearance'],r['name']):r for r in load(directory,'colors.json')['rows']}
    assert set(colors)=={(a,n) for a in ['light','dark'] for n in ['green','orange','red']}
    for row in colors.values():assert row['bytes']==[math.floor(v*255+.5) for v in row['srgb']]
    contexts={(s['file'],s['color']) for s in result['samples']}
    assert len(contexts)==64 and contexts=={('captures/'+n,c) for n in rows for c in ['green','orange']}
    for sample in result['samples']:
        row=rows[sample['file'].removeprefix('captures/')];path=SOURCE/sample['file']
        assert digest(path)==sample['sha256']==report['files'][sample['file']]
        assert sample['appearance']==row['appearance'] and sample['opacity']==.2
        part=row['states'][1]['partInstances']['leading' if sample['color']=='green' else 'trailing'][0]
        assert sample['point']==[round((part['x']+part['width']/2)*row['dpr']),round((part['y']+part['height']/2)*row['dpr'])]
        image=Image.open(path).convert('RGBA');background=image.getpixel((0,0));color=colors[(row['appearance'],sample['color'])]['srgb']
        expected=[math.floor(color[i]*255*.2+background[i]*.8+.5) for i in range(3)]+[255]
        assert sample['background']==list(background)
        assert sample['rgba']==sample['predicted']==list(image.getpixel(tuple(sample['point'])))==expected
    return dict(sourceReplayFiles=1,pngSamples=64,accepted=False)

if __name__=='__main__':print(json.dumps(verify(),indent=2))
