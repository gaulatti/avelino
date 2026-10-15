#!/usr/bin/env python3
"""Validate pinned alert, lifecycle and isolated text-layout evidence."""
import hashlib
import itertools
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/reference-investigations/alert-20261015'
def verify_boundaries(directory=ROOT/'evidence/reference-investigations/prose-boundaries-20261015'):
    directory=Path(directory);report=json.loads((directory/'investigation.json').read_text())
    assert report['accepted'] is False and report['existingExpectedImagesChanged'] is False
    assert report['reference']=='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    actual={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual==set(report['files'])|{'investigation.json'}
    for name,h in report['files'].items():
        path=Path(name);assert not path.is_absolute() and '..' not in path.parts
        assert hashlib.sha256((directory/path).read_bytes()).hexdigest()==h
    for folder,count in [('initial',32),('boundary',48)]:
        rows=json.loads((directory/folder/'measurements.json').read_text());assert len(rows)==count
        for c in rows:
            assert c['probeByteIdentical'] is True
            p=directory/folder/c['path'];assert p.read_bytes()==p.with_name(p.stem+'-probed.png').read_bytes()
    context=json.loads((directory/'context/measurements.json').read_text());assert len(context)==16
    mismatches=[]
    for c in context:
        if c['probed']:continue
        partner=next(p for p in context if p['text']==c['text'] and p['primary']==c['primary'] and p['hosted']==c['hosted'] and p['probed'])
        if (directory/'context'/c['path']).read_bytes()!=(directory/'context'/partner['path']).read_bytes():mismatches.append(c['path'])
    assert mismatches==report['untrustedContextWitnesses']==['text2-hosttrue-probefalse.png'],'Untrusted hosted renderer witness cannot be accepted'
    provenance=json.loads((directory/'tooling-provenance.json').read_text());replay=provenance['cleanReplay']
    assert provenance['toolArtifact']['sha256']==report['sourceToolArtifact'] and len(provenance['toolArtifact']['files'])==37
    assert replay['filesCompared']==replay['byteIdenticalFiles']==179 and replay['changedFiles']==[]
    if directory.resolve()==(ROOT/'evidence/reference-investigations/prose-boundaries-20261015').resolve():
        derived=json.loads((ROOT/'evidence/geometry/native-prose-boundaries.json').read_text());assert derived['reference']==report['reference'] and len(derived['cases'])==84
        assert derived['untrustedContextWitnesses']==mismatches
        for c in derived['cases']:
            folder,sourcePath=c['sourcePath'].split('/',1);rows=json.loads((directory/folder/'measurements.json').read_text());raw=next(r for r in rows if r['path']==sourcePath)
            assert c['text']==raw['text'] and c['componentWidth']==raw['componentWidth'] and c['componentHeight']==raw['componentHeight']
            assert c['dpr']==2 and c['sourcePath']!='context/text2-hosttrue-probefalse.png'
            if folder=='context':assert raw['hosted'] is False and raw['probed'] is False and c['weight']==('medium' if raw['size']==14 else 'semibold')
    return {'boundaryRecords':96,'trustedQtCases':84,'byteIdenticalReplayFiles':179,'untrustedHostedWitnesses':1}

