#!/usr/bin/env python3
"""Check native reserved-width evidence without accepting Linux date layout."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'evidence/reference-investigations/date-range-width-20261018'
ANALYSIS = ROOT / 'evidence/development/date-range-width-analysis-20261018'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def manifest(directory):
    files=read(directory/'files.json')
    assert set(files)=={str(p.relative_to(directory))for p in directory.rglob('*')if p.is_file()and p!=directory/'files.json'}
    for name,row in files.items():
        path=directory/name
        assert path.stat().st_size==row['bytes'] and digest(path)==row['sha256'],name


def verify():
    for directory in [NATIVE,ANALYSIS]:manifest(directory)
    result=read(NATIVE/'result.json')
    assert result['accepted'] is False and result['callerUpdates']==1848 and result['pickerDateObservations']==3696
    data=read(NATIVE/'output/widths.json')
    assert data['accepted'] is False and data['reference']=='fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert len(data['baseline'])==48 and len(data['contexts'])==23
    for row in data['baseline']:
        name=row['configuration']['id']
        original=ROOT/'evidence/reference-investigations/date-range-20261018/output'/f'{name}-light-text1.0-dpr1.0-mode0.png'
        assert row['getterCaptureStable']
        assert (NATIVE/'output'/f'{name}.png').read_bytes()==(NATIVE/'output'/f'{name}-after.png').read_bytes()==original.read_bytes()
    count=0
    for context in data['contexts']:
        name=context['configuration']['id'];sizes=set()
        assert context['restoredImageEqual']
        assert (NATIVE/'output'/f'{name}-initial.png').read_bytes()==(NATIVE/'output'/f'{name}-restored.png').read_bytes()
        for index,update in enumerate(context['updates']):
            assert update['index']==index and len(update['editors'])==2
            model=update['model']
            assert model['start']==model['end']==update['requestedDate']
            assert model['requests']==[] and model['pending']=={}
            assert model['appearances']==model['wrapperInstances']==1 and model['disappearances']==0
            for editor in update['editors']:
                assert editor['date']==update['requestedDate']
                sizes.add(tuple(editor['intrinsic'][key]for key in ['width','height']))
            count+=1
        assert len(sizes)==1
        for cold in context['coldExtremes']:
            for editor in cold['editors']:
                assert editor['date']==cold['requestedDate']
                assert tuple(editor['intrinsic'][key]for key in ['width','height']) in sizes
            label=cold['label']
            assert (NATIVE/'output'/f'{name}-{label}-retained.png').read_bytes()==(NATIVE/'output'/f'{name}-{label}-cold.png').read_bytes()
        # The raw helper calls this getter after restoring the original dates.
        assert [editor['date']for editor in context['initialEditors']]==[context['configuration'][key]for key in ['start','end']]
    assert count==1848
    bounds=read(NATIVE/'field-bounds/output/bounds.json')
    assert bounds['accepted'] is False and len(bounds['rows'])==23
    for row in bounds['rows']:
        name=row['configuration']['id'];assert row['getterImagesEqual']
        assert (NATIVE/'field-bounds/output'/f'{name}.png').read_bytes()==(NATIVE/'field-bounds/output'/f'{name}-after.png').read_bytes()==(NATIVE/'output'/f'{name}-initial.png').read_bytes()
        for editor in row['editors']:
            accessibility=editor['accessibility'];assert accessibility['nodes']==5
            roles=[]
            def visit(node):
                roles.append(node['role'])
                for child in node.get('children',[]):visit(child)
            visit(accessibility['tree'])
            assert Counter(roles)==Counter(AXUnknown=1,AXDateTimeArea=1,AXIncrementor=1,AXButton=2)
    replay=read(NATIVE/'source-only-replay/result.json')
    assert replay==dict(accepted=False,exitCode=0,extractedWithoutPrebuiltProducts=True,exactReplayFiles=282,allOutputBytesEqual=True,independentMachine=False)
    archive=read(NATIVE/'source-only-replay/artifact.json')
    assert archive['files']==len(archive['sourceFiles'])==95 and archive['pinnedSourceFiles']==89 and archive['compiledOutputs'] is False
    checks=read(NATIVE/'source-only-replay/output-checks.json');assert len(checks)==282
    for name,row in checks.items():
        prefix,relative=name.split('/',1)
        path=NATIVE/('output'if prefix=='width-output'else'field-bounds/output')/relative
        assert prefix in ['width-output','bounds-output']
        assert path.stat().st_size==row['bytes'] and digest(path)==row['originalSha256']==row['replaySha256']
    assert all(step['exitCode']==0 for step in read(NATIVE/'source-only-replay/commands.json'))
    earlier=NATIVE/'attempts/source-only-width'
    assert read(earlier/'result.json')['exactReplayFiles']==235 and read(earlier/'result.json')['allOutputBytesEqual']
    assert read(earlier/'artifact.json')['files']==93
    assert all(step['exitCode']==0 for step in read(earlier/'commands.json'))
    earlier_checks=read(earlier/'output-checks.json');assert len(earlier_checks)==235
    for name,row in earlier_checks.items():assert digest(NATIVE/'output'/name)==row['originalSha256']==row['replaySha256']
    assert read(NATIVE/'attempts/width-v1/commands.json')[-1]['exitCode']==-6
    assert 'CoreGraphics.CGFloat' in (NATIVE/'attempts/width-v1/capture.log').read_text()
    original_fixtures=read(ROOT/'evidence/reference-investigations/date-range-20261018/fixtures.json')
    expected_fixtures=[]
    for name in ['default','calendar-hebrew','calendar-islamic']:
        source=next(row for row in original_fixtures if row['id']==name)
        for size in ['regular','small','mini','large']:
            for style in ['field','stepperField','compact']:
                expected_fixtures.append(dict(source,id=name+'-'+size+'-'+style,controlSize=size,pickerStyle=style))
    assert read(NATIVE/'chrome/fixtures.json')==expected_fixtures
    chrome=read(NATIVE/'chrome/output/bounds.json')['rows'];assert len(chrome)==36
    chrome_by_id={row['configuration']['id']:row for row in chrome}
    for row,fixture in zip(chrome,expected_fixtures,strict=True):
        assert row['configuration']=={key:value for key,value in fixture.items()if value is not None}
        name=fixture['id'];assert row['getterImagesEqual']
        assert (NATIVE/'chrome/output'/f'{name}.png').read_bytes()==(NATIVE/'chrome/output'/f'{name}-after.png').read_bytes()
        assert [editor['date']for editor in row['editors']]==[fixture['start'],fixture['end']]
    for name in ['default','calendar-hebrew','calendar-islamic']:
        for size,stepper,field_height,stepper_height in [('regular',17,21,20),('small',15,19,18),('mini',11,16,16),('large',20,21,24)]:
            for index in [0,1]:
                field=chrome_by_id[f'{name}-{size}-field']['editors'][index]['intrinsic']
                step=chrome_by_id[f'{name}-{size}-stepperField']['editors'][index]['intrinsic']
                compact=chrome_by_id[f'{name}-{size}-compact']['editors'][index]['intrinsic']
                assert compact==step and step['width']-field['width']==stepper
                assert field['height']==field_height and step['height']==stepper_height
        assert (NATIVE/'chrome/output'/f'{name}-regular-field.png').read_bytes()==(NATIVE/'chrome/output'/f'{name}-large-field.png').read_bytes()
    style_replay=NATIVE/'chrome/source-replay'
    assert read(style_replay/'result.json')['exactOutputFiles']==73 and read(style_replay/'result.json')['allOutputBytesEqual']
    assert read(style_replay/'result.json')['freshSourceArchive']==archive['sha256']
    assert read(style_replay/'result.json')['fixtureSha256']==digest(NATIVE/'chrome/fixtures.json')
    style_checks=read(style_replay/'output-checks.json');assert len(style_checks)==73
    for name,row in style_checks.items():assert digest(NATIVE/'chrome/output'/name)==row['originalSha256']==row['replaySha256']
    assert all(step['exitCode']==0 for step in read(style_replay/'commands.json'))
    assert result['sourceOnlyReplayFiles']==355 and result['styleContexts']==36
    assert read(NATIVE/'attempts/chrome-v1/commands.json')[-1]['exitCode']!=0
    qt=ANALYSIS/'qt-measure/v3'
    measured=read(qt/'output.json');inputs=read(qt/'input.json')
    assert len(measured)==len(inputs)==1848
    assert (qt/'output.json').read_bytes()==(qt/'output-repeat.json').read_bytes()
    assert read(qt/'measure-result.json')['exitCode']==0 and read(qt/'measure-result.json')['repeatedOutputExact']
    assert all(step['exitCode']==0 for step in read(qt/'commands.json')+read(qt/'measure-repeat-commands.json'))
    groups=defaultdict(list)
    for actual,input_row in zip(measured,inputs,strict=True):
        for key in ['id','index','date','shortDateString']:assert actual[key]==input_row[key]
        assert actual['editorWidth']==actual['fieldTextWidth']
        groups[actual['id']].append(actual)
    summary=[]
    for context in data['contexts']:
        name=context['configuration']['id'];rows=groups[name]
        assert len(rows)==len(context['updates'])
        assert [row['date']for row in rows]==[row['requestedDate']for row in context['updates']]
        sizes=context['updates'][0]['editors'][0]['intrinsic']
        advances=[row['editorWidth']for row in rows]
        summary.append(dict(id=name,nativeIntrinsic=sizes,measuredDates=len(rows),qtCurrentEditorTextAdvance=dict(minimum=min(advances),maximum=max(advances)),qtTextAdvanceVaries=min(advances)!=max(advances),measurementOnly=True))
    assert summary==read(ANALYSIS/'summary.json')
    assert sum(row['qtTextAdvanceVaries']for row in summary)==10
    assert read(ANALYSIS/'qt-measure/v1/smoke-result.json')['exitCode']==5
    assert read(ANALYSIS/'qt-measure/v2/smoke-result.json')['validationExitCode']==1
    assert (ANALYSIS/'qt-measure/v2/smoke-output.json').stat().st_size==0
    state=read(ANALYSIS/'result.json')
    assert state['accepted'] is False and state['productCodeChanged'] is False
    assert state['desktopCandidates']==76 and state['acceptedDesktopEntries']==0
    spec=read(ANALYSIS/'source-specs.json')
    previous=read(ROOT/'evidence/development/date-range-editor-presentation-20261018/source-specs.json')
    assert spec['coreFiles']==previous['coreFiles'] and spec['consumerFiles']==previous['consumerFiles']
    for name,checksum in spec['integrationFiles'].items():assert digest(ANALYSIS/'implementation-inputs'/name)==checksum
    print('Date widths: 1848 native updates, 23 constant intrinsic contexts, 46 exact cold/retained pairs, 36 style contexts and 355 exact fresh source-built outputs; 10 Qt label-advance contexts vary; Linux layout/font/reader acceptance remains pending')


if __name__=='__main__':verify()
