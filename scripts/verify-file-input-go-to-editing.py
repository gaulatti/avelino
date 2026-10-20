#!/usr/bin/env python3
"""Audit recorded path-editing evidence; native mirror acceptance stays pending."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'evidence/development/file-input-go-to-editing-20261018'


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
    assert report['desktopCandidateCoverage']==[75,80] and report['acceptedDesktopEntries']==0
    assert report['expectedImagesChanged'] is False and report['tolerance']=='none' and report['approvedExceptions']==[]
    assert report['focusedQtTargets']==8 and report['finalFullQtSuiteRerun'] is False
    assert all(report[k]=='pending' for k in ['nativeHierarchy','nativeReaderComparison','completeFileChooser','independentMachine'])
    files=read('files.json')
    assert set(files)=={str(p.relative_to(DIRECTORY))for p in DIRECTORY.rglob('*')if p.is_file()and p.name!='files.json'}
    for name,row in files.items():
        raw=(DIRECTORY/name).read_bytes()
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('avelino_path_editing_restore',DIRECTORY/'tools/reconstruct.py')
    loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(loader)
    sources=read('source-specs.json');assert set(sources)=={report['producer']}
    source=sources[report['producer']]['files'];runtime=read('runtime-spec.json');records=read('records-spec.json')
    used=set()
    def raw_record(row):
        raw=b''.join(loader.chunk_bytes(part)for part in row['chunks'])
        used.update(part['sha256']for part in row['chunks'])
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
        return raw
    for table in [source,runtime,records]:
        for row in table.values():raw_record(row)
    assert used=={p.stem for p in(DIRECTORY/'blobs').glob('*.gz')}
    assert len(source)==report['sourceFiles']
    inputs=json.loads(raw_record(records['producer/inputs.json']))
    assert inputs['files']=={name:row['sha256']for name,row in source.items()}
    assert {'src/Avelino/filechooserpathinput.h','src/Avelino/filechooserpathinput.cpp'}<=set(source)
    commands=json.loads(raw_record(records['producer/commands.json']))
    assert len(commands)==8 and all(row['exitCode']==0 for row in commands)
    verbose=raw_record(records['producer/ui-verbose.log']).decode()
    assert verbose.count('PASS   : FileInputUiTests::actualGoToAccessibleTextEditingUpdatesSuggestionsAndKeepsUndo()')==2
    package=json.loads(raw_record(records['package/result.json']))
    assert package['exitCode']==0 and package['contexts']==8 and package['freshConsumerBuild'] is True
    assert package['libraryAndConsumerProjectSourcesAbsentAtRuntime'] is True
    for name,row in read('closed-stability.json').items():
        current=(DIRECTORY/'captures'/name).read_bytes();prior=ROOT/row['prior'];capture=json.loads(current)
        assert capture['structuralChecks']=='passed' and capture['accepted'] is False
        assert len(capture['actions'])==30 and capture['images']==49
        assert capture['pointerEvents']==62 and capture['keyEvents']==164
        for section in ['closed','sizing']:assert metadata(current,section)==metadata(prior.read_bytes(),section)
        for image,digest in row['images'].items():
            raw=(DIRECTORY/'captures'/image).read_bytes()
            assert hashlib.sha256(raw).hexdigest()==digest and raw==(prior.parent/image).read_bytes()
    assert sum(len(row['images'])for row in read('closed-stability.json').values())==report['closedImagesUnchanged']==256
    profiles=list((DIRECTORY/'display/output').glob('file-input-*.json'))
    assert len(profiles)==report['displayProfiles']==8
    for path in profiles:
        value=json.loads(path.read_text());assert value['structuralChecks']=='passed' and value['accepted'] is False
    for number in range(1,11):
        prefix=f'readers/file-input-go-to-reader-v{number}/'
        session=json.loads(raw_record(records[prefix+'session-result.json']))
        assert session['waitCode']==0 and session['containerExit']=='0'
        exercise=json.loads(raw_record(records[prefix+'exercise-result.json']))
        result=read(prefix+'operator-controls-v1/result.json')
        if number<=2:
            assert exercise['code']==1 and result['status']=='failed'
        elif number<=4:
            assert exercise['code']==0 and result['directAssistiveTextEdit']=='unsupported'
        elif number<=8:
            assert exercise['code']==1 and result['status']=='failed'
            assert 'go-to-editable-text-insert-delete' in {p['phase']for p in result['phases']}
        else:
            assert exercise['code']==0 and result['status']=='passed' and result['directAssistiveTextEdit']=='passed'
            phases={p['phase']:p for p in result['phases']}
            assert {'go-to-editable-text-prefix','go-to-editable-text-insert-delete','go-to-editable-text-native-undo-redo',
                    'go-to-editable-text-navigates-without-owner','go-to-editable-text-unicode-proposal',
                    'go-to-editable-text-missing-stays-modal','go-to-final-cancel-restores-caller'}<=set(phases)
            assert phases['go-to-editable-text-prefix']['observations']['interfaceResult'] is True
            log=raw_record(records[prefix+'orca-debug.log']).decode()
            assert 'SPEECH OUTPUT:'in log and 'SPEECH DISPATCHER: Speaking'in log and 'Go to Folder'in log
            receipt=json.loads(raw_record(records[prefix+'validation.json']))
            assert receipt['directAssistiveTextEdit']=='passed' and receipt['nativeReaderComparison']=='pending'
    portable=read('portable/result.json');assert portable['exitCode']==0 and portable['libraryAndConsumerSourcesAbsentAtRuntime'] is True
    current=(DIRECTORY/'portable/light-text1-dpr1.json').read_bytes();original=(DIRECTORY/'captures/light-text1-dpr1.json').read_bytes()
    for section in ['closed','sizing']:assert metadata(current,section)==metadata(original,section)
    for row in json.loads(current)['closed']:
        name='light-text1-dpr1-'+row['configuration']['id']+'.png'
        assert (DIRECTORY/'portable'/name).read_bytes()==(DIRECTORY/'captures'/name).read_bytes()
    print('Owned GoTo editing: Qt regression, installed consumers, X11/Wayland AT-SPI edits and exact portable replay verified; native parity gates pending')


if __name__=='__main__':verify()