def verify(directory=DIRECTORY):
    directory=Path(directory);report=json.loads((directory/'investigation.json').read_text())
    reference=json.loads((ROOT/'reference/source-manifest.json').read_text())['references']['desktop']
    assert report['accepted'] is False and report['existingExpectedImagesChanged'] is False
    assert report['reference']==reference['revision']
    actual={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual==set(report['files'])|{'investigation.json'}
    for name,h in report['files'].items():
        path=Path(name);assert not path.is_absolute() and '..' not in path.parts
        assert hashlib.sha256((directory/path).read_bytes()).hexdigest()==h,name
    data=json.loads((directory/'captures.json').read_text());assert data['reference']==reference['revision']
    captures=data['captures'];assert len(captures)==256
    assert {c['api'] for c in captures}=={'BleeckerAlert','BleeckerButton'}
    alerts=[c for c in captures if c['api']=='BleeckerAlert'];assert len(alerts)==248
    expected=set(itertools.product(['info','success','warning','error'],['normal','intrinsic','narrow','long'],['light','dark'],[1,1.5],[1,2]))
    assert expected<={(c['alertType'],c['variant'],c['appearance'],c['textScale'],c['dpr']) for c in alerts},'Missing alert variant/constraint matrix'
    for c in captures:
        assert c['source']==reference['revision'] and c['captureMethod']=='SwiftUI.ImageRenderer/CoreGraphics'
        assert c['status']=='proposed reference candidate; no baseline approval'
        assert c['environmentDisplayScale']==c['dpr'] and c['componentSize']['width']>0 and c['componentSize']['height']>0
        assert all(Path(c[k]).name==c[k] for k in ['path','instrumentedPath'])
        original=(directory/c['path']).read_bytes();probed=(directory/c['instrumentedPath']).read_bytes()
        assert original==probed and c['instrumentedPngByteIdentical'] is True,'Source alert instrumentation identity failed'
        assert original[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',original[16:24])==(c['width']*c['dpr'],c['height']*c['dpr'])
        if c['api']=='BleeckerAlert' and c['contentMode'] in ['text','custom-font']:
            f=c['resolvedLabelFonts']['content'];custom=c['contentMode']=='custom-font'
            assert f['pointSize']==(18 if custom else 13) and f['postScriptName']==('LibreFranklin-SemiBold' if custom else 'LibreFranklin-Regular')
    behavior=data['behavior'];assert len(behavior)==96
    assert {(c['alertType'],c['action'],c['appearance'],c['textScale']) for c in behavior}==set(itertools.product(['info','success','warning','error'],['activate','producer-update','disabled-click','outside-release','replace','reopen'],['light','dark'],[1,1.5]))
    for c in behavior:
        action=c['action'];reset=action in ['replace','reopen'];activated=action in ['activate','producer-update']
        assert (c['counter'],c['mounts'],c['unmounts'])==(int(activated),2 if reset else 1,int(reset)),'Invalid source alert lifecycle transition'
        assert c['nativeDpr']>0 and set(c['nativeWindowState'])=={'key','main','applicationActive'}
        assert c['titleAfterAction']==('Updated alert title' if action=='producer-update' else 'Edition ready')
        expectedType=('success' if c['alertType']=='error' else 'error') if action=='producer-update' else c['alertType']
        assert c['typeAfterAction']==expectedType
    text=json.loads((directory/'text-layout/measurements.json').read_text());assert len(text)==96
    assert {(c['text'],c['size'],c['weight'],c['offeredWidth'],c['dpr']) for c in text}==set(itertools.product(['Create an edition to get started.','One two three four five six'],[13,18],['regular','semibold'],[120,180,240,250,265,300],[1,2]))
    for c in text:
        assert Path(c['path']).name==c['path']
        original=directory/'text-layout'/c['path'];probed=original.with_name(original.stem+'-probed.png')
        assert c['probeByteIdentical'] is True and original.read_bytes()==probed.read_bytes(),'Source text instrumentation identity failed'
        assert c['componentWidth']==c['probedWidth'] and c['componentHeight']==c['probedHeight'],'Source text measurement changed under instrumentation'
        assert c['componentWidth']>0 and c['componentHeight']>0 and c['lines']
    provenance=json.loads((directory/'tooling-provenance.json').read_text())
    assert provenance['referenceRevision']==reference['revision'] and provenance['referenceArchiveSha256']==reference['sha256']
    assert provenance['toolArtifact']['sha256']==report['sourceToolArtifact'] and len(provenance['toolArtifact']['files'])==37
    replay=provenance['cleanReplay'];assert replay['filesCompared']==replay['byteIdenticalFiles']==722 and replay['changedFiles']==[]
    if directory.resolve()==DIRECTORY.resolve():
        assert (ROOT/'evidence/geometry/native-alert.json').read_bytes()==(directory/'captures.json').read_bytes()
        derived=json.loads((ROOT/'evidence/geometry/native-alert-text-layout.json').read_text())
        assert derived['reference']==reference['revision'] and derived['cases']==text
    boundaries=verify_boundaries()
    return {'boundaries':boundaries,'captures':256,'alertCaptures':248,'nativeLifecycleCases':96,'isolatedTextCases':96,'instrumentationIdentityWitnesses':352,'byteIdenticalReplayFiles':722,'accepted':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
