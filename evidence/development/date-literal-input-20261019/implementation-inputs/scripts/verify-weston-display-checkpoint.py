#!/usr/bin/env python3
"""Verify the complete historical display run, without native acceptance."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]
CAPSULE=ROOT/'evidence/development/weston-display-20261018'


def verify():
    read=lambda name:json.loads((CAPSULE/name).read_text())
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    manifest=read('files.json')
    assert set(manifest)=={str(p.relative_to(CAPSULE))for p in CAPSULE.rglob('*')if p.is_file()and p!=CAPSULE/'files.json'}
    for name,row in manifest.items():
        path=CAPSULE/name;assert path.stat().st_size==row['bytes']and digest(path)==row['sha256'],name
    result=read('result.json');producer=read('producer-result.json');spec=read('source-specs.json');inputs=read('inputs.json')
    assert not result['accepted']and result['acceptedDesktopEntries']==0 and result['desktopCandidates']==76
    assert not result['referencePinsChanged']and result['approvedExceptions']==[]
    assert result['completeDisplayGatePassed']and result['records']==304 and result['profiles']==8 and result['fixturesPerProfile']==38
    assert not result['previousCaptureFailurePermanentFixProven']and not result['currentDateLiteralSourceIncluded']
    assert producer['exitCode']==producer['scriptExitCode']==0 and producer['unexpectedCores']==[]
    assert producer['libraryAndConsumerProjectSourcesAbsentAtRuntime']
    assert len(read('commands.json'))==1 and read('commands.json')[0]['exitCode']==0
    typography=ROOT/'evidence/development/navigation-cjk-metrics-20261018'
    compositor=ROOT/'evidence/development/weston-popup-parent-20261018'
    assert digest(typography/'files.json')==spec['parentTypographyManifestSha256']
    assert digest(compositor/'files.json')==spec['parentCompositorManifestSha256']
    previous=json.loads((typography/'source-specs.json').read_text());package=json.loads((typography/'package/inputs.json').read_text())
    assert spec['coreFiles']==previous['coreFiles']and len(spec['coreFiles'])==604
    assert spec['consumerFiles']==previous['consumerFiles']==inputs['consumerFiles']and len(spec['consumerFiles'])==149
    assert inputs['consumerSha256']==package['consumerSha256']and inputs['packageFiles']==package['packageFiles']
    assert spec['runtimeSourceCheckpoint']=='97fe54cbed3d53ac7125ab8141f831f40dd7ac2d'
    assert inputs['imageId']==json.loads((compositor/'toolchain/result.json').read_text())['imageId']
    assert digest(CAPSULE/'check.sh')==inputs['scriptSha256']==previous['liveScripts']['scripts/check-display-sessions.sh']
    assert digest(compositor/'implementation-inputs/tools/weston-popup-parent.patch')==inputs['patchSha256']
    line=next(line.strip()for line in (CAPSULE/'check.sh').read_text().splitlines()if line.strip().startswith('for fixture in '))
    fixtures=set(line.removeprefix('for fixture in ').removesuffix('; do').split());assert len(fixtures)==38
    groups=Counter();seen={};tooltips=file_inputs=0
    for path in (CAPSULE/'output').glob('*.json'):
        row=json.loads(path.read_text())
        if 'sessionCaptureSha256'not in row:continue
        assert not row['physicalDisplay']and not row['hardwareAcceleration']
        image=path.with_suffix('.png');assert digest(image)==row['windowCaptureSha256']
        assert digest(path.parent/row['sessionCapture'])==row['sessionCaptureSha256']
        raw=image.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II',raw[16:24])==(round(row['width']*row['dpr']),round(row['height']*row['dpr']))
        group=(row['platform'],row['graphicsApi'],row['dpr']);groups[group]+=1
        present=seen.setdefault(group,set());assert row['fixture']not in present;present.add(row['fixture'])
        assert row['textScale']==(1 if row['dpr']==1 else 1.5)
        if row['fixture']=='tooltip':
            assert row['tooltipChecks']==row['qtAccessibilityChecks']==row['focusChecks']=='passed'
            assert row['repeatedRemountFrames']==20 and row['retainedCallerEditorFocus']and row['tooltipWindowType']==13
            assert 'eglSwapBuffers failed with 0x300d'not in path.with_suffix('.log').read_text()
            tooltips+=1
        if row['fixture']=='file-input':assert row['structuralChecks']=='passed'and not row['accepted'];file_inputs+=1
    assert sum(groups.values())==304 and len(groups)==8 and set(groups.values())=={38}
    assert set(groups)=={(platform,api,dpr)for platform in ['xcb','wayland']for api in [1,3]for dpr in [1,2]}
    assert all(value==fixtures for value in seen.values())and tooltips==file_inputs==8
    validation=read('validation.json');assert validation['records']==304 and validation['tooltipRemountFrames']==160
    for row in validation['rows']:assert digest(CAPSULE/'output'/row['path'])==row['sha256']
    print('Historical Weston display gate:304/304 raw window/session pairs,8 profiles,160 tooltip remount frames,8 FileInput reports; core604/consumer149; current date-literal source excluded; native acceptance pending')


if __name__=='__main__':verify()
