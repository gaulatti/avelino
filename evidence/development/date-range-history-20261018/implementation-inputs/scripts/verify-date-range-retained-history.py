#!/usr/bin/env python3
"""Verify typed DateRangePicker replay while retaining every parity failure."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / 'evidence/development/date-range-history-20261018'


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
    for name in ['qt/date-range-qt-v13', 'qt/date-range-qt-v14', 'package', 'display']:
        assert read(name + '/result.json')['exitCode'] == 0
        assert all(row['exitCode'] == 0 for row in read(name + '/commands.json'))
    history = read('implementation-inputs/tests/consumer/native-date-range-witnesses.json')['history']
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

    for appearance in ['light', 'dark']:
        for scale in ['1', '1.5']:
            for dpr in [1, 2]:
                report = read(f'package/output/{appearance}-text{scale}-dpr{dpr}.json')
                assert len(report['closed']) == report['modelMatches'] == 48 and len(report['input']) == 3
                history_matches(report, appearance == 'light' and scale == '1' and dpr == 1)
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
    before = ROOT / 'evidence/development/date-range-owned-editors-20261018/package/output'
    unchanged = read('unchanged-images.json')
    assert len(unchanged) == 544
    for name, checksum in unchanged.items():
        assert digest(before / name) == digest(CAPSULE / 'package/output' / name) == checksum
    comparisons = read('strict/comparison.json')['results']
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
    print('DateRangePicker: 17 exact model/lifecycle, editor identity, calendar and environment history steps; 544 earlier images unchanged; all 401 raster comparisons fail; physical/reader and full parity remain pending')


if __name__ == '__main__':
    verify()
