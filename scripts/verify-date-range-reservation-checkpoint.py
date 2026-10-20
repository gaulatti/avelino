#!/usr/bin/env python3
"""Verify reserved date widths without granting mirror acceptance."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/date-range-reservation-20261018'


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
    for name in ['qt/date-range-qt-v23', 'package', 'display', 'catalog']:
        assert read(name + '/result.json')['exitCode'] == 0
        assert all(row['exitCode'] == 0 for row in read(name + '/commands.json'))
    specification=read('source-specs.json')
    assert specification['coreFiles']==read('qt/date-range-qt-v23/inputs.json')['files']
    assert specification['consumerFiles']==read('package/inputs.json')['consumerFiles']
    for name,checksum in specification['integrationFiles'].items():
        assert digest(CAPSULE/'implementation-inputs'/name)==checksum
    assert digest(ROOT/'evidence/reference-investigations/date-range-width-20261018/chrome/output/bounds.json')==specification['nativeChromeSourceSha256']
    native=ROOT/'evidence/reference-investigations/date-range-reservation-20261018'
    assert digest(native/'files.json')==specification['nativeReservationManifestSha256']
    assert digest(native/'validation/output/validation.json')==specification['nativeReservationValidationSha256']
    assert '100% tests passed, 0 tests failed out of 3' in (CAPSULE/'qt/date-range-qt-v23/date-tests.log').read_text()
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
    before = json.loads((ROOT / 'evidence/development/date-range-chrome-correction-20261018/strict/comparison.json').read_text())['results']
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
    failure=read('qt/date-range-qt-v21/result.json')
    assert failure['exitCode']==8 and failure['failedStep']=='date-tests'
    assert 'FAIL!' in (CAPSULE/'qt/date-range-qt-v21/date-tests.log').read_text()
    report=read('package/output/light-text1-dpr1.json')
    closed={row['configuration']['id']:row for row in report['closed']}
    assert closed['locale-ja-jp']['actual']['editorText'][0]=='2024/ 3/ 9'
    assert closed['calendar-japanese']['actual']['editorText'][0]=='R   6/03/09'
    catalog=read('catalog/output/result.json')
    assert catalog['installedCatalogStartup']=='passed' and len(catalog['captures'])==4
    for capture in catalog['captures']:
        assert digest(CAPSULE/'catalog/output'/capture['path'])==capture['sha256']
    inputs=read('package/inputs.json')
    assert inputs['freshConsumerBuild'] is False and inputs['consumerSourcesUnchanged'] and inputs['publicPackageContractsUnchanged']
    assert inputs['consumerBuildProducer']=='date-range-package-v5'
    original=json.loads((ROOT/'evidence/development/date-range-editor-presentation-20261018/package/inputs.json').read_text())
    assert inputs['consumerFiles']==original['consumerFiles'] and inputs['consumerSha256']==original['consumerSha256']
    assert all(inputs['packageFiles'][name]==checksum for name,checksum in original['packageFiles'].items()if name.endswith(('.cmake','.qmltypes'))or name.endswith('/qmldir'))
    tests=(CAPSULE/'qt/date-range-qt-v23/ctest-last-test.log').read_text()
    assert 'DateRangeToolsTests::nativeChromeProfiles()' in tests and tests.count('DateRangeUiTests::nativeChromeProfilesReachOwnedEditors()')==2
    assert 'FAIL!' not in tests
    assert tests.count('DateRangeUiTests::widthsStayFixedAcrossNativeDates()')==2
    assert 'DateRangeToolsTests::widthsStayFixedAcrossNativeDates()' in tests
    assert 'DateRangeToolsTests::reservedWidthsUseNativeFontSamples()' in tests
    assert result['nativeDateUpdates']==1848 and result['qtWidthEndpointChecksPerDpr']==3696
    assert result['qtColdWidthEndpointChecksPerDpr']==92 and result['qtNativeFontSampleEndpointChecks']==118
    assert result['nativeProfileEndpointObservations']==72
    assert result['qtProfileDprRuns']==2 and result['freshConsumerBuild'] is False
    print(f"DateRangePicker widths: 1848 native updates, 3696 retained and 92 fresh endpoint checks per DPR, 118 native font-sample checks; 8 package/gallery, 8 virtual displays, 4 catalog captures; all 401 exact raster comparisons fail ({delta['lower']} lower, {delta['higher']} higher, {delta['identical']} identical changed-pixel counts); acceptance pending")


if __name__ == '__main__':
    verify()
