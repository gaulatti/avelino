#!/usr/bin/env python3
"""Verify native history evidence without granting Linux parity acceptance."""
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/hero-carousel-history-20261018'
REFERENCE = 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
STEPS = ['initial', 'last', 'first', 'width-160', 'width-337', 'last-height-200',
    'last-again', 'first-again', 'reorder', 'remove-last', 'empty', 'empty-idle-1',
    'empty-idle-3', 'restore', 'last-restored', 'first-restored']


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    files = read('files.json')
    assert set(files) == {str(p.relative_to(DIRECTORY)) for p in DIRECTORY.rglob('*')
        if p.is_file() and p.name != 'files.json'}
    for name, entry in files.items():
        path = DIRECTORY / name
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert path.stat().st_size == entry['bytes']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], name
    report = read('investigation.json')
    assert report['reference'] == REFERENCE and report['accepted'] is False
    assert report['historyContexts'] == 2 and report['historySteps'] == 32 and report['historyImages'] == 96
    assert report['appearance'] == 'light' and report['textScale'] == report['dpr'] == 1
    assert report['animationsSuppressed'] is True and report['expectedImagesChanged'] is False
    assert report['tolerance'] == 'none' and report['approvedExceptions'] == []
    assert report['helperSourceAvailability'] == 'external local helpers; independent availability pending'
    assert [command['exitCode'] for command in read('attempt1/commands.json')] == [1]
    for attempt, count in [('attempt2', 12), ('attempt3', 16)]:
        assert [command['exitCode'] for command in read(attempt + '/commands.json')] == [0, 0]
        inputs = read(attempt + '/inputs.json')
        assert inputs['libraryProducer'] == 'avelino-hero-carousel-native-20261018-v2'
        assert inputs['libraryObjectSha256'] == 'dfa92442946e9e93ad12e98686cca6bc80bc7aa9c5e6feb8f134f9ea63eceb4b'
        capture = read(attempt + '/output/histories.json')
        assert capture['accepted'] is False and capture['reference'] == REFERENCE
        assert [row['fitHeight'] for row in capture['histories']] == [False, True]
        expected_steps = STEPS if count == 16 else STEPS[:11] + ['restore']
        for history in capture['histories']:
            assert [step['step'] for step in history['steps']] == expected_steps
            for step in history['steps']:
                assert step['publicProbedIdentical'] is step['publicLiteralIdentical'] is True
                images = [(DIRECTORY / attempt / 'output' / name).read_bytes() for name in step['paths']]
                assert len(images) == 3 and images[0] == images[1] == images[2]
                assert all(struct.unpack('>II', image[16:24]) == (640, 400) for image in images)
                public, probe, literal = step['states']
                assert public['lifecycle'] == probe['lifecycle'] == literal['lifecycle']
                for key in ['carouselFrame', 'slideFrames', 'scrollViews']:
                    assert probe[key] == literal[key], (attempt, step['step'], key)
                fitted = history['fitHeight']
                expected_height = 0 if step['step'].startswith('empty') else 200 if step['step'] in ['reorder', 'remove-last'] else 80
                assert probe['carouselFrame']['height'] == (expected_height if fitted else 180)
                life = public['lifecycle']
                assert life['appearances'] == life['wrapperInstances'] == 1 and life['disappearances'] == 0
                assert all(value == 1 for value in life['slideInstances'].values())
                if step['step'] in ['width-337', 'empty', 'restore', 'last-restored', 'first-restored']:
                    assert life['slideInstances'] == {'0': 1, '1': 1, '2': 1}
                if step['step'].startswith('empty'):
                    assert all(not states for states in life['activeSlideStates'].values())
        assert len(list((DIRECTORY / attempt / 'output').glob('*.png'))) == count * 2 * 3
    limit = read('limit-value/result.json')
    assert [command['exitCode'] for command in read('limit-value/commands.json')] == [0, 0]
    assert limit['accepted'] is False and limit['alwaysMatchesOne'] is True and limit['alwaysMatchesFew'] is False
    assert limit['values']['always'] == limit['values']['alwaysByOne'] != limit['values']['alwaysByFew']
    assert limit['os'] == 'Version 27.0 (Build 26A428)'
    print('HeroCarousel native histories: 32 final steps, 96 identical witness images; acceptance pending')


if __name__ == '__main__':
    verify()
