#!/usr/bin/env python3
"""Verify the CJK typography checkpoint without granting mirror acceptance."""
import hashlib
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAPSULE=ROOT/'evidence/development/navigation-cjk-metrics-20261018'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((CAPSULE/name).read_text())
def verify():
    manifest=read('files.json')
    assert set(manifest)=={str(p.relative_to(CAPSULE))for p in CAPSULE.rglob('*')if p.is_file()and p!=CAPSULE/'files.json'}
    for name,row in manifest.items():
        path=CAPSULE/name;assert path.stat().st_size==row['bytes']and digest(path)==row['sha256'],name
    result=read('result.json');assert result['accepted']is False and result['acceptedDesktopEntries']==0 and result['desktopCandidates']==76
    assert result['referencePinsChanged']is False and result['approvedExceptions']==[]
    spec=read('source-specs.json');assert spec['coreFiles']==read('qt/inputs.json')['files']
    assert spec['consumerFiles']==read('package/inputs.json')['consumerFiles']
    assert len(spec['coreFiles'])==604 and len(spec['consumerFiles'])==149
    for name,value in spec['consumerFiles'].items():assert spec['coreFiles']['tests/consumer/'+name]==value
    for name,value in spec['integrationFiles'].items():assert digest(CAPSULE/'implementation-inputs'/name)==value
    for name,value in spec['liveScripts'].items():assert digest(ROOT/name)==value
    activation=read('qt/activated-inputs.json')
    assert activation['previousValidatedProducer']=='navigation-cjk-qt-v4' and activation['cacheBytesMatchSnapshot']
    assert set(activation['files'])=={'src/Avelino/CMakeLists.txt','src/Avelino/TooltipHost.qml','src/Avelino/tooltipwindowlifecycle.cpp','src/Avelino/tooltipwindowlifecycle.h','tests/consumer/tooltipchecks.h'}
    for name,value in activation['files'].items():assert spec['coreFiles'][name]==value
    assert read('source-checks/result.json')['exitCode']==0 and read('source-checks/result.json')['checks']==10
    assert all(step['exitCode']==0 for step in read('source-checks/commands.json'))
    assert read('qt/result.json')['exitCode']==0
    assert all(step['exitCode']==0 for step in read('qt/commands.json'))
    log=(CAPSULE/'qt/date-tests.log').read_text();assert '100% tests passed, 0 tests failed out of 55'in log
    tests=(CAPSULE/'qt/ctest-last-test.log').read_text();assert 'FAIL!'not in tests
    unicode_passes=re.findall(r'PASS\s+: avelino::NavigationContract::test_unicode_fallback_line_box\(([^)]+)\)',tests)
    assert len(unicode_passes)==8 and len(set(unicode_passes))==8
    geometry_passes=re.findall(r'PASS\s+: avelino::NavigationContract::test_native_geometry\(([^)]+)\)',tests)
    assert len(geometry_passes)==384 and len(set(geometry_passes))==384
    font_core=read('font-qt/inputs.json')['files'];assert len(font_core)==602
    assert read('font-qt/result.json')['exitCode']==0 and all(row['exitCode']==0 for row in read('font-qt/commands.json'))
    font_activation=read('font-qt/activated-inputs.json')
    assert font_activation['previousValidatedProducer']=='date-range-qt-v35'and font_activation['cacheBytesMatchSnapshot']
    assert set(font_activation['files'])=={'src/Avelino/buttonlabel.cpp','tests/components/tst_navigation.qml','tests/consumer/Navigation.qml','tests/consumer/navigationchecks.h'}
    for name,value in font_activation['files'].items():assert font_core[name]==spec['coreFiles'][name]==value
    assert read('red/result.json')['exitCode']==4
    red=(CAPSULE/'red/red.log').read_text();assert red.count('FAIL!')==4 and 'Source fallback line box'in red and 'Expected (): 32'in red
    ab={step['name']:step['exitCode']for step in read('ab/result.json')['steps']}
    assert ab['with-cjk']==4 and ab['without-cjk']==0
    assert '190 passed, 4 failed'in (CAPSULE/'ab/with-cjk.log').read_text()
    assert '194 passed, 0 failed'in (CAPSULE/'ab/without-cjk.log').read_text()
    ci=read('ci/base-failure-summary.json')
    assert ci['commit']=='e330fe330ddf9cee494267ce269b0ee9621cec9c'and ci['run']==39167761744
    assert digest(CAPSULE/'ci/base-failure.log')==ci['logSha256']
    assert len(ci['failures'])==16 and ci['onlyUnicodeHeader']
    assert all('NavigationContract::test_native_geometry(page-header-unicode-'in row['text']for row in ci['failures'])
    assert len(ci['ctestSummaries'])==2 and all('96% tests passed, 2 tests failed out of 55'in line for line in ci['ctestSummaries'])
    for dpr in [1,2]:
        text=(CAPSULE/f'matrix/dpr{dpr}.log').read_text();assert '0 failed'in text
        rows={marker:json.loads(line[line.index('{'):])for line in text.splitlines()for marker in ['OWNED_FONT_METRICS','NATIVE_NAVIGATION_METRICS']if marker in line}
        assert rows['OWNED_FONT_METRICS']==dict(count=144,changes=[],dpr=dpr)
        assert rows['NATIVE_NAVIGATION_METRICS']==dict(count=192,dpr=dpr)
    api=read('matrix/api/sources.json');assert api['installedHeaderMatchesRelease']and api['headerVersion']=='6.8.3'
    assert next(row['sha256']for row in api['sources']if row['file']=='qfont.h')==api['installedHeaderSha256']
    # The failed complete run and the focused A/B remain failures. They cannot
    # substitute for the complete display gate, which remains failed below.
    failed=read('tooltips/failed-display/result.json');assert failed['exitCode']==1
    assert read('tooltips/failed-display/completed-records.json')['records']==253
    failed_log=(CAPSULE/'tooltips/failed-display/display.log').read_text()
    assert 'eglSwapBuffers failed with 0x300d, surface: 0x0'in failed_log
    assert 'Visible window did not display a frame'in failed_log
    ab_tooltip=read('tooltips/ab/commands.json');assert len(ab_tooltip)==20
    for prefix,failed_count in [('old',5),('new',1)]:
        rows=[row for row in ab_tooltip if row['prefix']==prefix]
        assert len(rows)==10 and sum(row['exitCode']!=0 for row in rows)==failed_count
        for row in rows:
            if row['exitCode']:
                log=(CAPSULE/f"tooltips/ab/output/{prefix}/trace-v2-{row['attempt']}/tooltip-wayland-opengl-standard.log").read_text()
                assert 'eglSwapBuffers failed with 0x300d, surface: 0x0'in log
                assert 'Visible window did not display a frame'in log
    bindings=read('tooltips/ab/inputs.json')['bindings'];font_package=read('font-package-inputs.json')
    assert bindings['old']['consumerSha256']==bindings['new']['consumerSha256']==font_package['consumerSha256']
    assert bindings['new']['packageFiles']==font_package['packageFiles']
    policy=read('tooltips/policy/commands.json');assert len(policy)==22 and all(row['exitCode']==0 for row in policy)
    red_tooltip=read('tooltips/red/commands.json');assert len(red_tooltip)==5
    assert all(row['exitCode']==0 for row in red_tooltip[:2])and any(row['exitCode']for row in red_tooltip[2:])
    assert read('tooltips/red/inputs.json')['consumerFiles']==spec['consumerFiles']
    # This is a development checkpoint, not a runtime pass. Retain the failed
    # same-ELF run and require its compositor crash to remain visible.
    green=read('tooltips/green/commands.json');assert len(green)==20
    assert [row['attempt']for row in green if row['exitCode']] == [18]
    assert 'Segmentation fault'in (CAPSULE/'tooltips/green/attempt18.log').read_text()
    green_inputs=read('tooltips/green/inputs.json')
    assert green_inputs['consumerSha256']==read('tooltips/red/environment.json')['consumerSha256']
    assert green_inputs['consumerFiles']==spec['consumerFiles']
    assert 'setPersistent'not in (CAPSULE/'implementation-inputs/tests/consumer/tooltipchecks.h').read_text()
    for attempt in range(1,21):
        if attempt==18:
            assert not (CAPSULE/f'tooltips/green/output/attempt{attempt}/tooltip-wayland-opengl-standard.json').exists()
            continue
        row=read(f'tooltips/green/output/attempt{attempt}/tooltip-wayland-opengl-standard.json')
        assert row['tooltipChecks']==row['qtAccessibilityChecks']==row['focusChecks']=='passed'
        assert row['repeatedRemountFrames']==20 and row['retainedCallerEditorFocus']
        assert row['separateTooltipWindow']and row['tooltipWindowType']==13
    ordinary=read('tooltips/ordinary/commands.json');assert len(ordinary)==40
    assert all(row['exitCode']==0 and row['coreFiles']==[]for row in ordinary)
    ordinary_inputs=read('tooltips/ordinary/inputs.json')
    assert ordinary_inputs['originalClientSha256']==green_inputs['consumerSha256']
    ordinary_validation=read('tooltips/ordinary/validation.json')
    assert ordinary_validation['ordinaryRuns']==40 and ordinary_validation['remountFrames']==800
    assert ordinary_validation['priorFailureResolved']is False
    for attempt in range(1,41):
        row=read(f'tooltips/ordinary/output/attempt{attempt}/tooltip-wayland-opengl-standard.json')
        assert row['repeatedRemountFrames']==20 and row['retainedCallerEditorFocus']
        assert row['tooltipChecks']==row['qtAccessibilityChecks']==row['focusChecks']=='passed'
    instrumented=read('tooltips/sanitizer/runtime-commands.json');assert len(instrumented)==32
    assert all(row['exitCode']==0 and not row['sanitizerError']for row in instrumented[:-1])
    assert instrumented[-1]['exitCode']!=0 and instrumented[-1]['sanitizerError']
    assert read('tooltips/sanitizer/runtime-inputs.json')['clientSha256']==green_inputs['consumerSha256']
    sanitizer_inputs=read('tooltips/sanitizer/inputs.json')
    assert sanitizer_inputs['installedVersion']=='13.0.4'and not sanitizer_inputs['sourceModified']
    assert sanitizer_inputs['sourceReleaseSha256']=='66252c9c5bbc45ab402e2518b76e6d824f09ebc1d0040ee2f51b096a1bc585b1'
    fault=(CAPSULE/'tooltips/sanitizer/output/attempt32/weston-client.log').read_text()
    assert 'runtime error: member access within null pointer'in fault
    assert 'weston_desktop_surface_update_view_position'in fault and 'surface.c:117'in fault
    assert result['westonFaultResolved']is False
    tooltip_api=read('tooltips/api/sources.json')
    assert tooltip_api['qt']=='6.8.3'and tooltip_api['installedQuickWindowHeaderMatchesRelease']
    assert next(row['sha256']for row in tooltip_api['sources']if row['file']=='qquickwindow.h')==tooltip_api['installedQuickWindowHeaderSha256']
    package=read('package/inputs.json');assert package['freshConsumerBuild']and len(package['consumerFiles'])==149
    assert green_inputs['packageFiles']==package['packageFiles']
    package_result=read('package/result.json')
    assert package_result['exitCode']==0 and package_result['contexts']==8 and package_result['freshConsumerBuild']
    assert package_result['libraryAndConsumerProjectSourcesAbsentAtRuntime']
    assert package['smokeDriverSha256']==spec['liveScripts']['scripts/check-linux.sh']
    assert all(step['exitCode']==0 for step in read('package/commands.json'))
    assert read('package/result.json')['smokeInvocations']==len(package['smokeArguments'])==41
    for appearance in ['light','dark']:
        for scale in ['1','1.5']:
            for dpr in [1,2]:
                name=f'{appearance}-text{scale}-dpr{dpr}';row=read(f'package/output/{name}.json')
                assert row['fixture']=='navigation'and row['navigationChecks']==row['focusChecks']==row['qtAccessibilityChecks']=='passed'
                assert row['mounts']==3 and row['unmounts']==2 and row['requests']==[2,2,2,0]
                assert row['dpr']==dpr and row['textScale']==float(scale)and row['appearance']==appearance
    assert read('catalog/result.json')['exitCode']==0 and all(step['exitCode']==0 for step in read('catalog/commands.json'))
    assert read('catalog/inputs.json')['scriptSha256']==spec['liveScripts']['scripts/check-installed-catalog.sh']
    assert read('catalog/inputs.json')['packageFiles']==package['packageFiles']
    catalog=read('catalog/output/catalog-results.json');assert catalog['status']=='passed'and catalog['missingModuleRefusal']=='passed'
    assert len(catalog['captures'])==159
    for row in catalog['captures']:
        image=CAPSULE/'catalog/output'/row['path'];assert digest(image)==row['sha256']and digest(image.with_name(image.name+'.json'))==row['metadataSha256']
    assert read('display/result.json')['exitCode']==1 and read('display/result.json')['scriptExitCode']==1
    assert read('display/result.json')['unexpectedCores']==[]
    assert len(read('display/commands.json'))==1 and read('display/commands.json')[0]['exitCode']==1
    display_failure=(CAPSULE/'display/display.log').read_text()
    assert 'FileInput: Capture failed'in display_failure
    assert 'status 99 before producing session evidence: /display-check/output/file-input-wayland-opengl-scaled'in display_failure
    assert result['completeDisplayGatePassed']is False and result['virtualDisplayRecords']==303
    display=read('display/inputs.json')
    assert display['scriptSha256']==spec['liveScripts']['scripts/check-display-sessions.sh']
    assert display['consumerSha256']==package['consumerSha256'] and display['imageId']==package['imageId']
    counts=Counter();navigation=tooltips=0
    fixtures={}
    for path in (CAPSULE/'display/output').glob('*.json'):
        row=json.loads(path.read_text())
        if 'sessionCaptureSha256'not in row:continue
        assert not row['physicalDisplay']and not row['hardwareAcceleration']
        assert digest(path.with_suffix('.png'))==row['windowCaptureSha256']
        assert digest(path.parent/row['sessionCapture'])==row['sessionCaptureSha256']
        backend='software'if row['graphicsApi']==1 else'opengl';assert row['graphicsApi']in [1,3]
        assert row['dpr']in [1,2]and row['textScale']==(1 if row['dpr']==1 else 1.5)
        group=(row['platform'],backend,row['dpr']);counts[group]+=1
        seen=fixtures.setdefault(group,set());assert row['fixture']not in seen;seen.add(row['fixture'])
        if row.get('fixture')=='navigation':assert row['navigationChecks']=='passed';navigation+=1
        if row.get('fixture')=='tooltip':
            assert row['tooltipChecks']==row['qtAccessibilityChecks']==row['focusChecks']=='passed'
            assert row['repeatedRemountFrames']==20 and row['retainedCallerEditorFocus']
            assert row['separateTooltipWindow']and row['tooltipWindowType']==13
            tooltips+=1
    assert len(counts)==8 and sum(counts.values())==303 and navigation==tooltips==8
    assert set(counts)=={(platform,backend,dpr)for platform in ['xcb','wayland']for backend in ['software','opengl']for dpr in [1,2]}
    assert all(value==(37 if group==('wayland','opengl',2)else 38)for group,value in counts.items())
    expected=fixtures[('xcb','software',1)]
    assert len(expected)==38
    for group,seen in fixtures.items():
        assert seen==expected-({'file-input'}if group==('wayland','opengl',2)else set())
    contracts=read('contracts/result.json');assert contracts['exitCode']==0
    assert 'Ran 792 tests'in (CAPSULE/'contracts/tests.log').read_text()
    assert re.search(r'^OK$',(CAPSULE/'contracts/tests.log').read_text(),re.M)
    parent=ROOT/'evidence/development/date-range-fields-20261018';assert digest(parent/'files.json')==spec['parentDateCheckpointSha256']
    # The parent's verifier recomputes original reference comparisons; the new
    # raw date captures must remain byte-identical to that verified checkpoint.
    module_spec=importlib.util.spec_from_file_location('parent_date_fields',ROOT/'scripts/verify-date-range-fields-checkpoint.py')
    module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module);module.verify()
    comparisons=json.loads((parent/'strict/comparison.json').read_text())['results']
    chinese=json.loads((parent/'chinese-comparison.json').read_text())['results']
    for row in comparisons:assert digest(CAPSULE/'date-replay/output'/row['fixture'])==row['candidateSHA256']
    for row in chinese:assert digest(CAPSULE/'date-replay/output'/row['candidateName'])==row['candidateSHA256']
    assert len(comparisons)+len(chinese)==437 and result['dateCandidateImagesIdentical']==437
    replay=read('date-replay/inputs.json');replay_result=read('date-replay/result.json')
    assert replay['consumerFiles']==package['consumerFiles'] and replay['consumerSha256']==package['consumerSha256']
    assert replay['packageFiles']==package['packageFiles'] and not replay['freshConsumerBuild']
    assert replay['consumerCompilationProducer']=='navigation-cjk-package-v2'
    assert replay_result['exitCode']==0 and replay_result['contexts']==replay_result['galleryContexts']==8
    assert replay_result['libraryAndConsumerProjectSourcesAbsentAtRuntime']
    comparison=read('date-replay/raw-image-comparison.json')
    assert comparison['count']==comparison['identical']==437 and comparison['differences']==[]
    assert all(step['exitCode']==0 for step in read('date-replay/commands.json'))
    print('Development checkpoint integrity passed:604 core inputs; 55 Qt and792 Python tests; fresh consumer149,41 smoke invocations,159 catalog captures; display gate FAILED303/304; same-ELF tooltip19/20, Weston null-parent fault UNRESOLVED; date437 images unchanged; mirror acceptance pending')
if __name__=='__main__':verify()
