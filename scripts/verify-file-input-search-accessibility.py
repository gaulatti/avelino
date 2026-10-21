#!/usr/bin/env python3
"""Audit captured Linux search accessibility evidence without granting parity."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/development/file-input-search-accessibility-20261021'


def verify():
    read=lambda name:json.loads((DIRECTORY/name).read_text())
    digest=lambda raw:hashlib.sha256(raw).hexdigest()
    files=read('files.json')
    assert set(files)=={str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*') if p.is_file() and p.name!='files.json'}
    for name,row in files.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        raw=(DIRECTORY/name).read_bytes()
        assert len(raw)==row['bytes'] and digest(raw)==row['sha256'],name
    records=read('records.json');used=set()
    def raw(name):
        row=records[name];stored=row['stored'];used.add(stored)
        assert stored in files and not Path(stored).is_absolute() and '..' not in Path(stored).parts
        payload=(DIRECTORY/stored).read_bytes()
        value=gzip.decompress(payload) if stored.endswith('.gz') else payload
        assert len(value)==row['bytes'] and digest(value)==row['sha256'],name
        assert Path(stored).stem==row['sha256']
        return value
    def record(name):return json.loads(raw(name))
    for name in records:raw(name)
    assert used=={n for n in files if n.startswith(('images/','blobs/'))}
    report=read('validation.json')
    for key in ['accepted','nativeReaderComparisonAccepted','speechEngineAudioAccepted','physicalInput','physicalDisplay','independentMachineAccepted','expectedImagesChanged','referenceChanged','tolerancesChanged']:
        assert report[key] is False,key
    assert report['desktopCandidateCoverage']==[78,80] and report['acceptedDesktopEntries']==0
    assert report['architecture']=='arm64' and report['qt']=='6.8.3'
    source=record('producer/inputs.json');overrides=read('source-overrides.json')
    assert source['parent']==overrides['baseSourceRevision']==report['sourceParent']
    assert source['sourceUncommittedAtExecution'] is True
    assert len(source['sourceFiles'])==overrides['selectedFiles']==report['sourceFiles']==4046
    restored=read('source-reconstruction.json');assert restored['exitCode']==0 and restored['sourceFiles']==4046
    assert restored['allBytesMatchProducer'] is True and restored['accepted'] is False
    staged=read('staged-input-binding.json')
    assert staged['frozenProducerInputSha256']==digest(raw('producer/inputs.json'))
    assert staged['stagedFilesMatching']==4042 and staged['allCompiledModuleFixtureAndConsumerInputsMatch'] is True
    assert set(staged['stagedDifferences'])=={'docs/admin-shell.md','docs/file-input-search.md','docs/parity-inventory.json','scripts/verify-admin-clipping.py'}
    names=list(source['sourceFiles'])
    batch=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=('\n'.join(source['parent']+':'+n for n in names)+'\n').encode())
    stream=io.BytesIO(batch)
    for name in names:
        header=stream.readline().split()
        if len(header)==3:
            assert header[1]==b'blob';original=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        else:
            assert header[-1]==b'missing';original=None
        value=raw('source-overrides/'+name) if name in overrides['overrides'] else original
        assert value is not None and digest(value)==source['sourceFiles'][name],name
    assert not stream.read()
    assert set(overrides['overrides'])=={n.removeprefix('source-overrides/') for n in records if n.startswith('source-overrides/')}
    producer=record('validation/package-producer.json');module=producer['librarySha256']
    for name in ['producer/result.json','validation/result.json','validation/ctest/result.json','validation/consumer/result.json','validation/sessions/result.json']:
        result=record(name);assert result['exitCode']==0 and result['accepted'] is False,name
    tests=raw('validation/ctest/full-remaining-tests.log')
    assert b'100% tests passed, 0 tests failed out of 57' in tests
    assert b'100% tests passed, 0 tests failed out of 1' in raw('producer/search-dpr1.log')
    assert report['fullCtestGroups']==58
    for key in ['sourceInputsUnchanged','installedModuleUnchanged','runtimeCorpusUnchanged']:
        assert record('validation/ctest/result.json')[key] is True
    consumer=record('validation/consumer/result.json')
    assert consumer['moduleHashes']['libAvelino.so']==module
    assert consumer['sourceProjectsMounted'] is consumer['productBuildMounted'] is False
    assert consumer['installedConsumerSourcesUnchanged'] is True
    phases=consumer['availableReport']['phases'];assert len(phases)==6
    owner=next(p for p in phases if p['phase']=='owner-result')['state']
    cancelled=next(p for p in phases if p['phase']=='cancelled-query')['state']
    assert owner['visibleAtCallback'] is True and len(owner['results'])==1
    assert owner['results']==cancelled['results']
    assert owner['results'][0]['urls'][0].endswith('/inside/pine-only.txt')
    assert consumer['unavailableReport']['providerUnavailable'] is True
    sessions=record('validation/sessions/result.json');assert len(sessions['reports'])==report['searchDisplayProfiles']==8
    assert sessions['sourceProjectsMounted'] is sessions['productBuildMounted'] is False
    comparison=record('closed-comparison-controller/result.json')
    assert comparison['newModuleSha256']==module and comparison['consumerSha256']==consumer['consumerSha256']
    assert comparison['byteIdentical']==comparison['frameAndStateIdentical']==256
    assert len(comparison['closedComparisons'])==256
    for context in {row['context'] for row in comparison['closedComparisons']}:
        prefix='closed-comparison-output/'+context+'/'
        assert record(prefix+'old.json')['closed']==record(prefix+'new.json')['closed']
    for row in comparison['closedComparisons']:
        prefix='closed-comparison-output/'+row['context']+'/'
        assert raw(prefix+'old-'+row['id']+'.png')==raw(prefix+'new-'+row['id']+'.png')
        assert row['byteIdentical'] is row['frameAndStateIdentical'] is True
    portable=record('portable-controller/result.json');portable_inputs=record('portable-controller/inputs.json')
    assert portable['exitCode']==0 and portable['runtimeFilesUnchanged'] is True
    assert portable['displayProfiles']==8 and portable['moduleSha256']==module
    assert portable['consumerSha256']==consumer['consumerSha256']
    for key in ['libraryProjectMounted','consumerProjectMounted','productBuildMounted']:
        assert portable[key] is portable_inputs[key] is False
    runtime=portable_inputs['runtimeFiles']
    assert {name for name in runtime if not name.startswith('install/')}=={'consumer-build/InstalledConsumer','run-file-search.py','check-display-sessions-file-search.sh','environment.json'}
    assert runtime['consumer-build/InstalledConsumer']==consumer['consumerSha256']
    assert record('portable-output/available.json')['structuralChecks']=='passed'
    assert record('portable-output/unavailable.json')['providerUnavailable'] is True
    profiles=[n for n in records if n.startswith('portable-output/display/') and n.endswith(('-standard.json','-scaled.json'))]
    assert len(profiles)==8
    for name in profiles:
        profile=record(name);assert profile['structuralChecks']=='passed' and profile['accepted'] is False
        display=profile['displaySession']
        assert digest(raw('portable-output/display/'+display['sessionCapture']))==display['sessionCaptureSha256']
        assert digest(raw('portable-output/display/'+display['finalWindowCapture']))==display['finalWindowCaptureSha256']
    for profile in report['readerProfiles']:
        number=profile['attempt'];prefix=f'readers/v{number}/'
        run=record(f'reader-controllers/v{number}/result.json')
        assert run['exitCode']==0 and run['installedModuleUnchanged'] is run['probeSourcesUnchanged'] is True
        assert record(f'reader-controllers/v{number}/inputs.json')['moduleSha256']==module
        operator=record(prefix+'operator-report.json')
        assert operator['status']=='passed' and len(operator['phases'])==profile['phases']==12
        for key in ['accepted','physicalInput','readerNativeComparisonAccepted','speechEngineAudioAccepted']:assert operator[key] is False
        phases={p['phase']:p for p in operator['phases']}
        assert phases['offscreen-selection']['observations']['selected']==['zz-avelinoulnacerulean-row-47.txt']
        assert phases['multiple-selection']['observations']['selected']==['avelinoulnacerulean-name.txt','pine-only.txt']
        events=[json.loads(line) for line in raw(prefix+'events.jsonl').splitlines()]
        assert any(event['event']=='object:selection-changed' and event['name']=='Search results'
            and phases['focused-result-speech']['time']<=event['time']<=phases['keyboard-result-speech']['time'] for event in events)
        speech=raw(prefix+'orca-debug.log')
        for name,target in [('focused-result-speech','pine-only.txt'),('keyboard-result-speech','avelinoulnacerulean-name.txt')]:
            phase=phases[name];observation=phase['observations'];assert observation['selected']==[target]
            window=speech[observation['speechOffset']:phase['readerLogBytes']]
            for marker in [b'SPEECH OUTPUT:',b'SPEECH DISPATCHER: Speaking']:
                assert any(marker in line and target.encode() in line for line in window.splitlines()),(number,name,marker)
        assert phases['owner-result']['observations']['owner'].endswith('/inside/pine-only.txt')
        assert phases['owner-result']['observations']['owner']==phases['cancel-preserves-owner']['observations']['owner']
        for name in ['editable-text-query','editable-text-undo-redo']:assert phases[name]['observations']['text']=='avelinoulnacerulean'
    for number in [1,2]:assert record(f'reader-controllers/v{number}/result.json')['exitCode']==1
    assert b'no QAccessibleSelectionInterface' in raw('previous-source-16/search-dpr1.log') or b'Search results must expose' in raw('previous-source-16/search-dpr1.log')
    assert report['invalidManualLoaderDeletionAttempt']==22
    print('Indexed search: exact captured source, 58 Qt groups, installed consumer, eight virtual profiles, 256 unchanged closed images and two actual AT-SPI/Orca profiles verified; native parity remains pending')


if __name__=='__main__':verify()
