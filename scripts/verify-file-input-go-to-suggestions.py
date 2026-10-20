#!/usr/bin/env python3
"""Audit scoped Linux selection evidence; native mirror acceptance stays pending."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/development/file-input-go-to-suggestions-20261018'


def metadata(raw,name):
    text=raw.decode();match=re.search(r'"'+re.escape(name)+r'"\s*:\s*',text)
    assert match
    _,length=json.JSONDecoder().raw_decode(text[match.end():])
    return text[match.end():match.end()+length].encode()


def verify():
    read=lambda name:json.loads((DIRECTORY/name).read_text())
    report=read('validation.json')
    assert report['accepted'] is report['physicalInput'] is report['physicalDisplay'] is report['physicalListening'] is False
    assert report['reference']=='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['desktopCandidateCoverage']==[75,80]and report['acceptedDesktopEntries']==0
    assert report['expectedImagesChanged'] is False and report['tolerance']=='none'and report['approvedExceptions']==[]
    assert report['focusedQtTargets']==8 and report['finalFullQtSuiteRerun'] is False
    assert report['sourceAttempts']==[62,63,64]and report['producer']=='file-input-qt-v64'
    assert report['speechPolicyChanged'] is False
    for key in ('nativeHierarchy','nativeReaderComparison','nativeTiming','speechEngineAudioVerification','completeFileChooser','independentMachine'):
        assert report[key]=='pending'
    files=read('files.json')
    assert set(files)=={str(p.relative_to(DIRECTORY))for p in DIRECTORY.rglob('*')if p.is_file()and p.name!='files.json'}
    for name,row in files.items():
        raw=(DIRECTORY/name).read_bytes()
        assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'],name
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('avelino_suggestion_restore',DIRECTORY/'tools/reconstruct.py')
    loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(loader)
    sources,runtime,records=map(read,('source-specs.json','runtime-spec.json','records-spec.json'))
    assert set(sources)=={f'file-input-qt-v{n}'for n in (62,63,64)}
    used=set()
    def raw_record(row):
        raw=b''.join(loader.chunk_bytes(part)for part in row['chunks'])
        used.update(part['sha256']for part in row['chunks'])
        assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256']
        return raw
    def record(name):return json.loads(raw_record(records[name]))
    for table in [*(row['files']for row in sources.values()),runtime,records]:
        for row in table.values():raw_record(row)
    assert used=={p.stem for p in(DIRECTORY/'blobs').glob('*.gz')}
    for producer,row in sources.items():
        source=row['files'];assert len(source)==report['sourceFiles']==571
        assert record('producers/'+producer+'/inputs.json')['files']=={name:value['sha256']for name,value in source.items()}
        assert {'src/Avelino/filechoosersuggestions.h','src/Avelino/filechoosersuggestions.cpp'}<=set(source)
        result=record('producers/'+producer+'/result.json')
        commands=record('producers/'+producer+'/commands.json')
        verbose=raw_record(records['producers/'+producer+'/ui-verbose.log']).decode()
        if producer.endswith('62'):
            assert result['exitCode']==8 and result['failedStep']=='ui-tests'
            assert 'class destructor may have already run'in verbose
        else:
            assert result['exitCode']==0 and len(commands)==8 and all(c['exitCode']==0 for c in commands)
            for test in ('actualGoToAccessibleSelectionEventsKeepTextFocusAndRespectSingleChoice','closingGoToDuringSelectionNotificationKeepsOwner','removingGoToOwnerDuringSelectionNotification'):
                assert verbose.count('PASS   : FileInputUiTests::'+test+'()')==2,test
    package=record('package/result.json');assert package['exitCode']==0 and package['contexts']==8 and package['freshConsumerBuild'] is True
    assert package['libraryAndConsumerProjectSourcesAbsentAtRuntime'] is True
    package_inputs=record('package/inputs.json');assert package_inputs['producer']==report['producer']
    assert package_inputs['packageFiles']=={name.removeprefix('install/'):row['sha256']for name,row in runtime.items()if name.startswith('install/')}
    assert package_inputs['consumerSha256']==runtime['consumer-build/InstalledConsumer']['sha256']
    assert record('provisional-package/inputs.json')['producer']=='file-input-qt-v63'
    for name,row in read('closed-stability.json').items():
        current=(DIRECTORY/'captures'/name).read_bytes();prior=ROOT/row['prior'];capture=json.loads(current)
        assert capture['structuralChecks']=='passed'and capture['accepted'] is False
        assert len(capture['actions'])==30 and capture['images']==49
        for section in ('closed','sizing'):assert metadata(current,section)==metadata(prior.read_bytes(),section)
        for image,digest in row['images'].items():
            raw=(DIRECTORY/'captures'/image).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==digest and raw==(prior.parent/image).read_bytes()
    assert sum(len(row['images'])for row in read('closed-stability.json').values())==report['closedImagesUnchanged']==256
    profiles=list((DIRECTORY/'display/output').glob('file-input-*.json'))
    assert len(profiles)==report['displayProfiles']==8 and record('display/result.json')['exitCode']==0
    for path in profiles:
        value=json.loads(path.read_text());assert value['structuralChecks']=='passed'and value['accepted'] is False
    for number in (11,12,13,14):
        prefix=f'readers/file-input-go-to-reader-v{number}/'
        session=record(prefix+'session-result.json');assert session['waitCode']==0 and session['containerExit']=='0'
        assert record(prefix+'collect-result.json')['code']==0
        exercise=record(prefix+'exercise-result.json');result=read(prefix+'operator-controls-v1/result.json')
        inputs=record(prefix+'inputs.json')
        assert inputs['packageFiles']==record(('provisional-package/'if number<13 else'package/')+'inputs.json')['packageFiles']
        if number<13:
            assert exercise['code']==1 and result['status']=='failed'
            assert 'observation did not arrive'in result['error']
            if number==12:
                raw=raw_record(records[prefix+'orca-debug.log'])
                failure=next(p for p in result['phases']if p['phase']=='operator-failure')
                assert raw.index(b"SPEECH OUTPUT: '/probe/fixtures/Alpine.'")>failure['readerLogBytes']
            continue
        assert exercise['code']==0 and result['status']=='passed'and len(result['phases'])==21
        assert result['nativeKeyFlow']==result['directAssistiveTextEdit']=='passed'
        assert inputs['producer']==report['producer']and inputs['speechPolicyChanged'] is False
        assert inputs['observationLimitSeconds']==10 and inputs['compilerLoadDuringReader'] is False
        phases={p['phase']:p for p in result['phases']};receipt=record(prefix+'validation.json')
        assert receipt['accepted'] is False and receipt['singleSelectionQuery']=='passed'
        raw=raw_record(records[prefix+'orca-debug.log']);assert hashlib.sha256(raw).hexdigest()==receipt['orcaLogSha256']
        events=[json.loads(line)for line in raw_record(records[prefix+'events.jsonl']).splitlines()]
        arrow=phases['go-to-native-arrows-preserve-input'];begin=arrow['observations']['arrowStartTime'];end=arrow['time']
        assert 0<end-begin<10 and receipt['arrowIntervalSeconds']==end-begin
        selection=[e for e in events if begin<=e['time']<=end and ('selected'in e['event']or 'selection'in e['event'])]
        assert selection==receipt['arrowSelectionEvents']
        for target,state in (('Alpha',0),('Alpine',1)):
            assert any(e['event']=='object:state-changed:selected'and e['name']=='/probe/fixtures/'+target and e['detail1']==state for e in selection)
        assert any(e['event']=='object:selection-changed'and e['name']=='Folder suggestions'for e in selection)
        for name,offset,target in [('go-to-native-arrows-preserve-input','arrowReaderStartBytes','Alpine'),('go-to-assistive-selection-keeps-input','readerStartBytes','Alphabet')]:
            phase=phases[name];observation=phase['observations']
            assert observation['raw']=='/probe/fixtures/Al'and observation['pathHasKeyboardFocus'] is True
            assert observation['assistiveSelected']==['/probe/fixtures/'+target]
            start=observation[offset];stop=phase['readerLogBytes'];window=raw[start:stop]
            assert hashlib.sha256(window).hexdigest()==receipt['speechWindows'][name]['sha256']
            assert ("SPEECH OUTPUT: '/probe/fixtures/"+target+".'").encode()in window
            assert ("SPEECH DISPATCHER: Speaking '/probe/fixtures/"+target+".'").encode()in window
        assert phases['go-to-assistive-selection-keeps-input']['observations']['owner']==''
        for key in ('nativeHierarchy','nativeReaderComparison','nativeTiming','speechEngineAudioVerification'):assert receipt[key]=='pending'
    portable=read('portable/result.json');assert portable['exitCode']==0 and portable['libraryAndConsumerSourcesAbsentAtRuntime'] is True
    current=(DIRECTORY/'portable/light-text1-dpr1.json').read_bytes();original=(DIRECTORY/'captures/light-text1-dpr1.json').read_bytes()
    for section in ('closed','sizing'):assert metadata(current,section)==metadata(original,section)
    for row in json.loads(current)['closed']:
        name='light-text1-dpr1-'+row['configuration']['id']+'.png'
        assert (DIRECTORY/'portable'/name).read_bytes()==(DIRECTORY/'captures'/name).read_bytes()
    print('Owned GoTo suggestions: source attempts, lifecycle regressions, source-free consumers, selection events, real reader speech and portable replay verified; native parity gates pending')


if __name__=='__main__':verify()
