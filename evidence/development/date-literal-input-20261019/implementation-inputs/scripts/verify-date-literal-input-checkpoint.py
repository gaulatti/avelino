#!/usr/bin/env python3
"""Verify retained-field input evidence without granting native parity acceptance."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/date-literal-input-20261019'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    def read(name):
        return json.loads((CAPSULE / name).read_text())

    manifest = read('files.json')
    assert set(manifest) == {
        str(p.relative_to(CAPSULE)) for p in CAPSULE.rglob('*')
        if p.is_file() and p != CAPSULE / 'files.json'
    }
    for name, row in manifest.items():
        path = CAPSULE / name
        assert path.stat().st_size == row['bytes'] and digest(path) == row['sha256'], name

    result = read('result.json')
    assert result['accepted'] is False and result['acceptedDesktopEntries'] == 0
    assert result['desktopCandidates'] == 76 and not result['referencePinsChanged']
    assert result['approvedExceptions'] == []
    assert not result['initialFieldSelectionAccepted'] and not result['rtlGlyphClippingResolved']
    assert result['nativeObservations'] == 15 and result['nativeRetainedSelectionHistories'] == 4
    assert result['compiledCoreInputs'] == 607 and result['freshConsumerInputs'] == 150
    assert result['qtLiteralRows'] == 32 and result['dateCTestGroups'] == 3
    assert not result['all55QtTestsRerun'] and not result['all792PythonTestsRerun']
    assert result['consumerSmokeInvocations'] == 41 and result['navigationProfiles'] == 8
    assert result['datePackageProfiles'] == result['dateGalleryProfiles'] == 8
    assert result['dateDisplayProfiles'] == 5 and result['dateDisplayAttemptedProfiles'] == 6
    assert result['dateDisplayFailedProfiles'] == 1 and result['dateDisplayUnrunProfiles'] == 2
    assert not result['completeDateDisplayGatePassed']
    assert result['datePackageLiteralChecks'] == 128 and result['dateDisplayLiteralChecks'] == 80
    assert result['datePackageNativeValueComparisons'] == 64 and result['dateDisplayNativeValueComparisons'] == 40
    assert result['rawDateCandidatesIdentical'] == result['strictDateRasterComparisons'] == 437
    assert result['strictDateRasterMatches'] == 0

    spec = read('source-specs.json')
    assert not spec['accepted'] and spec['baseGit'] == '97fe54cbed3d53ac7125ab8141f831f40dd7ac2d'
    parents = {
        'nativeInputManifestSha256': 'evidence/reference-investigations/date-range-literal-input-20261018',
        'nativeStabilityManifestSha256': 'evidence/reference-investigations/date-range-selected-field-stability-20261019',
        'priorTypographyManifestSha256': 'evidence/development/navigation-cjk-metrics-20261018',
        'parentDateManifestSha256': 'evidence/development/date-range-fields-20261018',
        'historicalDisplayManifestSha256': 'evidence/development/weston-display-20261018',
    }
    for key, name in parents.items():
        assert digest(ROOT / name / 'files.json') == spec[key]
    for name, checksum in spec['changedFiles'].items():
        assert digest(CAPSULE / 'implementation-inputs' / name) == checksum
    previous = json.loads((ROOT / parents['priorTypographyManifestSha256'] / 'source-specs.json').read_text())
    core = spec['coreFiles']
    assert core == read('qt/inputs.json')['files'] and len(core) == 607
    for name, checksum in core.items():
        assert checksum == previous['coreFiles'].get(name) or spec['changedFiles'].get(name) == checksum, name
    assert len(spec['consumerFiles']) == 150
    assert spec['consumerFiles'] == read('package/inputs.json')['consumerFiles']
    assert all(core['tests/consumer/' + name] == checksum for name, checksum in spec['consumerFiles'].items())
    date_driver = json.loads((ROOT / parents['parentDateManifestSha256'] / 'display/inputs.json').read_text())['scriptSha256']
    for name, checksum in spec['runtimeScripts'].items():
        assert checksum == (date_driver if name == 'scripts/check-display-sessions-date-range.sh' else previous['liveScripts'][name])
    assert digest(CAPSULE / 'display/check.sh') == spec['runtimeScripts']['scripts/check-display-sessions-date-range.sh']

    for name in ['qt', 'package', 'date-replay', 'source-checks']:
        assert read(name + '/result.json')['exitCode'] == 0
        assert all(row['exitCode'] == 0 for row in read(name + '/commands.json'))
    extra = read('additional-contract-attempt/interruption.json')
    assert extra['intentionallyInterrupted'] and not extra['fullSuitePassed'] and extra['ciSuiteUnchanged']
    assert read('additional-contract-attempt/result.json')['exitCode'] == -2
    partial = (CAPSULE / 'additional-contract-attempt/contracts.log').read_text()
    assert 'KeyboardInterrupt' in partial and extra['completedPassingCases'] == partial.count(' ... ok')
    assert ' ... FAIL\n' not in partial and ' ... ERROR\n' not in partial
    assert 'python3 -m unittest discover -s tests/contracts -v' in (CAPSULE / 'implementation-inputs/.github/workflows/references.yml').read_text()
    qt = read('qt/result.json')
    assert qt['focusedLiteralRows'] == 32 and qt['dateCTestGroups'] == 3 and not qt['all55TestsRerun']
    for dpr in [1, 2]:
        log = (CAPSULE / f'qt/literal-dpr{dpr}.log').read_text()
        assert log.count('PASS   : qmltestrunner::DateLiteralHitContract::test_literal_does_not_activate_calendar(') == 16
        assert '0 failed' in log and 'FAIL!' not in log
        red = (CAPSULE / f'red/dpr{dpr}.log').read_text()
        assert red.count('FAIL!  : qmltestrunner::DateLiteralHitContract::test_literal_does_not_activate_calendar(') == 16
        assert read('red/result.json')['steps'][dpr - 1]['exitCode'] == 16
    assert digest(CAPSULE / 'qt/tst_date_literal_hits.qml') == digest(CAPSULE / 'red/tst_literal_hits.qml')
    assert digest(CAPSULE / 'qt/date_literal_cases.js') == digest(CAPSULE / 'red/date_literal_cases.js')
    assert '100% tests passed, 0 tests failed out of 3' in (CAPSULE / 'qt/date-tests.log').read_text()
    activation = read('qt/activated-inputs.json')
    assert activation['cacheBytesMatchSnapshot'] and activation['previousValidatedProducer'] == 'date-literal-qt-v1'
    assert set(activation['files']) == {'src/Avelino/daterangeinput.cpp', 'tests/consumer/daterangechecks.h'}
    assert all(core[name] == checksum for name, checksum in activation['files'].items())

    package = read('package/inputs.json')
    assert read('package/result.json')['freshConsumerBuild'] and package['freshConsumerBuild']
    assert read('package/result.json')['smokeInvocations'] == len(package['smokeArguments']) == 41
    assert [row['name'] for row in read('package/commands.json')[:3]] == ['source-absence', 'consumer-configure', 'consumer-build']
    replay = read('date-replay/inputs.json')
    for key in ['packageFiles', 'consumerFiles', 'consumerSha256', 'imageId']:
        assert replay[key] == package[key]
    assert replay['consumerCompilationProducer'] == spec['producers']['package']
    assert not replay['freshConsumerBuild']
    assert read('package/result.json')['libraryAndConsumerProjectSourcesAbsentAtRuntime']
    assert read('date-replay/result.json')['libraryAndConsumerProjectSourcesAbsentAtRuntime']
    assert read('display/result.json')['exitCode'] == 1
    assert len(read('display/commands.json')) == 1 and read('display/commands.json')[0]['exitCode'] == 1
    assert read('display/inputs.json')['consumerSha256'] == package['consumerSha256']
    assert read('display/inputs.json')['imageId'] == package['imageId'] == read('qt/inputs.json')['imageId']
    identity = read('runtime-identity.json')
    assert set(identity) == {'qt', 'package', 'date-replay', 'display'}
    for name, actual in identity.items():
        assert actual['packageFiles'] == package['packageFiles'] and len(actual['packageFiles']) == 151
        if name != 'qt':
            assert actual['consumerSha256'] == package['consumerSha256']

    witnesses = read('implementation-inputs/tests/consumer/native-date-literal-input-witnesses.json')
    profiles = {row['nativeCase']: row for row in witnesses['profiles']}
    assert set(profiles) == {'hebrew-day', 'hebrew-month', 'english-month', 'arabic-year'}

    def literal_checks(report):
        rows = report['literalInput']
        assert len(rows) == 16
        assert {(row['sourceCase'], row['callerRtl'], row['endpoint']) for row in rows} == {
            (case, rtl, endpoint) for case in profiles for rtl in [False, True] for endpoint in ['start', 'end']
        }
        for row in rows:
            before = row['before']
            assert row['samePixels'] and before == row['after']
            assert before['activeFocus'] and not before['calendarVisible']
            assert before['selectionStart'] != before['selectionEnd']
            model = row['afterUp']['model']
            request, = model['requests']
            assert request['endpoint'] == row['endpoint'] and request['requested'] == model[row['endpoint']]
            assert row['nativeValueCompared'] == (row['endpoint'] == 'start')
            if row['nativeValueCompared']:
                assert model['start'] == profiles[row['sourceCase']]['nativeStartAfterUp']
                assert model['end'] == request['previousEnd']
            else:
                assert model['start'] == request['previousStart']
                assert model['end'] != request['previousEnd']
        return len(rows), sum(row['nativeValueCompared'] for row in rows)

    total = native = 0
    for appearance in ['light', 'dark']:
        for scale in ['1', '1.5']:
            for dpr in [1, 2]:
                name = f'{appearance}-text{scale}-dpr{dpr}'
                report = read(f'date-replay/output/{name}.json')
                assert not report['accepted'] and report['structuralChecks'] == 'passed'
                assert report['modelMatches'] == len(report['closed']) == 48 and len(report['input']) == 3
                assert len(report['chinese']) == 36
                assert report['chineseModelMatches'] == report['chineseTextMatches'] == report['chineseCalendarMatches'] == 36
                n, m = literal_checks(report); total += n; native += m
                assert len(read(f'date-replay/output/gallery-{name}.json')['gallery']) == 21
    assert (total, native) == (128, 64)
    validation = read('date-replay/literal-validation.json')
    assert validation['checks'] == 128 and validation['nativeValueComparisons'] == 64
    for row in validation['profiles']:
        assert digest(CAPSULE / 'date-replay/output' / row['path']) == row['sha256']

    total = native = 0
    expected = {'xcb-software-standard', 'xcb-software-scaled', 'xcb-opengl-standard', 'xcb-opengl-scaled', 'wayland-software-standard'}
    reports = {path.stem: json.loads(path.read_text()) for path in (CAPSULE / 'display/output').glob('*.json')
               if 'displaySession' in json.loads(path.read_text())}
    assert set(reports) == expected
    for name, report in reports.items():
        protocol, backend, configuration = name.split('-')
        assert report['platform'] == protocol and report['graphicsApi'] == (1 if backend == 'software' else 3)
        assert report['structuralChecks'] == 'passed' and not report['accepted']
        n, m = literal_checks(report); total += n; native += m
        session = report['displaySession']
        assert not session['physicalDisplay'] and not session['hardwareAcceleration'] and not session['physicalInput']
        for key in ['sessionCapture', 'finalWindowCapture']:
            path = CAPSULE / 'display/output' / session[key]
            assert digest(path) == session[key + 'Sha256']
        with Image.open(CAPSULE / 'display/output' / session['sessionCapture']) as image:
            assert list(image.size) == session['sessionOutputSize'] == [2560, 1920]
    assert (total, native) == (80, 40)
    failure = read('display/output/wayland-software-scaled-failed.json')
    assert failure['sameState'] and failure['sameModel'] and not failure['samePixels']
    assert failure['sourceCase'] == 'arabic-year' and failure['endpoint'] == 'end' and not failure['callerRtl']
    with Image.open(CAPSULE / 'display/output/wayland-software-scaled-failed-before.png') as image:
        before = image.convert('RGBA')
    with Image.open(CAPSULE / 'display/output/wayland-software-scaled-failed-after.png') as image:
        after = image.convert('RGBA')
    delta = ImageChops.difference(before, after); rgb = delta.convert('RGB')
    assert rgb.getbbox() == delta.getchannel('A').getbbox() == (765, 384, 766, 418)
    channels = rgb.split(); maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    assert maximum.width * maximum.height - maximum.histogram()[0] == 12
    assert before.getchannel('A').histogram()[0] == 12 and after.getchannel('A').histogram()[0] == 0
    analysis = read('display/failure-analysis.json')
    assert analysis['changedPixels'] == 12 and not analysis['causeProven']
    assert analysis['completeProfiles'] == 5 and analysis['failedProfiles'] == 1 and analysis['unrunProfiles'] == 2
    for name in ['wayland-software-scaled', 'wayland-opengl-standard', 'wayland-opengl-scaled']:
        assert not (CAPSULE / 'display/output' / (name + '.json')).exists()

    parent = ROOT / parents['parentDateManifestSha256']
    comparisons = json.loads((parent / 'strict/comparison.json').read_text())['results']
    chinese = json.loads((parent / 'chinese-comparison.json').read_text())['results']
    assert len(comparisons) == 401 and len(chinese) == 36
    for row in comparisons + chinese:
        name = row.get('candidateName', row.get('fixture'))
        assert digest(CAPSULE / 'date-replay/output' / name) == row['candidateSHA256']
        assert row['status'] == 'failed'
    raw = read('date-replay/raw-image-comparison.json')
    assert raw['count'] == raw['identical'] == 437 and raw['differences'] == []
    assert raw['parentManifestSHA256'] == spec['parentDateManifestSha256']

    assert read('failed-display/result.json')['exitCode'] == 1
    assert read('diagnostic/result.json')['exitCode'] == 1 and read('fixed-diagnostic/result.json')['exitCode'] == 0
    assert digest(CAPSULE / 'interim-qt/failed-daterangeinput.cpp') == read('interim-qt/inputs.json')['files']['src/Avelino/daterangeinput.cpp']
    assert digest(CAPSULE / 'interim-package/failed-daterangechecks.h') == read('interim-package/inputs.json')['consumerFiles']['daterangechecks.h']
    failure = read('diagnostic/output/xcb-opengl-scaled-failed.json')
    assert failure['sameState'] and failure['sameModel'] and not failure['samePixels']
    with Image.open(CAPSULE / 'diagnostic/output/xcb-opengl-scaled-failed-before.png') as image:
        before = image.convert('RGBA')
    with Image.open(CAPSULE / 'diagnostic/output/xcb-opengl-scaled-failed-after.png') as image:
        after = image.convert('RGBA')
    delta = ImageChops.difference(before, after)
    assert delta.getchannel('A').getbbox() is None
    rgb = delta.convert('RGB')
    assert rgb.getbbox() == (555, 385, 557, 417)
    channels = rgb.split()
    maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    assert maximum.width * maximum.height - maximum.histogram()[0] == 64
    fixed = read('fixed-diagnostic/inputs.json')
    assert fixed['sameDiagnosticElf'] and fixed['newModuleProducer'] == spec['producers']['qt']
    assert fixed['consumerSha256'] == read('diagnostic/artifacts.json')['consumerSha256']
    assert literal_checks(read('fixed-diagnostic/output/xcb-opengl-scaled.json')) == (16, 8)
    review = read('visual-review.json')
    assert not review['accepted'] and digest(CAPSULE / review['capture']) == review['sha256']
    print('Date literal checkpoint:32 pointer cases,3 date CTests,150-input independent consumer,8 date/gallery profiles,5 passing display profiles; scaled Wayland12-pixel alpha failure retained and2 profiles unrun;437 unchanged candidates; acceptance pending')


if __name__ == '__main__':
    verify()
