#!/usr/bin/env python3
"""Verify independently clipped date fields without granting mirror acceptance."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/date-range-fields-20261018'


def verify():
    read = lambda name: json.loads((CAPSULE / name).read_text())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = read('files.json')
    assert set(manifest) == {str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*') if p.is_file() and p != CAPSULE / 'files.json'}
    for name, row in manifest.items():
        path = CAPSULE / name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name
    result = read('result.json')
    assert result['accepted'] is False and result['desktopCandidates'] == 76 and result['acceptedDesktopEntries'] == 0
    assert result['historySteps'] == 17 and result['historyModelMatches'] == result['historyEditorInstanceMatches'] == result['historyCalendarMatches'] == result['historyEnvironmentMatches'] == 17
    assert result['historyGeometryMatches'] == result['strictRasterMatches'] == 0 and result['strictRasterComparisons'] == 401
    for name in ['qt/date-range-qt-v35', 'package', 'display', 'catalog']:
        assert read(name + '/result.json')['exitCode'] == 0
        assert all(row['exitCode'] == 0 for row in read(name + '/commands.json'))
    specification=read('source-specs.json')
    assert specification['coreFiles']==read('qt/date-range-qt-v35/inputs.json')['files']
    activation=read('qt/date-range-qt-v34/activated-inputs.json')
    assert activation['cacheBytesMatchSnapshot'] and activation['previousValidatedProducer']=='date-range-qt-v32'
    assert set(activation['files'])=={'src/Avelino/DateRangeField.qml','src/Avelino/daterangeinput.cpp','tests/components/daterangeui.cpp'}
    assert all(specification['coreFiles'][name]==checksum for name,checksum in activation['files'].items())
    final_activation=read('qt/date-range-qt-v35/activated-inputs.json')
    assert final_activation['previousValidatedProducer']=='date-range-qt-v34' and final_activation['cacheBytesMatchSnapshot']
    assert set(final_activation['files'])=={'tests/consumer/DateRangePicker.qml','tests/consumer/daterangechecks.h'}
    assert all(specification['coreFiles'][name]==checksum for name,checksum in final_activation['files'].items())
    assert read('qt/date-range-qt-v33/invalidated.json')['compiledInputAttestation'] is False
    api=read('api-review/review.json')
    assert api['qt']=='6.8.3' and api['installedHeadersEqualReviewedReleaseSources'] and len(api['installedHeaders'])==4
    assert all(api['sourceFiles'][name]['sha256']==checksum for name,checksum in api['installedHeaders'].items())
    assert specification['consumerFiles']==read('package/inputs.json')['consumerFiles']
    for name,checksum in specification['integrationFiles'].items():
        assert digest(CAPSULE/'implementation-inputs'/name)==checksum
    assert digest(ROOT/'evidence/reference-investigations/date-range-width-20261018/chrome/output/bounds.json')==specification['nativeChromeSourceSha256']
    native=ROOT/'evidence/reference-investigations/date-range-reservation-20261018'
    assert digest(native/'files.json')==specification['nativeReservationManifestSha256']
    assert digest(native/'validation/output/validation.json')==specification['nativeReservationValidationSha256']
    assert '100% tests passed, 0 tests failed out of 3' in (CAPSULE/'qt/date-range-qt-v35/date-tests.log').read_text()
    history = json.loads((ROOT / 'evidence/development/date-range-history-20261018/implementation-inputs/tests/consumer/native-date-range-witnesses.json').read_text())['history']
    source = ROOT / history['source']
    assert digest(source) == history['sourceSha256']
    provenance = json.loads((ROOT / 'evidence/reference-investigations/date-range-20261018/provenance/helper-files.json').read_text())
    assert history['actionSource'] == provenance['history-v1']['tool/DateHistory.swift']
    expected_steps = [row['step'] for row in history['steps']]

    def history_matches(report, supported):
        rows = report['histories']
        assert [row['step'] for row in rows] == (expected_steps if supported else [])
        for row, native in zip(rows, history['steps'], strict=supported):
            assert row['native'] == native and row['action'] == native['action']
            actual = row['actual']
            assert actual['model'] == native['model'] and actual['displayed'] == native['displayed']
            assert row['actualEditorInstances'] == row['nativeEditorInstances'] == [item['instance'] for item in native['nativeInstances']]
            assert row['actualDark'] == row['nativeDark'] == native['dark']
            assert row['modelMatches'] and row['editorInstancesMatch'] and row['calendarMatches'] and row['environmentMatches']
            frames = dict(actual['frames']); frames.pop('arrow')
            assert row['geometryMatches'] == (frames == native['frames'])
            for actual_parts, source_instance in zip(actual['calendarParts'], native['nativeInstances'], strict=True):
                calendar = source_instance['calendar']
                for key in ['firstWeekday', 'minimumDaysInFirstWeek']:
                    assert actual_parts[key] == calendar[key]
                assert all(actual_parts[key] == value for key, value in calendar['components'].items())
            configuration = native['configuration']
            for key, source_key in [('style', 'pickerStyle'), ('controlSize', 'controlSize'), ('locale', 'locale'), ('calendar', 'calendar'), ('timeZone', 'timeZone'), ('mirrored', 'rtl')]:
                assert actual[key] == configuration[source_key]
            assert actual['enabled'] == (not configuration['disabled'])
        for key in ['historyModelMatches', 'historyEditorInstanceMatches', 'historyCalendarMatches', 'historyEnvironmentMatches']:
            assert report[key] == (17 if supported else 0)
        assert report['historyGeometryMatches'] == 0

    model_matches=geometry_matches=0
    for appearance in ['light', 'dark']:
        for scale in ['1', '1.5']:
            for dpr in [1, 2]:
                report = read(f'package/output/{appearance}-text{scale}-dpr{dpr}.json')
                assert len(report['closed']) == report['modelMatches'] == 48 and len(report['input']) == 3
                model_matches+=report['modelMatches'];geometry_matches+=report['geometryMatches']
                history_matches(report, appearance == 'light' and scale == '1' and dpr == 1)
    assert result['closedModelMatches']==model_matches==384
    assert result['closedGeometryMatches']==geometry_matches
    for protocol in ['xcb', 'wayland']:
        for backend in ['software', 'opengl']:
            for configuration in ['standard', 'scaled']:
                report = read(f'display/output/{protocol}-{backend}-{configuration}.json')
                assert report['accepted'] is False and report['platform'] == protocol
                assert report['graphicsApi'] == (1 if backend == 'software' else 3)
                assert len(report['closed']) == report['modelMatches'] == 48
                history_matches(report, configuration == 'standard')
                session = report['displaySession']
                assert not session['physicalDisplay'] and not session['hardwareAcceleration'] and not session['physicalInput']
                assert digest(CAPSULE / 'display/output' / session['sessionCapture']) == session['sessionCaptureSha256']
    comparisons = read('strict/comparison.json')['results']
    assert len(read('strict/commands.json'))==1 and read('strict/commands.json')[0]['exitCode']==1
    assert len(comparisons) == 401 and sum('-history-' in row['fixture'] for row in comparisons) == 17
    witness = read('package/output/light-text1-dpr1.json')
    paths = {f'light-text1-dpr1-history-{row["step"]}.png': ('history-output', row['native']['referenceCapture']) for row in witness['histories']}
    for appearance in ['light', 'dark']:
        for scale in ['1', '1.5']:
            for dpr in [1, 2]:
                prefix = f'{appearance}-text{scale}-dpr{dpr}'
                for row in read(f'package/output/{prefix}.json')['closed']:
                    paths[prefix + '-' + row['configuration']['id'] + '.png'] = ('output', row['native']['referenceCapture'])
    for row in comparisons:
        directory, name = paths[row['fixture']]
        reference = ROOT / 'evidence/reference-investigations/date-range-20261018' / directory / name
        candidate = CAPSULE / 'package/output' / row['fixture']
        assert digest(reference) == row['referenceSHA256'] and digest(candidate) == row['candidateSHA256']
        assert row['status'] == 'failed' and 'error' not in row
        with Image.open(reference) as image: expected = image.copy()
        with Image.open(candidate) as image: actual = image.copy()
        assert expected.size == actual.size
        delta = ImageChops.difference(expected.convert('RGB'), actual.convert('RGB'))
        alpha = ImageChops.difference(expected.convert('RGBA').getchannel('A'), actual.convert('RGBA').getchannel('A'))
        assert delta.getbbox() is not None or alpha.getbbox() is not None
        red, green, blue = delta.split()
        maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
        assert row['changedPixels'] == delta.width * delta.height - maximum.histogram()[0]
        assert row['maximumChannelError'] == maximum.getextrema()[1]
        bounds=delta.getbbox();alpha_bounds=alpha.getbbox()
        assert row['differenceBounds'] == (list(bounds) if bounds else None)
        assert row['alphaDifferenceBounds'] == (list(alpha_bounds) if alpha_bounds else None)
    before = json.loads((ROOT / 'evidence/development/date-range-chinese-20261018/strict/comparison.json').read_text())['results']
    previous = {row['fixture']: row for row in before}
    changes = []
    for row in comparisons:
        prior = previous[row['fixture']]
        assert row['referenceSHA256'] == prior['referenceSHA256']
        changes.append(dict(fixture=row['fixture'],before=prior['changedPixels'],after=row['changedPixels'],change=row['changedPixels']-prior['changedPixels']))
    delta=read('raster-delta.json')
    assert delta['rows']==changes
    assert delta['lower']==sum(row['change']<0 for row in changes)
    assert delta['higher']==sum(row['change']>0 for row in changes)
    assert delta['identical']==sum(row['change']==0 for row in changes)
    assert delta['accepted'] is False and delta['comparisonOnly'] is True
    for producer in ['date-range-qt-v29','date-range-qt-v31']:
        failure=read('qt/'+producer+'/result.json')
        assert failure['exitCode']==1 and failure['failedStep']=='date-tests'
        assert 'FAIL!' in (CAPSULE/'qt'/producer/'date-tests.log').read_text()
    assert 'Actual   (rectangle(0).x())' in (CAPSULE/'qt/date-range-qt-v29/date-tests.log').read_text()
    assert 'selectedSegment' in (CAPSULE/'qt/date-range-qt-v31/date-tests.log').read_text()
    report=read('package/output/light-text1-dpr1.json')
    closed={row['configuration']['id']:row for row in report['closed']}
    assert closed['locale-ja-jp']['actual']['editorText'][0]=='2024/ 3/ 9'
    assert closed['calendar-japanese']['actual']['editorText'][0]=='R   6/03/09'
    catalog=read('catalog/output/result.json')
    assert catalog['installedCatalogStartup']=='passed' and len(catalog['captures'])==4
    for capture in catalog['captures']:
        assert digest(CAPSULE/'catalog/output'/capture['path'])==capture['sha256']
    inputs=read('package/inputs.json')
    assert inputs['freshConsumerBuild'] is True and specification['freshConsumerBuild'] is True
    assert specification['consumerCompilationProducer']=='date-range-package-v11'
    commands=read('package/commands.json')
    assert [r['name']for r in commands[:3]]==['source-absence','consumer-configure','consumer-build']
    assert all(r['exitCode']==0 for r in commands)
    assert len(inputs['consumerFiles'])==149
    native=ROOT/'evidence/reference-investigations/date-range-chinese-20261018'
    assert digest(native/'files.json')==specification['nativeChineseManifestSha256']
    assert digest(ROOT/'tests/consumer/native-date-chinese-witnesses.json')==specification['nativeChineseWitnessesSha256']
    total=0
    for appearance in ['light','dark']:
        for scale in ['1','1.5']:
            for dpr in [1,2]:
                report=read(f'package/output/{appearance}-text{scale}-dpr{dpr}.json');rows=report['chinese'];assert len(rows)==36
                assert report['chineseModelMatches']==report['chineseTextMatches']==report['chineseCalendarMatches']==36
                for row in rows:
                    actual=row['actual'];expected=row['native']
                    assert actual['model']==expected['model'] and actual['displayed']==expected['displayed']
                    assert actual['editorText']==expected['editorText'] and actual['editorRoles']==expected['editableRoles']
                    assert row['modelMatches'] and row['textMatches'] and row['calendarMatches']
                    for parts,source in zip(actual['calendarParts'],expected['calendarParts'],strict=True):assert all(parts[k]==v for k,v in source.items())
                    total+=1
                gallery=read(f'package/output/gallery-{appearance}-text{scale}-dpr{dpr}.json')['gallery'];assert len(gallery)==21
                leap=next(row['actual']for row in gallery if row['operator']=='leap-month')
                cases=json.loads((ROOT/'tests/consumer/native-date-chinese-witnesses.json').read_text())['cases']
                source=next(row for row in cases if row['configuration']['id']=='chinese-zh-cn-leap-regular')
                assert leap['displayed']==source['displayed'] and leap['editorText']==source['editorText'] and leap['editorRoles']==source['editableRoles']
                for parts,expected in zip(leap['calendarParts'],source['calendarParts'],strict=True):assert all(parts[key]==value for key,value in expected.items())
                selected={r['operator']:r['actual'] for r in gallery if r['operator'].startswith('chinese-')}
                assert set(selected)=={'chinese-en_US','chinese-zh_CN','chinese-ko_KR'}
                for key,actual in selected.items():assert actual['calendar']=='chinese' and actual['locale']==key.removeprefix('chinese-') and actual['editorRoles']==[['month','day'],['month','day']]
    assert total==288
    for protocol in ['xcb','wayland']:
        for backend in ['software','opengl']:
            for configuration in ['standard','scaled']:
                report=read(f'display/output/{protocol}-{backend}-{configuration}.json');assert len(report['chinese'])==36
                assert report['chineseModelMatches']==report['chineseTextMatches']==report['chineseCalendarMatches']==36
    summary=read('chinese-result.json');assert summary['packageModelMatches']==summary['packageTextMatches']==summary['packageCalendarMatches']==288 and summary['freshConsumerBuild'] is True
    assert summary['legacyCandidateImagesIdentical']==all(row['candidateSHA256']==previous[row['fixture']]['candidateSHA256'] for row in comparisons)
    comparison=read('chinese-comparison.json')['results'];assert len(comparison)==36 and summary['strictMatches']==sum(r['status']=='passed'for r in comparison)
    for row in comparison:
        reference=ROOT/row['referencePath'];candidate=CAPSULE/'package/output'/row['candidateName']
        assert digest(reference)==row['referenceSHA256'] and digest(candidate)==row['candidateSHA256']
        with Image.open(reference)as image:expected=image.convert('RGBA')
        with Image.open(candidate)as image:actual=image.convert('RGBA')
        assert expected.size==actual.size
        difference=ImageChops.difference(expected,actual);rgb=difference.convert('RGB');alpha=difference.getchannel('A')
        red,green,blue=rgb.split();maximum=ImageChops.lighter(ImageChops.lighter(red,green),blue)
        passed=rgb.getbbox()is None and alpha.getbbox()is None
        assert row['status']==('passed'if passed else'failed') and row['changedPixels']==rgb.width*rgb.height-maximum.histogram()[0]
    parent=ROOT/'evidence/development/date-range-chinese-20261018'
    assert digest(parent/'files.json')==specification['parentCheckpointManifestSha256']
    font=json.loads((parent/'font-toolchain/font-environment.json').read_text())
    assert inputs['imageId']==font['imageId'] and font['cjkFamilies'] and len(font['fontFiles'])==4
    assert digest(ROOT/'tools/Dockerfile')==font['rootDockerfileSha256']
    tests=(CAPSULE/'qt/date-range-qt-v35/ctest-last-test.log').read_text()
    assert 'DateRangeToolsTests::nativeChromeProfiles()' in tests and tests.count('DateRangeUiTests::nativeChromeProfilesReachOwnedEditors()')==2
    assert 'FAIL!' not in tests
    assert tests.count('DateRangeUiTests::widthsStayFixedAcrossNativeDates()')==2
    assert 'DateRangeToolsTests::widthsStayFixedAcrossNativeDates()' in tests
    assert 'DateRangeToolsTests::reservedWidthsUseNativeFontSamples()' in tests
    assert result['nativeDateUpdates']==1848 and result['qtWidthEndpointChecksPerDpr']==3696
    assert result['qtColdWidthEndpointChecksPerDpr']==92 and result['qtNativeFontSampleEndpointChecks']==118
    assert result['nativeProfileEndpointObservations']==72
    assert result['qtProfileDprRuns']==2 and result['freshConsumerBuild'] is True
    assert tests.count('DateRangeUiTests::chinesePresentationReachesOwnedEditors()')==2 and tests.count('DateRangeUiTests::chineseDayInputMethodCommit()')==2
    assert 'DateRangeToolsTests::chineseGlyphCoverage()' in tests
    assert 'DateRangeToolsTests::chineseEditorPresentationAndParsing()'in tests and 'DateRangeToolsTests::chineseWidthsUseNativeFontSamples()'in tests
    for name in ['leapMonthKeepsIndependentDayPosition','segmentedInputMethodAndAccessibility','fieldHitTestingAcrossLocaleDirections']:
        assert tests.count('PASS   : DateRangeUiTests::'+name+'()')==2
    assert tests.count('Calendar field endpoint clicks and QML hit tests: 400')==2
    assert specification['consumerCompilationProducer']=='date-range-package-v11'
    print(f"Date field checkpoint: segmented geometry, preedit and accessibility checks at both DPRs; fresh consumer149 with 21 gallery operators in 8 package and 8 display profiles; exact pixel passes {result['strictRasterMatches']}/401 and {summary['strictMatches']}/36; acceptance pending")



if __name__ == '__main__':
    verify()
