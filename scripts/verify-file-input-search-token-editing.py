#!/usr/bin/env python3
"""Audit captured token editing, Qt undo and installed-runtime evidence."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/development/file-input-search-token-editing-20261021'
digest=lambda raw:hashlib.sha256(raw).hexdigest()


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
    read=lambda name:json.loads((DIRECTORY/name).read_text())
    files=read('files.json')
    assert set(files)=={str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name!='files.json'}
    for name,row in files.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        value=(DIRECTORY/name).read_bytes();assert len(value)==row['bytes'] and digest(value)==row['sha256'],name
    records=read('records.json');used=set()
    def raw(name):
        row=records[name];stored=row['stored'];assert stored in files;used.add(stored)
        payload=(DIRECTORY/stored).read_bytes();value=gzip.decompress(payload) if stored.endswith('.gz') else payload
        assert len(value)==row['bytes'] and digest(value)==row['sha256'] and Path(stored).stem==row['sha256'],name
        return value
    def record(name):return json.loads(raw(name))
    for name in records:raw(name)
    assert used=={name for name in files if name.startswith(('images/','blobs/'))}
    report=read('validation.json')
    for key in ['accepted','nativeReaderComparisonAccepted','speechEngineAudioAccepted','physicalInputAccepted','physicalDisplayAccepted','independentMachineAccepted','expectedImagesChanged','referenceChanged','tolerancesChanged']:assert report[key] is False,key
    assert report['sourceAttempt']==report['installedConsumerSourceAttempt']==36
    assert report['coreRuntimeExecutedOnSourceAttempt']==34
    assert report['focusedQtGroups']==9 and report['portableProfiles']==8 and report['readerPhasesEach']==17
    historical=json.loads((ROOT/report['historicalFullSuite']['capsule']/'validation.json').read_text())
    assert report['historicalFullSuite']['sourceAttempt']==24 and report['historicalFullSuite']['groups']==historical['fullCtestGroups']==58
    native=ROOT/report['nativeObservations']/'files.json';assert raw('native-manifest.json')==native.read_bytes()
    specs=read('source-overrides.json');sources={}
    for number in range(28,38):
        prefix=f'source{number}/';source=record(prefix+'controller/inputs.json');sources[number]=source
        spec=specs[str(number)];assert source['parent']==spec['parent']==report['sourceParent']
        assert source['sourceUncommittedAtExecution'] is True and len(source['sourceFiles'])==spec['selectedFiles']
        names=list(source['sourceFiles'])
        batch=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=('\n'.join(source['parent']+':'+name for name in names)+'\n').encode());stream=io.BytesIO(batch)
        for name in names:
            header=stream.readline().split()
            if len(header)==3:
                assert header[1]==b'blob';value=stream.read(int(header[2]));assert stream.read(1)==b'\n'
            else:assert header[-1]==b'missing';value=None
            if name in spec['overrides']:value=raw(prefix+'overrides/'+name)
            assert value is not None and digest(value)==source['sourceFiles'][name],(number,name)
        assert not stream.read()
        result=record(prefix+'controller/result.json');assert result['sourceUnchanged'] is True and result['accepted'] is False
        expected=8 if number in [28,29,31] else 1 if number in [30,32] else 0
        assert result['exitCode']==expected
    assert len(sources[36]['sourceFiles'])==report['selectedSourceFiles']==4114
    assert b'Actual   (search->mode()): "filename"' in raw('source28/controller/search-dpr1.log')
    assert b'visible("bleeckerFileChooserSearchSuggestions")' in raw('source29/controller/search-dpr1.log')
    assert b'assistiveTokenReplacementUndoAndReadOnly()' in raw('source31/controller/search-dpr1.log')
    assert b'100% tests passed, 0 tests failed out of 9' in raw('source34/controller/validation/focused/run.log')
    assert record('source34/controller/validation/focused/result.json')['exitCode']==0
    identity=record('source36/controller/validation/runtime-identity-v34-v36.json')
    assert identity['sourceAttempts']==[34,36] and identity['allInstalledPrefixBytesIdentical'] is identity['allComponentAndInputTestSourceBytesIdentical'] is True
    assert identity['newExecutionClaimed'] is identity['accepted'] is False
    assert identity['installedPrefixFiles']==len(identity['installedPrefixFilesSha256'])==158
    core=[n for n in sources[36]['sourceFiles'] if n.startswith('src/') or n=='tests/components/filesearch.cpp']
    assert len(core)==identity['componentAndInputTestFiles']==223
    assert all(sources[34]['sourceFiles'][name]==sources[36]['sourceFiles'][name] for name in core)
    producer=record('source36/controller/validation/package-producer.json');module=producer['librarySha256']
    assert identity['installedPrefixFilesSha256']['lib/qml/Avelino/libAvelino.so']==module
    assert record('source34/controller/validation/package-producer.json')['librarySha256']==module
    assert record('source34/controller/validation/consumer/result.json')['exitCode']==99
    for number in [35,36]:assert record(f'source{number}/controller/validation/consumer/result.json')['exitCode']==0
    consumer=record('source36/controller/validation/consumer/result.json');assert consumer['moduleHashes']['libAvelino.so']==module
    phases=consumer['availableReport']['phases'];assert len(phases)==report['consumerSearchPhases']==9
    indexed={phase['phase']:phase for phase in phases}
    assert [phase['phase'] for phase in phases][3:6]==['token-replacement','token-undo','token-redo']
    assert indexed['token-replacement']['mode']==indexed['token-redo']['mode']=='general'
    assert indexed['token-replacement']['query']==indexed['token-redo']['query']=='avelinoulnacerulean-name'
    assert indexed['token-undo']['query']=='avelinoulnacerulean' and indexed['token-undo']['mode']=='filename'
    assert all(not phase['busy'] and not phase['error'] for phase in phases)
    assert indexed['owner-result']['state']['visibleAtCallback'] is True
    assert indexed['owner-result']['state']['results']==indexed['cancelled-query']['state']['results']
    portable=record('portable5/controller/result.json');runtime=record('portable5/controller/inputs.json')
    assert portable['exitCode']==0 and portable['runtimeFilesUnchanged'] is True and portable['displayProfiles']==8
    assert portable['moduleSha256']==module and portable['consumerSha256']==consumer['consumerSha256']
    for key in ['libraryProjectMounted','consumerProjectMounted','productBuildMounted']:assert portable[key] is runtime[key] is False
    assert {n for n in runtime['runtimeFiles'] if not n.startswith('install/')}=={'consumer-build/InstalledConsumer','run-file-search.py','check-display-sessions-file-search.sh','environment.json'}
    profiles=[name for name in records if name.startswith('portable5/output/display/') and name.endswith(('-standard.json','-scaled.json'))]
    assert len(profiles)==8
    for name in profiles:
        value=record(name);assert value['structuralChecks']=='passed' and value['accepted'] is False
        assert len(value['phases'])==report['portableSessionPhases']==10
        assert all(not phase['busy'] and not phase['error'] for phase in value['phases'])
        display=value['displaySession']
        for field in ['sessionCapture','finalWindowCapture']:assert digest(raw('portable5/output/display/'+display[field]))==display[field+'Sha256']
    assert record('portable4/controller/result.json')['exitCode']==1
    assert record('closed4/controller/result.json')['exitCode']==99
    comparison=record('closed5/controller/result.json');assert comparison['newModuleSha256']==module and comparison['consumerSha256']==consumer['consumerSha256']
    installed=read('installed-runtime-binding.json')
    assert installed['observedAfterAllRuntimeRuns'] is True and installed['currentModuleSha256']==module
    assert installed['oldModuleSha256']==comparison['oldModuleSha256'] and installed['currentConsumerSha256']==consumer['consumerSha256']
    assert installed['nativeVisualAccepted'] is installed['accepted'] is False
    for name,value in installed['candidateVisualInspection']['images'].items():assert digest(raw('portable5/output/'+name))==value
    assert comparison['byteIdentical']==comparison['frameAndStateIdentical']==report['closedImagePairs']==256
    for key in ['libraryProjectMounted','consumerProjectMounted','productBuildMounted']:assert comparison[key] is False
    for row in comparison['closedComparisons']:
        prefix='closed5/output/'+row['context']+'/'
        assert raw(prefix+'old-'+row['id']+'.png')==raw(prefix+'new-'+row['id']+'.png')
        assert row['byteIdentical'] is row['frameAndStateIdentical'] is True
    for context in {row['context'] for row in comparison['closedComparisons']}:
        prefix='closed5/output/'+context+'/';assert record(prefix+'old.json')['closed']==record(prefix+'new.json')['closed']
    for number in [9,10]:
        prefix=f'reader{number}/';run=record(prefix+'controller/result.json');inputs=record(prefix+'controller/inputs.json')
        assert run['exitCode']==0 and run['installedModuleUnchanged'] is run['probeSourcesUnchanged'] is True
        assert inputs['moduleSha256']==module and inputs['sourceProjectsMounted'] is False
        operator=record(prefix+'output/operator-report.json');assert operator['status']=='passed' and len(operator['phases'])==17
        for key in ['accepted','physicalInput','readerNativeComparisonAccepted','speechEngineAudioAccepted']:assert operator[key] is False
        phases={phase['phase']:phase for phase in operator['phases']}
        assert phases['token-replacement']['observations']['tokenVisible'] is phases['token-redo']['observations']['tokenVisible'] is False
        assert phases['token-undo']['observations']['tokenLabel']=='Everything: avelinoulnacerulean'
        assert phases['token-replacement']['observations']['text']==phases['token-redo']['observations']['text']=='avelinoulnacerulean-name'
        speech=raw(prefix+'output/orca-debug.log')
        for name,target in [('focused-result-speech','pine-only.txt'),('keyboard-result-speech','avelinoulnacerulean-name.txt')]:
            phase=phases[name];window=speech[phase['observations']['speechOffset']:phase['readerLogBytes']]
            for marker in [b'SPEECH OUTPUT:',b'SPEECH DISPATCHER: Speaking']:assert any(marker in line and target.encode() in line for line in window.splitlines())
    invariance=record('inventory-invariance.json');assert invariance['base']==report['sourceParent']
    baseline=json.loads(subprocess.check_output(['git','show',invariance['base']+':docs/parity-inventory.json'],cwd=ROOT))
    before=protected_fields(baseline);after=protected_fields(record('candidate/docs/parity-inventory.json'))
    assert len(before)==invariance['existingProtectedFields'] and all(name in after and after[name]==value for name,value in before.items())
    binding=record('candidate-input-binding.json');assert binding['producerInputSha256']==digest(raw('source36/controller/inputs.json'))
    assert binding['allSelectedCompiledInputsMatch'] is True and set(binding['postExecutionDocumentationDifferences'])=={'docs/file-input-search.md','docs/parity-inventory.json'}
    for name,pair in binding['postExecutionDocumentationDifferences'].items():assert pair['producer']==sources[36]['sourceFiles'][name] and pair['current']==digest(raw('candidate/'+name))
    current=read('current-candidate.json')
    assert current['sourceAttempt']==current['runtimeSourceAttempt']==37 and current['selectedSourceFiles']==len(sources[37]['sourceFiles'])==4116
    for key in ['accepted','nativeReaderComparisonAccepted','speechEngineAudioAccepted','physicalInputAccepted','physicalDisplayAccepted','independentMachineAccepted','expectedImagesChanged','referenceChanged','tolerancesChanged']:assert current[key] is False
    assert b'State editState()const;' in raw('source37/overrides/src/Avelino/filechoosersearchtext.h')
    assert b'State state()const;' not in raw('source37/overrides/src/Avelino/filechoosersearchtext.h')
    assert record('source37/controller/validation/focused/result.json')['exitCode']==0
    assert b'100% tests passed, 0 tests failed out of 9' in raw('source37/controller/validation/focused/run.log')
    current_producer=record('source37/controller/validation/package-producer.json');current_module=current_producer['librarySha256']
    current_consumer=record('source37/controller/validation/consumer/result.json')
    assert current_consumer['exitCode']==0 and current_consumer['moduleHashes']['libAvelino.so']==current_module
    assert len(current_consumer['availableReport']['phases'])==9
    current_portable=record('portable6/controller/result.json');current_runtime=record('portable6/controller/inputs.json')
    assert current_portable['exitCode']==0 and current_portable['runtimeFilesUnchanged'] is True and current_portable['displayProfiles']==8
    assert current_portable['moduleSha256']==current_module and current_portable['consumerSha256']==current_consumer['consumerSha256']
    for key in ['libraryProjectMounted','consumerProjectMounted','productBuildMounted']:assert current_portable[key] is current_runtime[key] is False
    current_profiles=[name for name in records if name.startswith('portable6/output/display/') and name.endswith(('-standard.json','-scaled.json'))]
    assert len(current_profiles)==8
    for name in current_profiles:
        value=record(name);assert value['structuralChecks']=='passed' and value['accepted'] is False and len(value['phases'])==10
        assert all(not phase['busy'] and not phase['error'] for phase in value['phases'])
        for field in ['sessionCapture','finalWindowCapture']:assert digest(raw('portable6/output/display/'+value['displaySession'][field]))==value['displaySession'][field+'Sha256']
    for number in [11,12]:
        prefix=f'reader{number}/';result=record(prefix+'controller/result.json');inputs=record(prefix+'controller/inputs.json')
        assert result['exitCode']==0 and result['installedModuleUnchanged'] is result['probeSourcesUnchanged'] is True and inputs['moduleSha256']==current_module
        operator=record(prefix+'output/operator-report.json');assert operator['status']=='passed' and len(operator['phases'])==17
        for key in ['accepted','physicalInput','readerNativeComparisonAccepted','speechEngineAudioAccepted']:assert operator[key] is False
        phases={phase['phase']:phase for phase in operator['phases']}
        assert phases['token-replacement']['observations']['tokenVisible'] is phases['token-redo']['observations']['tokenVisible'] is False
        assert phases['token-undo']['observations']['tokenLabel']=='Everything: avelinoulnacerulean'
        speech=raw(prefix+'output/orca-debug.log')
        for name,target in [('focused-result-speech','pine-only.txt'),('keyboard-result-speech','avelinoulnacerulean-name.txt')]:
            phase=phases[name];window=speech[phase['observations']['speechOffset']:phase['readerLogBytes']]
            for marker in [b'SPEECH OUTPUT:',b'SPEECH DISPATCHER: Speaking']:assert any(marker in line and target.encode() in line for line in window.splitlines())
    current_comparison=record('closed6/controller/result.json')
    assert current_comparison['newModuleSha256']==current_module and current_comparison['consumerSha256']==current_consumer['consumerSha256']
    assert current_comparison['byteIdentical']==current_comparison['frameAndStateIdentical']==256
    for key in ['libraryProjectMounted','consumerProjectMounted','productBuildMounted']:assert current_comparison[key] is False
    for row in current_comparison['closedComparisons']:
        prefix='closed6/output/'+row['context']+'/'
        assert raw(prefix+'old-'+row['id']+'.png')==raw(prefix+'new-'+row['id']+'.png')
        assert record(prefix+'old.json')['closed']==record(prefix+'new.json')['closed']
    final_inventory=record('current-candidate/docs/parity-inventory.json');final_fields=protected_fields(final_inventory)
    assert all(name in final_fields and final_fields[name]==value for name,value in before.items())
    final_binding=record('current-candidate-input-binding.json')
    assert final_binding['producerInputSha256']==digest(raw('source37/controller/inputs.json')) and final_binding['allSelectedCompiledInputsMatch'] is True
    assert set(final_binding['postExecutionDocumentationDifferences'])=={'docs/file-input-search.md','docs/parity-inventory.json','scripts/verify-file-input-search-token-editing.py'}
    for name,pair in final_binding['postExecutionDocumentationDifferences'].items():assert pair['producer']==sources[37]['sourceFiles'][name] and pair['current']==digest(raw('current-candidate/'+name))
    print('Token replacement and Qt undo: exact captured source, nine focused groups, current installed consumer, eight portable profiles, seventeen-phase readers and256 closed pairs verified; native parity remains pending')


if __name__=='__main__':verify()
