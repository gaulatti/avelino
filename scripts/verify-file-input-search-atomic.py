#!/usr/bin/env python3
"""Verify scoped native observations and isolated Qt mechanism receipts."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'evidence/reference-investigations/file-input-search-atomic-20261021'
LINUX=ROOT/'evidence/development/file-input-search-atomic-20261021'
PIN='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
OBJECT='\ufffc'
digest=lambda value:hashlib.sha256(value).hexdigest()
read=lambda directory,name:json.loads((directory/name).read_text())


def audit_files(directory):
    files=read(directory,'files.json')
    assert set(files)=={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name!='files.json'}
    for name,record in files.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        payload=(directory/name).read_bytes()
        assert len(payload)==record['bytes'] and digest(payload)==record['sha256'],name
    return files


def native_phases(projections):
    for key in ['accepted','physicalInput','rasterAccepted','readerComparisonAccepted']:assert projections[key] is False,key
    phases={row['phase']:row for row in projections['phases']}
    assert len(phases)==len(projections['phases'])==projections['phaseCount']==31
    def field(name):
        for line in phases[name]['fieldLines']:
            found=re.search(r'search text field .*?Value: (.*), ID: Search$',line)
            if found:return found.group(1)
        return ''
    def labels(name):
        return [line.split('menu button ',1)[1] for line in phases[name]['fieldLines'] if 'menu button ' in line]
    assert field('filename-created')==OBJECT and phases['filename-created']['selectedText'] is None
    assert phases['filename-first-backspace']['selectedText']==OBJECT and field('filename-first-backspace')==OBJECT
    assert field('filename-second-backspace')==field('keyboard-undo-attempt')==''
    assert phases['filename-menu-restored']['selectedText']==OBJECT
    assert field('trailing-draft-x')==OBJECT+'x'
    assert field('two-filename-tokens')==2*OBJECT and labels('two-filename-tokens')==['Filename: avelinoulnacerulean','Filename: x']
    assert phases['two-token-first-backspace']['selectedText']==OBJECT
    assert field('two-token-second-backspace')==OBJECT and labels('two-token-second-backspace')==['Filename: avelinoulnacerulean']
    assert phases['left-selects-token']['selectedText']==OBJECT
    assert field('leading-draft-y')=='y'+OBJECT
    assert labels('leading-token-commit')==['Filename: y','Filename: avelinoulnacerulean']
    assert field('inter-token-draft-z')==OBJECT+'z'+OBJECT
    assert field('forward-delete-adjacent-token').count(OBJECT)==1
    assert field('replace-first-token')=='name'+OBJECT and labels('replace-first-token')==['Everything: pine']
    assert field('replacement-undone')==2*OBJECT and phases['replacement-undone']['selectedText']==OBJECT
    assert labels('replacement-undone')==['Everything: avelinoulnacerulean','Everything: pine']
    assert field('replacement-redone')=='name'+OBJECT and labels('replacement-redone')==['Everything: pine']
    def disabled(name,action):return any(re.search(r'\(disabled\) '+action+r', ID:',line) for line in phases[name]['menuLines'])
    assert disabled('two-token-undo-menu','Undo') and disabled('two-token-undo-menu','Redo')
    assert not disabled('replacement-undo-menu','Undo') and disabled('replacement-undo-menu','Redo')
    assert disabled('replacement-redo-menu','Undo') and not disabled('replacement-redo-menu','Redo')
    for name,expected in [('compound-everything',{'avelinoulnacerulean-name.txt','pine-only.txt'}),('compound-mixed',{'pine-only.txt'}),('compound-both-everything',{'pine-only.txt'})]:
        phase=phases[name]
        names={Path(url).name for line in phase['controlledResultLines'] for url in re.findall(r'file://[^\s,]+',line)}
        assert names==expected,(name,names)
        assert not phase['busyLines']
        assert any('avelino-file-search-fixtures' in line and 'Value: 1' in line for line in phase['scopeLines'])
    return phases


def mechanism(runtime,version):
    assert runtime['exitCode']==0 and runtime['failure']=='' and runtime['qt']=='6.8.3'
    for key in ['registeredInAvelino','nativeMatchingAccepted','physicalInput','accepted']:assert runtime[key] is False,key
    assert [variant['variant'] for variant in runtime['variants']]==['plain','rich']
    for variant in runtime['variants']:
        phases={row['phase']:row for row in variant['observations']}
        assert len(phases)==len(variant['observations'])==(24 if version==3 else 14)
        committed=phases['committed'];assert committed['plainText']==OBJECT and not committed['canUndo'] and not committed['canRedo']
        if variant['variant']=='plain':assert committed['propertyText']==OBJECT
        assert phases['first-backspace']['plainText']==OBJECT and phases['first-backspace']['selectedText']==OBJECT
        assert phases['second-backspace']['plainText']=='' and phases['second-backspace']['canUndo']
        assert phases['deletion-undo']['segments']==committed['segments'] and phases['deletion-undo']['canRedo']
        assert phases['trailing-draft']['plainText']==OBJECT+'x'
        assert phases['two-tokens']['plainText']==2*OBJECT
        assert [row['query'] for row in phases['two-tokens']['segments']]==['avelinoulnacerulean','x']
        assert phases['leading-draft']['plainText']=='y'+2*OBJECT
        assert phases['leading-token']['plainText']==3*OBJECT
        assert phases['middle-draft']['plainText']==OBJECT+'z'+2*OBJECT
        assert phases['forward-delete']['plainText']==OBJECT+'z'+OBJECT
        assert phases['replacement-undo']['segments'][0]['query']=='y'
        assert phases['replacement-redo']['plainText']=='namez'+OBJECT
        if version==1:
            assert not committed['accessibleExists']
        else:
            assert committed['accessibleExists'] and committed['accessibleRole']==42
            assert committed['accessibleText']==OBJECT and committed['accessibleCharacterCount']==1
            assert committed['accessibleEditable'] is (version==3)
        if version==3:
            for name in ['deletion-undo','replacement-undo','assistive-undo']:assert phases[name]['selectedText']==OBJECT,name
            end=phases['leading-token'];assert end['scrollX']>0
            assert end['viewportSceneLeft']<=end['cursorSceneX']<=end['viewportSceneLeft']+end['viewportWidth']-1
            assert phases['scroll-to-start']['scrollX']==0
            assert phases['assistive-replacement']['plainText']==phases['assistive-redo']['plainText']=='name'+OBJECT
            assert phases['assistive-readonly']['plainText']==phases['assistive-disabled']['plainText']=='name'+OBJECT
            assert phases['assistive-undo']['segments']==phases['ime-preedit']['segments']
            assert phases['ime-preedit']['plainText']==2*OBJECT
            assert phases['ime-commit-between-tokens']['plainText']==OBJECT+'かな'+OBJECT
            segments=phases['ime-commit-between-tokens']['segments']
            assert segments[0]['query']=='avelinoulnacerulean' and segments[2]['query']=='pine'
            assert phases['ime-undo']['plainText']==2*OBJECT
            assert phases['ime-redo']['plainText']==OBJECT+'かな'+OBJECT
    return runtime


def protected_fields(value,path=''):
    result={}
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='status' or any(s in key.lower() for s in ['accept','capture','reference','toleran','exception','mask','comparison']):result[path+'/'+key]=item
            else:result.update(protected_fields(item,path+'/'+key))
    elif isinstance(value,list):
        for index,item in enumerate(value):result.update(protected_fields(item,path+'/'+str(index)))
    return result


def verify():
    native_files=audit_files(NATIVE);linux_files=audit_files(LINUX)
    projections=read(NATIVE,'field-projections.json');native_phases(projections)
    publication=read(NATIVE,'publication.json');observations=read(NATIVE,'observations.json')
    assert publication['publishedRawRecords']==[37] and publication['originalRawRecordCount']==37
    for key in ['broadDraftResultListingsPublished','nativeCaptureToolSourcePublished','accepted']:assert publication[key] is False
    exported=(NATIVE/publication['storedExport']).read_bytes()
    assert digest(exported)==publication['sourceExport']['sha256']
    assert json.loads(json.loads(exported)['content'][0]['text'])==projections
    assert publication['sourceExport']==observations['records'][-1]
    assert all(record['sourceByteOffset']>0 and len(record['argumentsCodeSha256'])==64 for record in observations['records'])
    assert observations['reference']==PIN and observations['libraryObjectSha256']=='61d1e55c6f9c17c841eded420066c72b5611ec51af8c5a4821306f1751ea6514'
    for key in ['accepted','physicalInputAccepted','nativeReaderComparisonAccepted','rasterAccepted','generalQueryReadinessAccepted','keyboardUndoShortcutDispatchEstablished','independentNativeLibraryRebuild','nativeProcessStillRunning']:assert observations[key] is False,key
    assert observations['callerWasLaunchedAndNormallyClosed'] and observations['menuUndoRedoPositiveControlObserved'] and observations['conjunctionObservedForControlledFixture']
    assert observations['ownerResults']==read(NATIVE,'ui-trace-final.json')['steps'][-1]['results']==[]
    assert read(NATIVE,'caller-build.json')['libraryUnchanged'] is True
    closure=read(NATIVE,'closure-check.json');assert closure['pid']==observations['nativePid']
    assert closure['exitCode']==1 and not closure['stdout'].strip() and closure['accepted'] is False
    assert closure['libraryObjectSha256']==observations['libraryObjectSha256']
    report=read(LINUX,'validation.json')
    assert report['nativeManifestSha256']==digest((NATIVE/'files.json').read_bytes())
    assert report['nativePhases']==31 and report['prototype3PhasesPerVariant']==24
    assert report['platform']=='offscreen' and report['backend']=='software'
    for key,value in report.items():
        if key.endswith(('Changed','Executed','Established','Accepted')) or key in ['accepted','registeredInAvelino']:assert value is False,key
    for version in [1,2,3]:
        path=LINUX/f'prototype{version}';inputs=read(path,'inputs.json');result=read(path,'result.json');runtime=read(path,'output/runtime.json')
        assert result['exitCode']==0 and result['sourceUnchanged'] is True and result['productionImplementationChanged'] is result['accepted'] is False
        assert result['runtime']==runtime;mechanism(runtime,version)
        for key in ['productionLibraryMounted','productionConsumerMounted','registeredInAvelino','accepted']:assert inputs[key] is False,key
        for name,expected in inputs['sourceFiles'].items():assert digest((path/'source'/name).read_bytes())==expected
        log=read(path,'run-log.json');stored=(path/log['stored']).read_bytes();raw=gzip.decompress(stored)
        assert log['rawBytesPreserved'] is True and len(raw)==log['rawBytes'] and digest(raw)==log['rawSha256']
        assert len(stored)==log['storedBytes'] and digest(stored)==log['storedSha256']
        binary=read(path,'binary.json');assert binary['binaryPublished'] is False and len(binary['sha256'])==64
        assert binary['imageId'] in inputs['command']
        assert binary['imageId']=='sha256:c32e246cda73ab6992d808ceb551fa569fdf8ee85308f82d2bf1b15a96e69b14'
    product=read(LINUX,'product-checkpoint.json');assert product['revision']==report['sourceParent']
    assert product['productionSourceChanged'] is False and product['scalarQueryModeGapConfirmed'] is True
    for name,expected in product['files'].items():
        value=subprocess.check_output(['git','show',product['revision']+':'+name],cwd=ROOT)
        assert digest(value)==expected,name
    previous=json.loads(subprocess.check_output(['git','show',product['revision']+':docs/parity-inventory.json'],cwd=ROOT))
    current=read(ROOT,'docs/parity-inventory.json');before=protected_fields(previous);after=protected_fields(current)
    for name,value in before.items():assert after[name]==value,name
    return {'nativeFiles':len(native_files),'linuxFiles':len(linux_files),'nativePhases':31,'prototypePhases':104,'preexistingProtectedValuesUnchanged':len(before),'productionIntegrated':False,'accepted':False}


if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
