#!/usr/bin/env python3
"""Audit controlled native menu observations and scoped Linux evidence."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'evidence/reference-investigations/file-input-search-owner-menu-20261021'
DIRECTORY=ROOT/'evidence/development/file-input-search-menu-20261021'
PIN='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
digest=lambda raw:hashlib.sha256(raw).hexdigest()


def inventory(directory):
    files=json.loads((directory/'files.json').read_text())
    assert set(files)=={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name!='files.json'}
    for name,row in files.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        raw=(directory/name).read_bytes()
        assert len(raw)==row['bytes'] and digest(raw)==row['sha256'],name
    return files


def native_menu_choices(text):
    lines=text.splitlines()
    start=next(i for i,line in enumerate(lines) if re.search(r'menu button (Filename|Everything): avelinoulnacerulean$',line))
    menu=lines[start+1];level=len(menu)-len(menu.lstrip('\t'))
    assert 'menu Secondary Actions: Cancel' in menu
    result=[]
    for line in lines[start+2:]:
        depth=len(line)-len(line.lstrip('\t'))
        if depth<=level:break
        if depth==level+1:result.append(re.sub(r'^\d+ ','',line.strip()))
    return result


def protected_inventory_fields(value,path=''):
    result={}
    if isinstance(value,dict):
        for key,item in value.items():
            if key=='status' or any(s in key.lower() for s in ['accept','capture','reference','toleran','exception','mask','comparison']):
                result[path+'/'+key]=item
            else:result.update(protected_inventory_fields(item,path+'/'+key))
    elif isinstance(value,list):
        for index,item in enumerate(value):result.update(protected_inventory_fields(item,path+'/'+str(index)))
    return result


def verify_native():
    inventory(NATIVE)
    read=lambda name:json.loads((NATIVE/name).read_text())
    observation=read('observations.json')
    assert observation['reference']==PIN and observation['tokenMenuChoices']==['Filename','Everything']
    for key in ['independentNativeLibraryRebuild','readerNativeComparisonAccepted','physicalInputAccepted','rasterAccepted','accepted']:
        assert observation[key] is False,key
    platform=read('runtime-platform-v2.json')
    assert '27.0.1' in platform['sw_vers'] and '26A434' in platform['sw_vers']
    assert platform['sdkVersion']=='27.0' and platform['minimumCompilationTarget']=='arm64-apple-macosx26.0'
    assert platform['independentNativeLibraryRebuild'] is platform['accepted'] is False
    bindings={row['kind']:row for row in read('runtime-bindings.json')}
    library='61d1e55c6f9c17c841eded420066c72b5611ec51af8c5a4821306f1751ea6514'
    for host,count in [('appkit',2),('swiftui',3)]:
        build=read(host+'/build.json');trace=read(host+'/output/ui-trace.json')
        assert build['reference']==trace['reference']==PIN and build['exitCode']==0
        assert build['libraryObjectSha256']==bindings[host]['libraryObjectSha256']==library
        assert build['libraryUnchanged'] is True
        assert build['independentNativeLibraryRebuild'] is build['injectedCompletion'] is build['accepted'] is trace['accepted'] is False
        assert bindings[host]['sourceLibraryChanged'] is bindings[host]['independentNativeLibraryRebuild'] is bindings[host]['accepted'] is False
        assert digest((NATIVE/host/'fixture.json').read_bytes())==build['helperInputHashes']['fixture.json']
        callbacks=[step for step in trace['steps'] if step['phase']=='owner-result']
        assert len(callbacks)==count==observation['nativeSuccessfulCallbacks'][host]
        final=callbacks[-1];assert len(final['results'])==count
        for ordinal,result in enumerate(final['results']):
            assert result['ordinal']==ordinal and result['kind']=='success' and result['panelVisibleAtCallback'] is True
            assert len(result['urls'])==1 and result['urls'][0].startswith('file:///Users/gaulatti/Documents/Codex/2026-10-20/avelino-file-search-fixtures/')
        assert final['results'][0]['urls'][0].endswith('/avelino-search-body-20261020.txt')
        assert final['results'][1]['urls'][0].endswith('/pine-only.txt')
        if host=='swiftui':
            assert final['mounted'] is False and observation['nativeOwnerUnmountOnLastSwiftuiResult'] is True
            assert final['results'][2]['urls'][0].endswith('/avelinoulnacerulean-name.txt')
            # The retained diagnostic precedes the successful retry in the raw trace.
            requests=[s for s in trace['steps'] if s['phase']=='owner-command']
            assert len(requests)==2 and len(requests[0]['results'])==1
    assert len(read('fixture-files.json'))==8
    for number in range(1,5):
        query=read(f'controlled-cua/query-0{number}.json')
        assert query['completeImageBytesArchived'] is False and 'actionArguments' not in query
        for item in query['imageMetadata']:assert item['mimeType']=='image/jpeg' and item['elidedInSessionLog'] is True
        if number>=2:assert native_menu_choices(query['text'])==['Filename','Everything']
    late=read('controlled-cua/query-03.json')['text']
    assert '/file-search-compiled-v24/source/' in late and 'Value: 1' in late


def verify():
    verify_native();files=inventory(DIRECTORY)
    read=lambda name:json.loads((DIRECTORY/name).read_text())
    records=read('records.json');used=set()
    def raw(name):
        row=records[name];stored=row['stored'];used.add(stored)
        assert stored in files and not Path(stored).is_absolute() and '..' not in Path(stored).parts
        payload=(DIRECTORY/stored).read_bytes();value=gzip.decompress(payload) if stored.endswith('.gz') else payload
        assert len(value)==row['bytes'] and digest(value)==row['sha256'] and Path(stored).stem==row['sha256'],name
        return value
    def record(name):return json.loads(raw(name))
    for name in records:raw(name)
    assert used=={name for name in files if name.startswith(('images/','blobs/'))}
    report=read('validation.json')
    for key in ['accepted','nativeReaderComparisonAccepted','speechEngineAudioAccepted','physicalInputAccepted','physicalDisplayAccepted','independentMachineAccepted','expectedImagesChanged','referenceChanged','tolerancesChanged']:
        assert report[key] is False,key
    assert report['sourceAttempt']==27 and report['runtimeExecutedOnSourceAttempt']==26
    assert report['focusedQtGroups']==9 and report['historicalFullSuite']['sourceAttempt']==24
    historical=json.loads((ROOT/report['historicalFullSuite']['capsule']/'validation.json').read_text())
    assert historical['fullCtestGroups']==report['historicalFullSuite']['groups']==58
    overrides=read('source-overrides.json');sources={}
    for number in [25,26,27]:
        prefix=f'source{number}/';source=record(prefix+'controller/inputs.json');sources[number]=source
        assert source['parent']==overrides[str(number)]['parent']==report['sourceParent']
        assert source['sourceUncommittedAtExecution'] is True
        assert len(source['sourceFiles'])==overrides[str(number)]['files']==report['selectedSourceFiles']==4108
        names=list(source['sourceFiles'])
        batch=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=('\n'.join(source['parent']+':'+n for n in names)+'\n').encode())
        stream=io.BytesIO(batch)
        for name in names:
            header=stream.readline().split()
            if len(header)==3:
                assert header[1]==b'blob';value=stream.read(int(header[2]));assert stream.read(1)==b'\n'
            else:assert header[-1]==b'missing';value=None
            if name in overrides[str(number)]['overrides']:value=raw(prefix+'overrides/'+name)
            assert value is not None and digest(value)==source['sourceFiles'][name],(number,name)
        assert not stream.read()
    differences={n for n in sources[26]['sourceFiles'] if sources[26]['sourceFiles'][n]!=sources[27]['sourceFiles'][n]}
    assert differences=={'tests/components/filesearch.cpp'}
    binding=record('candidate-input-binding.json')
    assert binding['producerInputSha256']==digest(raw('source27/controller/inputs.json'))
    assert binding['compiledControlAndTestBytesMatch'] is True and binding['matchingSelectedSourceFiles']==4106
    assert set(binding['postExecutionDocumentationDifferences'])=={'docs/file-input-search.md','docs/parity-inventory.json'}
    for name,pair in binding['postExecutionDocumentationDifferences'].items():
        assert pair['producer']==sources[27]['sourceFiles'][name] and digest(raw('candidate/'+name))==pair['current']
    invariance=record('inventory-invariance.json')
    assert invariance['base']==report['sourceParent'] and invariance['allExistingFieldsUnchanged'] is True
    baseline=json.loads(subprocess.check_output(['git','show',invariance['base']+':docs/parity-inventory.json'],cwd=ROOT))
    previous=protected_inventory_fields(baseline);current=protected_inventory_fields(record('candidate/docs/parity-inventory.json'))
    assert len(previous)==invariance['existingProtectedFields'] and all(key in current and current[key]==value for key,value in previous.items())
    assert record('source25/controller/result.json')['exitCode']==8
    assert b'The native token menu offers only Filename and Everything' in raw('source25/controller/search-dpr1.log')
    assert record('source26/controller/validation/focused/result.json')['exitCode']==8
    assert b'accessibleResultSelectionAndOffscreenRows' in raw('source26/controller/validation/focused/run.log')
    for name in ['result.json','validation/result.json','validation/focused/result.json']:
        value=record('source27/controller/'+name);assert value['exitCode']==0 and value['sourceUnchanged'] is True and value['accepted'] is False
    assert b'100% tests passed, 0 tests failed out of 9' in raw('source27/controller/validation/focused/run.log')
    identity=record('source27/controller/validation/runtime-identity-v26-v27.json')
    assert identity['sourceAttempts']==[26,27] and identity['installedPrefixFiles']==158
    assert len(identity['installedPrefixFilesSha256'])==158
    assert identity['allInstalledPrefixBytesIdentical'] is True and identity['installedPrefixDifferences']=={}
    assert identity['newExecutionClaimed'] is identity['accepted'] is False
    assert set(identity['sourceDifferences'])==differences
    producer=record('source26/controller/validation/package-producer.json');module=producer['librarySha256']
    assert identity['installedPrefixFilesSha256']['lib/qml/Avelino/libAvelino.so']==module
    assert record('source27/controller/validation/package-producer.json')['librarySha256']==module
    consumer=record('source26/controller/validation/consumer/result.json')
    assert consumer['exitCode']==0 and consumer['moduleHashes']['libAvelino.so']==module
    portable=record('portable-controller/result.json');inputs=record('portable-controller/inputs.json')
    assert portable['exitCode']==0 and portable['runtimeFilesUnchanged'] is True
    assert portable['displayProfiles']==report['portableProfiles']==8 and portable['moduleSha256']==module
    assert portable['consumerSha256']==consumer['consumerSha256']
    for key in ['libraryProjectMounted','consumerProjectMounted','productBuildMounted']:assert portable[key] is inputs[key] is False
    assert {n for n in inputs['runtimeFiles'] if not n.startswith('install/')}=={'consumer-build/InstalledConsumer','run-file-search.py','check-display-sessions-file-search.sh','environment.json'}
    assert record('portable-output/available.json')['structuralChecks']=='passed'
    assert record('portable-output/unavailable.json')['providerUnavailable'] is True
    profiles=[n for n in records if n.startswith('portable-output/display/') and n.endswith(('-standard.json','-scaled.json'))]
    assert len(profiles)==8
    for name in profiles:
        value=record(name);display=value['displaySession'];assert value['structuralChecks']=='passed' and value['accepted'] is False
        for field in ['sessionCapture','finalWindowCapture']:assert digest(raw('portable-output/display/'+display[field]))==display[field+'Sha256']
    preflight=record('portable-preflight-failure/result.json');assert preflight['exitCode']==1 and preflight['clientProcessesStarted'] is False
    for number in [7,8]:
        prefix=f'reader{number}/';run=record(prefix+'controller/result.json')
        assert run['exitCode']==0 and run['installedModuleUnchanged'] is run['probeSourcesUnchanged'] is True
        assert record(prefix+'controller/inputs.json')['moduleSha256']==module
        operator=record(prefix+'output/operator-report.json')
        assert operator['status']=='passed' and len(operator['phases'])==report['readerPhasesEach']==14
        for key in ['accepted','physicalInput','readerNativeComparisonAccepted','speechEngineAudioAccepted']:assert operator[key] is False
        phases={p['phase']:p for p in operator['phases']}
        for name in ['filename-token-menu','everything-token-menu']:
            assert phases[name]['observations']['choices']==['Filename','Everything']
            assert record(prefix+'output/'+name+'.json')['observations']['choices']==['Filename','Everything']
        speech=raw(prefix+'output/orca-debug.log')
        for name,target in [('focused-result-speech','pine-only.txt'),('keyboard-result-speech','avelinoulnacerulean-name.txt')]:
            phase=phases[name];window=speech[phase['observations']['speechOffset']:phase['readerLogBytes']]
            for marker in [b'SPEECH OUTPUT:',b'SPEECH DISPATCHER: Speaking']:
                assert any(marker in line and target.encode() in line for line in window.splitlines())
    comparison=record('closed-controller/result.json')
    assert comparison['newModuleSha256']==module and comparison['byteIdentical']==comparison['frameAndStateIdentical']==256
    assert len(comparison['closedComparisons'])==report['closedImagePairs']==256
    for row in comparison['closedComparisons']:
        prefix='closed-output/'+row['context']+'/'
        assert raw(prefix+'old-'+row['id']+'.png')==raw(prefix+'new-'+row['id']+'.png')
        assert row['byteIdentical'] is row['frameAndStateIdentical'] is True
    for context in {r['context'] for r in comparison['closedComparisons']}:
        prefix='closed-output/'+context+'/';assert record(prefix+'old.json')['closed']==record(prefix+'new.json')['closed']
    print('Controlled native token choices and owner deliveries, nine focused Qt groups, identical26/27 runtime, eight portable profiles, fourteen-phase readers and256 closed pairs audited; native acceptance remains pending')


if __name__=='__main__':verify()
