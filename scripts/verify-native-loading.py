#!/usr/bin/env python3
"""Verify actual hosted progress evidence; reject historical renderer placeholders."""
import hashlib
import itertools
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/loading-native-20261015'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(directory=DIRECTORY):
    directory=Path(directory)
    report=json.loads((directory/'investigation.json').read_text())
    assert report['accepted'] is False and report['existingExpectedImagesChanged'] is False
    expected=json.loads((ROOT/'reference/source-manifest.json').read_text())['references']['desktop']
    assert report['reference']==expected['revision'] and report['captures']==32 and report['nativeDprs']==[2]
    actual={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual==set(report['files'])|{'investigation.json'}
    for name,h in report['files'].items():
        p=Path(name);assert not p.is_absolute() and '..' not in p.parts
        assert digest(directory/p)==h,name
    manifest=json.loads((directory/'captures.json').read_text())
    if directory.resolve()==DIRECTORY.resolve():
        assert (ROOT/'evidence/geometry/native-loading-hosted.json').read_bytes()==(directory/'captures.json').read_bytes(),'Derived hosted fixtures differ from native source'
    assert manifest['reference']==expected['revision']
    rows=manifest['captures'];assert len(rows)==32
    variants={'default','normal','empty-message','long','multiline','narrow','intrinsic','rtl'}
    assert {(c['variant'],c['appearance'],c['textScale'],c['dpr']) for c in rows}==set(itertools.product(variants,['light','dark'],[1,1.5],[2]))
    for c in rows:
        assert c['api']=='BleeckerLoadingOverlay' and c['source']==expected['revision']
        assert c['captureMethod'].startswith('NSHostingView.cacheDisplay'), 'Native progress cannot use ImageRenderer placeholders'
        assert c['dpr']==c['environmentDisplayScale']==2 and (c['width'],c['height'])==(640,400)
        name=Path(c['path']);assert name.name==str(name) and name.suffix=='.png'
        data=(directory/name).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==(1280,800)
        indicators=c['nativeProgressIndicators'];assert len(indicators)==1,'Missing actual native progress descendant'
        p=indicators[0]
        assert p['class']=='NSProgressIndicator' and p['style']==1 and p['controlSize']==3,'Unexpected native progress presentation'
        assert p['indeterminate'] is True and p['hidden'] is False and (p['width'],p['height'])==(32,32),'Native progress must be visible and correctly sized'
        assert 0<=p['x']<=608 and 0<=p['y']<=368
        font=c['resolvedLabelFonts']['loading'];assert (font['postScriptName'],font['pointSize'])==('EncodeSans-Md',14)
        assert c['animationPhase']=='uncontrolled native indeterminate progress; no phase acceptance'
    old=ROOT/'evidence/reference-investigations/presentation-states-20261014'
    original=json.loads((old/'captures.json').read_text())
    invalid={c['path'] for c in original['captures'] if c['api']=='BleeckerLoadingOverlay'}
    excluded=report['unsupportedImageRendererCaptures']
    assert len(excluded)==64 and {c['path'] for c in excluded}==invalid,'Missing unsupported-renderer exclusions'
    for c in excluded:assert digest(old/c['path'])==c['sha256'], 'Historical unsupported images must remain preserved'
    provenance=json.loads((directory/'tooling-provenance.json').read_text())
    assert provenance['referenceRevision']==expected['revision'] and provenance['referenceArchiveSha256']==expected['sha256']
    assert provenance['toolArtifact']['sha256']==report['sourceToolArtifact']
    replay=provenance['cleanReplay']
    assert replay['metadataByteIdentical'] is True and replay['filesCompared']==replay['byteIdenticalFiles']==33 and replay['changedFiles']==[]
    assert replay['nativeAnimationPhaseAcceptance'].startswith('pending;')
    return {'captures':32,'actualNativeProgressIndicators':32,'unsupportedHistoricalCaptures':64,'byteIdenticalReplayFiles':33,'accepted':False}

if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
