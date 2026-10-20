#!/usr/bin/env python3
"""Audit owned navigation/modal runtime evidence without accepting native parity."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/file-input-navigation-20261017'


def nodes(item):
    yield item
    for child in item.get('children', []):
        yield from nodes(child)


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    sha = lambda data: hashlib.sha256(data).hexdigest()
    report = read('validation.json')
    assert report['accepted'] is False and report['desktopCandidateCoverage'] == [75, 80]
    assert report['reference'] == 'fe8a1d462fbd793d883fb92086a16aa2947e32c9'
    assert report['expectedImagesChanged'] is False and report['approvedExceptions'] == [] and report['tolerance'] == 'none'
    assert report['physicalDisplay'] is report['physicalInput'] is report['physicalListening'] is False
    assert report['finalFullQtSuiteRerun'] is False
    for gate in ['completeChooser', 'nativeRaster', 'nativeTypes', 'nativeAccessibility', 'nativeReader', 'nativeTiming', 'independentMachine']:
        assert report['gates'][gate] == 'pending', gate
    files = read('files.json')
    assert set(files) == {str(f.relative_to(DIRECTORY)) for f in DIRECTORY.rglob('*') if f.is_file() and f.name != 'files.json'}
    for name, row in files.items():
        path = DIRECTORY / name
        assert path.stat().st_size == row['bytes'] and sha(path.read_bytes()) == row['sha256'], name

    source = read('replay/source.json')
    assert source['baseGit'] == '164be2415d6e40ad4a3010e57efa8ee0e67da218'
    assert source['final'] == 'file-input-qt-v29' and len(source['snapshots']) == 8
    final = source['snapshots'][source['final']]
    assert len(final) == 552
    tree = {r.split(b'\t', 1)[1].decode(): r.split(b'\t', 1)[0].split()[2].decode()
            for r in subprocess.check_output(['git', 'ls-tree', '-rz', '--full-tree', source['baseGit']], cwd=ROOT).split(b'\0') if r}
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as git:
        for name, baseline in source['baseline'].items():
            if baseline is None:
                assert name not in tree
            else:
                assert baseline['blob'] == tree[name]
                git.stdin.write((baseline['blob'] + '\n').encode()); git.stdin.flush()
                header = git.stdout.readline().split(); assert header[1] == b'blob'
                raw = git.stdout.read(int(header[2])); assert git.stdout.read(1) == b'\n'
                assert sha(raw) == baseline['sha256']
            for snapshot in source['snapshots'].values():
                if name not in snapshot:
                    continue
                digest = snapshot[name]
                if not baseline or digest != baseline['sha256']:
                    assert sha((DIRECTORY / 'replay/blobs' / digest).read_bytes()) == digest
        git.stdin.close(); assert git.wait() == 0
    prefix = 'attempts/file-input-qt-v29/'
    assert read(prefix + 'inputs.json')['files'] == final
    assert read(prefix + 'result.json')['exitCode'] == 0
    assert all(step['exitCode'] == 0 for step in read(prefix + 'commands.json'))
    for name in ['foundation-tests', 'backend-tests', 'ui-tests']:
        assert '100% tests passed, 0 tests failed out of 2' in (DIRECTORY / (prefix + name + '.log')).read_text()
    last = (DIRECTORY / 'qt-ui-LastTest.log').read_text()
    assert 'actualNewFolderValidationNestedEscapeAndHistory' in last and 'removingOwnerClosesNestedFolderPrompt' in last
    assert 'directoryFilterKeepsReturnInsideNewFolderPrompt' in last

    prefix = 'attempts/file-input-navigation-package-v5/'
    fresh = read(prefix + 'inputs.json')
    assert fresh['producer'] == 'file-input-qt-v28' and fresh['freshConsumerBuild'] is True
    assert fresh['consumerFiles'] == {name.removeprefix('tests/consumer/'): digest for name, digest in final.items() if name.startswith('tests/consumer/')}
    assert read(prefix + 'result.json')['libraryAndConsumerProjectSourcesAbsentAtRuntime'] is True
    steps = read(prefix + 'commands.json')
    assert len(steps) == 11 and all(step['exitCode'] == 0 for step in steps)
    prefix = 'attempts/file-input-navigation-package-v6/'
    package = read(prefix + 'inputs.json')
    assert package['producer'] == source['final'] and package['consumerSourceIdenticalToFinal'] is True
    assert package['consumerBinarySource'] == 'file-input-navigation-package-v5'
    assert package['consumerSourceProducer'] == fresh['producer'] and package['consumerSha256'] == fresh['consumerSha256']
    assert read(prefix + 'result.json')['consumerSourceAbsent'] is True
    steps = read(prefix + 'commands.json')
    assert len(steps) == 8 and all(step['exitCode'] == 0 for step in steps)
    actions = ['multiple-owner-result', 'cancel-no-result', 'escape-no-result', 'alias-result',
               'new-folder-conflict', 'new-folder-nested-escape', 'new-folder-created', 'history-back',
               'history-forward', 'new-folder-cancel-no-result', 'child-selected', 'removed-in-result']
    baseline = ROOT / 'evidence/development/file-input-20261017/captures'
    contexts = list((DIRECTORY / 'captures').glob('*.json')); assert len(contexts) == 8
    closed = 0
    for path in contexts:
        row = json.loads(path.read_text()); old = json.loads((baseline / path.name).read_text())
        assert row['closed'] == old['closed'] and row['sizing'] == old['sizing']
        assert [a['phase'] for a in row['actions']] == actions and row['images'] == 38
        assert row['pointerEvents'] == 21 and row['keyEvents'] == 32
        for case in row['closed']:
            name = path.stem + '-' + case['configuration']['id'] + '.png'
            assert (path.parent / name).read_bytes() == (baseline / name).read_bytes(), name
            closed += 1
    assert closed == 256
    assert read(prefix + 'visual-binding.json')['byteIdenticalClosedImages'] == 256
    assert read('attempts/file-input-navigation-display-v4/result.json')['exitCode'] == 0
    profiles = set()
    for path in (DIRECTORY / 'display').glob('file-input-*.json'):
        row = json.loads(path.read_text()); profiles.add((row['platform'], row['graphicsApi'], row['dpr']))
        assert row['images'] == 38 and [a['phase'] for a in row['actions']] == actions
        assert row['physicalDisplay'] is row['hardwareAcceleration'] is row['accepted'] is False
    assert profiles == {(p, r, d) for p in ['xcb', 'wayland'] for r in [1, 3] for d in [1, 2]}
    for version, platform in [(8, 'xcb'), (9, 'wayland')]:
        prefix = f'attempts/file-input-navigation-reader-v{version}/'
        assert read(prefix + 'inputs.json')['packageFiles'] == package['packageFiles']
        assert read(prefix + 'exercise-result.json')['exitCode'] == read(prefix + 'session-result.json')['exitCode'] == 0
        row = read(prefix + 'operator-controls-v1/result.json')
        assert row['status'] == 'passed' and row['modalStateExposed'] is True and row['profile']['platform'] == platform
        assert len(row['phases']) == 12 and len(row['announcementEvents']) == 2
        assert all(e['detail1'] == 2 for e in row['announcementEvents'])
        speech = read(prefix + 'speech-observations.json')
        assert all(speech['orcaSpeechOutputChecks'].values()) and all(speech['orcaBackendCommandChecks'].values())
        assert speech['serverUtteranceContentLogged'] is False and speech['physicalAudioHeard'] is False
        assert speech['engineAudioVerification'] == speech['nativeReaderComparison'] == speech['nativeTimingAcceptance'] == 'pending'
        assert len(speech['additionalFocusWaitSeconds']) == 2
        assert speech['producer'] == source['final']
        back = read(prefix + 'operator-controls-v1/history-back.json')
        forward = read(prefix + 'operator-controls-v1/history-forward.json')
        for snapshot, selected in [(back, []), (forward, ['Created by reader'])]:
            assert [n['name'] for n in nodes(snapshot['tree']) if any('STATE_SELECTED ' in s for s in n.get('states', []))] == selected
            buttons = [n for n in nodes(snapshot['tree']) if n['name'] == 'Open' and n['role'] == 'push button']
            assert len(buttons) == 1 and not any('STATE_ENABLED ' in s for s in buttons[0]['states'])
        assert report['historyRestoresFileSelection'] is False
    archived = read('replay/package.json')
    assert archived['chunkBytes'] == 16 * 1024 * 1024
    assert {name.removeprefix('install/'): row['sha256'] for name, row in archived['files'].items() if name.startswith('install/')} == package['packageFiles']
    assert archived['files']['consumer-build/InstalledConsumer']['sha256'] == package['consumerSha256']
    with tempfile.TemporaryDirectory(prefix='avelino-navigation-audit-') as temp:
        out = Path(temp) / 'restored'
        subprocess.run(['python3', str(DIRECTORY / 'tools/reconstruct.py'), '--output', str(out), '--source', '--package'], check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
        for name, digest in final.items(): assert sha((out / 'source' / name).read_bytes()) == digest
        for name, row in archived['files'].items(): assert sha((out / 'package' / name).read_bytes()) == row['sha256']
    portable = read('portable/runtime-result.json')
    assert portable['exitCode'] == 0 and portable['libraryAndConsumerSourceAbsent'] is True
    assert read('portable/comparison.json')['unchangedClosedImages'] == 32
    print('FileInput navigation: six Qt targets, eight package contexts/profiles, modal AT-SPI/Orca flows and package replay; native parity pending')


if __name__ == '__main__':
    verify()
