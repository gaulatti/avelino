#!/usr/bin/env python3
"""Recompute the captured search-token Undo baseline and runtime bindings."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'evidence/reference-investigations/file-input-search-token-baseline-20261021'
DIRECTORY=ROOT/'evidence/development/file-input-search-token-baseline-20261021'
digest=lambda value:hashlib.sha256(value).hexdigest()


def audit_files(directory):
    files=json.loads((directory/'files.json').read_text())
    assert set(files)=={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name!='files.json'}
    for name,row in files.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        value=(directory/name).read_bytes()
        assert len(value)==row['bytes'] and digest(value)==row['sha256'],name
    return files


def text_blocks(value):
    if not isinstance(value,dict):return []
    if value.get('type')=='text':
        text=value.get('text','')
        try:nested=json.loads(text)
        except (json.JSONDecodeError,TypeError):nested=None
        return text_blocks(nested) if isinstance(nested,dict) and 'content' in nested else [text]
    return [text for child in value.get('content',[]) for text in text_blocks(child)]


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
    native_files=audit_files(NATIVE)
    native=lambda name:json.loads((NATIVE/name).read_text())
    limits=native('limits.json')
    for key,value in limits.items():
        if key!='scope':assert value is False,key
    observations=native('observations.json')
    assert observations['reference']=='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert observations['nativeDeletionUndoRedoPositiveControlComplete'] is observations['nativeUndoBaselinePolicyConfirmed'] is True
    for key in ['nativeProcessStillRunning','accepted','physicalInput','readerComparisonAccepted','rasterAccepted','independentNativeLibraryRebuild','nativeMembershipReadinessAccepted']:assert observations[key] is False
    assert observations['libraryObjectSha256']=='61d1e55c6f9c17c841eded420066c72b5611ec51af8c5a4821306f1751ea6514'
    captures=native('records.json');assert len(captures)==15
    texts={}
    for row in captures:
        value=(NATIVE/row['path']).read_bytes();assert digest(value)==row['sha256']
        texts[row['path']]='\n'.join(text_blocks(json.loads(value)))
    enabled=lambda text,label:bool(re.search(r'^\s*\d+ '+label+r', ID:',text,re.M))
    disabled=lambda text,label:bool(re.search(r'^\s*\d+ \(disabled\) '+label+r', ID:',text,re.M))
    before=texts['captures/before-19.json']
    assert disabled(before,'Undo') and disabled(before,'Redo')
    assert all(enabled(before,name) for name in ['Cut','Copy','Delete'])
    assert 'Selected text: ```\n\ufffc\n```' in texts['captures/control-01.json']
    assert 'Everything: avelinoulnacerulean' not in texts['captures/control-02.json']
    assert enabled(texts['captures/control-03.json'],'Undo') and disabled(texts['captures/control-03.json'],'Redo')
    assert 'Everything: avelinoulnacerulean' in texts['captures/control-04.json']
    assert disabled(texts['captures/control-05.json'],'Undo') and enabled(texts['captures/control-05.json'],'Redo')
    assert 'Everything: avelinoulnacerulean' not in texts['captures/control-06.json']
    assert 'search text field (settable) Search' in texts['captures/control-06.json']
    assert native('ui-trace-final.json')['steps'][-1]['results']==[]
    assert digest((NATIVE/'ui-trace-final.json').read_bytes())==observations['traceSha256']
    assert native('caller-build.json')['libraryUnchanged'] is True

    files=audit_files(DIRECTORY)
    records=json.loads((DIRECTORY/'records.json').read_text());used=set()
    def raw(name):
        row=records[name];stored=row['stored'];assert stored in files;used.add(stored)
        payload=(DIRECTORY/stored).read_bytes();value=gzip.decompress(payload) if stored.endswith('.gz') else payload
        assert digest(value)==row['sha256'] and len(value)==row['bytes'] and Path(stored).stem==row['sha256'],name
        return value
    record=lambda name:json.loads(raw(name))
    for name in records:raw(name)
    assert used=={name for name in files if name.startswith(('images/','blobs/'))}
    report=json.loads((DIRECTORY/'validation.json').read_text())
    for key,value in report.items():
        if key=='accepted' or key.endswith(('Accepted','Changed')):assert value is False,key
    assert report['currentSourceAttempt']==40 and report['prototypeSourceAttempt']==report['runtimeEvidenceExecutedOnSource']==39
    assert report['focusedQtGroups']==9 and report['portableProfiles']==8 and report['closedPairs']==256
    assert raw('native-manifest.json')==(NATIVE/'files.json').read_bytes()
    module=report['moduleSha256'];consumer_sha=report['consumerSha256']
    specs=json.loads((DIRECTORY/'source-overrides.json').read_text());sources={}
    for number in [38,39,40]:
        source=record(f'source{number}/controller/inputs.json');sources[number]=source
        spec=specs[str(number)];assert source['parent']==spec['parent']==report['sourceParent']
        names=list(source['sourceFiles']);assert len(names)==spec['selectedFiles']==4116
        data=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=('\n'.join(source['parent']+':'+name for name in names)+'\n').encode());stream=io.BytesIO(data)
        for name in names:
            header=stream.readline().split()
            if len(header)==3:
                assert header[1]==b'blob';value=stream.read(int(header[2]));assert stream.read(1)==b'\n'
            else:assert header[-1]==b'missing';value=None
            if name in spec['overrides']:value=raw(f'source{number}/overrides/'+name)
            assert value is not None and digest(value)==source['sourceFiles'][name],(number,name)
        assert not stream.read()
        result=record(f'source{number}/controller/result.json')
        assert result['sourceUnchanged'] is True and result['accepted'] is False
        assert result['exitCode']==(8 if number==38 else 0)
    assert sources[39]['prototypeOnly'] is True and not sources[40].get('prototypeOnly',False)
    assert sources[39]['sourceFiles']==sources[40]['sourceFiles']
    red=raw('source38/controller/search-dpr1.log')
    assert len(re.findall(rb'^FAIL!',red,re.M))==2
    for name in [b'Filename',b'Everything']:assert b'committedTokensDoNotUndoEarlierLiteralEdits('+name+b')' in red
    for number in [39,40]:
        prefix=f'source{number}/controller/validation/'
        assert record(prefix+'result.json')['exitCode']==0
        assert record(prefix+'focused/result.json')['exitCode']==0
        assert b'100% tests passed, 0 tests failed out of 9' in raw(prefix+'focused/runtime.log')
        producer=record(prefix+'package-producer.json');assert producer['librarySha256']==module
        consumer=record(prefix+'consumer/result.json')
        assert consumer['exitCode']==0 and consumer['consumerSha256']==consumer_sha and consumer['moduleHashes']['libAvelino.so']==module
        assert len(consumer['availableReport']['phases'])==9 and consumer['unavailableReport']['providerUnavailable'] is True
        scope=record(prefix+'consumer/mount-scope.json')
        assert scope['libraryProjectMounted'] is False and scope['productionConsumerProjectMounted'] is True
    identity=record('source40/controller/validation/runtime-identity-v39-v40.json')
    measurements=record('source40/controller/validation/installed-prefix-hash-measurements-v39-v40.json')['filesBySource']
    assert identity['allSelectedSourceInputsIdentical'] is identity['allInstalledPrefixBytesIdentical'] is True
    assert measurements['39']==measurements['40'] and len(measurements['40'])==158
    assert measurements['40']['lib/qml/Avelino/libAvelino.so']==module
    diagnosis=record('diagnostic4/controller/result.json')
    assert diagnosis['exitCode']==0 and diagnosis['moduleSha256']==module and diagnosis['baselineChecksPassed'] is True
    assert len(diagnosis['baselineChecks'])==7 and all(diagnosis['baselineChecks'].values())
    assert record('diagnostic1/controller/result.json')['exitCode']==125
    assert record('diagnostic2/controller/result.json')['exitCode']==3
    lifetime=record('lifetime1/runtime.json');assert lifetime['exitCode']==0 and len(lifetime['cases'])==3
    for case in lifetime['cases']:assert case['cacheClearedBeforeNotification'] is case['destroyedSynchronously'] is case['setterReturned'] is True
    portable=record('portable7/controller/result.json');assert portable['exitCode']==0 and portable['displayProfiles']==8 and portable['runtimeFilesUnchanged'] is True
    assert portable['moduleSha256']==module and portable['consumerSha256']==consumer_sha
    for key in ['libraryProjectMounted','consumerProjectMounted','productBuildMounted']:assert portable[key] is False
    profiles=[name for name in records if name.startswith('portable7/output/display/') and name.endswith(('-standard.json','-scaled.json'))]
    assert len(profiles)==8
    for name in profiles:
        value=record(name);assert value['structuralChecks']=='passed' and value['accepted'] is False and len(value['phases'])==10
        assert all(not phase['busy'] and not phase['error'] for phase in value['phases'])
        for field in ['sessionCapture','finalWindowCapture']:assert digest(raw('portable7/output/display/'+value['displaySession'][field]))==value['displaySession'][field+'Sha256']
    for number in [13,14]:
        prefix=f'reader{number}/';inputs=record(prefix+'controller/inputs.json');result=record(prefix+'controller/result.json')
        assert inputs['moduleSha256']==module and result['exitCode']==0 and result['installedModuleUnchanged'] is result['probeSourcesUnchanged'] is True
        for name,expected in inputs['probeFiles'].items():assert digest(raw(prefix+'output/'+name))==expected
        operator=record(prefix+'output/operator-report.json');assert operator['status']=='passed' and len(operator['phases'])==17
        for key in ['accepted','physicalInput','readerNativeComparisonAccepted','speechEngineAudioAccepted']:assert operator[key] is False
        phases={phase['phase']:phase for phase in operator['phases']}
        assert phases['token-replacement']['observations']['tokenVisible'] is phases['token-redo']['observations']['tokenVisible'] is False
        assert phases['token-undo']['observations']['tokenLabel']=='Everything: avelinoulnacerulean'
        speech=raw(prefix+'output/orca-debug.log')
        for name,target in [('focused-result-speech','pine-only.txt'),('keyboard-result-speech','avelinoulnacerulean-name.txt')]:
            phase=phases[name];window=speech[phase['observations']['speechOffset']:phase['readerLogBytes']]
            for marker in [b'SPEECH OUTPUT:',b'SPEECH DISPATCHER: Speaking']:assert any(marker in line and target.encode() in line for line in window.splitlines())
    caches=json.loads((DIRECTORY/'generated-runtime-caches.json').read_text())['files']
    assert len(caches)==4
    for cache in caches:
        assert '/__pycache__/' in cache['path'] and cache['path'] not in records
        prefix,relative=cache['path'].split('/output/',1)
        assert relative not in record(prefix+'/controller/inputs.json')['probeFiles']
    comparison=record('closed7/controller/result.json');assert comparison['newModuleSha256']==module and comparison['consumerSha256']==consumer_sha
    assert comparison['byteIdentical']==comparison['frameAndStateIdentical']==256
    for row in comparison['closedComparisons']:
        prefix='closed7/output/'+row['context']+'/'
        assert raw(prefix+'old-'+row['id']+'.png')==raw(prefix+'new-'+row['id']+'.png')
        assert record(prefix+'old.json')['closed']==record(prefix+'new.json')['closed']
    binding=json.loads((DIRECTORY/'candidate-input-binding.json').read_text())
    assert binding['producerInputSha256']==digest(raw('source40/controller/inputs.json')) and binding['allSelectedCompiledInputsMatch'] is True
    assert set(binding['postExecutionDocumentationDifferences'])=={'docs/file-input-search.md','docs/parity-inventory.json'}
    for name,pair in binding['postExecutionDocumentationDifferences'].items():
        assert pair['producer']==sources[40]['sourceFiles'][name] and pair['current']==digest(raw('candidate/'+name))
    assert set(binding['postExecutionAuditFiles'])=={'scripts/verify-file-input-search-token-baseline.py','tests/contracts/test_file_search_token_baseline_evidence.py','.github/workflows/references.yml'}
    for name,expected in binding['postExecutionAuditFiles'].items():assert digest(raw('candidate/'+name))==expected
    invariance=json.loads((DIRECTORY/'inventory-invariance.json').read_text())
    before=protected_fields(json.loads(subprocess.check_output(['git','show',invariance['base']+':docs/parity-inventory.json'],cwd=ROOT)))
    after=protected_fields(record('candidate/docs/parity-inventory.json'))
    assert len(before)==invariance['existingProtectedFields'] and all(name in after and after[name]==value for name,value in before.items())
    print('Token Undo baseline: native positive control, exact38/39/40 source recovery, current40 focused/consumer checks and identical39 runtime verified; native parity remains pending')


if __name__=='__main__':verify()
