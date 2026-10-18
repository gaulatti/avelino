#!/usr/bin/env python3
"""Audit owned location and persistence evidence without accepting native parity."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/file-input-location-20261017'


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
    assert source['baseGit'] == 'ab287b391ac529981bee85bbc602ce51d9d00261'
    assert source['final'] == 'file-input-qt-v54' and len(source['snapshots']) == 9
    final = source['snapshots'][source['final']]
    assert len(final) == 563
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
    prefix = 'attempts/file-input-qt-v54/'
    assert read(prefix + 'inputs.json')['files'] == final
    assert read(prefix + 'result.json')['exitCode'] == 0
    assert all(step['exitCode'] == 0 for step in read(prefix + 'commands.json'))
    for name, count in [('foundation-tests', 2), ('backend-tests', 3), ('ui-tests', 2)]:
        assert f'100% tests passed, 0 tests failed out of {count}' in (DIRECTORY / (prefix + name + '.log')).read_text()
    last = (DIRECTORY / 'qt-ui-LastTest.log').read_text()
    assert 'actualViewMenuListDisclosureAndIconsNavigation' in last and 'removingListOwnerDuringAccessibleAccept' in last
    assert 'actualLocationMenuSelectionHistoryRecentAndRemoval' in last
    assert 'ReferenceError' not in last and 'TypeError' not in last

    prefix = 'attempts/file-input-location-package-v1/'
    fresh = read(prefix + 'inputs.json')
    assert fresh['producer'] == 'file-input-qt-v50' and fresh['freshConsumerBuild'] is True
    assert fresh['consumerFiles'] == {name.removeprefix('tests/consumer/'): digest for name, digest in final.items() if name.startswith('tests/consumer/')}
    assert read(prefix + 'result.json')['libraryAndConsumerProjectSourcesAbsentAtRuntime'] is True
    steps = read(prefix + 'commands.json')
    assert len(steps) == 11 and all(step['exitCode'] == 0 for step in steps)
    prefix = 'attempts/file-input-location-package-v5/'
    package = read(prefix + 'inputs.json')
    assert package['producer'] == source['final'] and package['consumerSourceIdenticalToFinal'] is True
    assert package['consumerBinarySource'] == 'file-input-location-package-v1'
    assert package['consumerSourceProducer'] == fresh['producer'] and package['consumerSha256'] == fresh['consumerSha256']
    assert read(prefix + 'result.json')['libraryAndConsumerProjectSourcesAbsentAtRuntime'] is True
    steps = read(prefix + 'commands.json')
    assert len(steps) == 8 and all(step['exitCode'] == 0 for step in steps)
    actions = ['multiple-owner-result', 'cancel-no-result', 'escape-no-result', 'alias-result', 'new-folder-conflict', 'new-folder-nested-escape', 'new-folder-created', 'history-back', 'history-forward', 'new-folder-cancel-no-result', 'view-list-root-selection', 'view-list-expanded-selection', 'view-icons-prunes-child', 'view-icons-folder-navigation', 'view-history-clears-selection', 'view-list-keyboard-child', 'view-child-owner-result', 'view-retained-cancel', 'location-current-keeps-selection', 'location-ancestor-clears-selection', 'location-recent-does-not-submit', 'location-history-owner-and-cancel', 'child-selected', 'removed-in-result']
    baseline = ROOT / 'evidence/development/file-input-views-20261017/captures'
    contexts = list((DIRECTORY / 'captures').glob('*.json')); assert len(contexts) == 8
    closed = 0
    for path in contexts:
        row = json.loads(path.read_text()); old = json.loads((baseline / path.name).read_text())
        assert row['closed'] == old['closed'] and row['sizing'] == old['sizing']
        assert [a['phase'] for a in row['actions']] == actions and row['images'] == 44
        assert row['pointerEvents'] == 54 and row['keyEvents'] == 40
        for case in row['closed']:
            name = path.stem + '-' + case['configuration']['id'] + '.png'
            assert (path.parent / name).read_bytes() == (baseline / name).read_bytes(), name
            closed += 1
    assert closed == 256
    assert read(prefix + 'visual-binding.json')['byteIdenticalClosedImages'] == 256
    assert read('attempts/file-input-location-display-v5/result.json')['exitCode'] == 0
    profiles = set()
    for path in (DIRECTORY / 'display').glob('file-input-*.json'):
        row = json.loads(path.read_text()); profiles.add((row['platform'], row['graphicsApi'], row['dpr']))
        assert row['images'] == 44 and [a['phase'] for a in row['actions']] == actions
        assert row['physicalDisplay'] is row['hardwareAcceleration'] is row['accepted'] is False
    assert profiles == {(p, r, d) for p in ['xcb', 'wayland'] for r in [1, 3] for d in [1, 2]}
    for version, platform in [(19, 'xcb'), (18, 'wayland')]:
        prefix = f'attempts/file-input-location-reader-v{version}/'
        assert read(prefix + 'inputs.json')['packageFiles'] == package['packageFiles']
        assert read(prefix + 'exercise-result.json')['exitCode'] == read(prefix + 'session-result.json')['exitCode'] == 0
        row = read(prefix + 'operator-controls-v1/result.json')
        assert row['status'] == 'passed' and row['modalStateExposed'] is True and row['profile']['platform'] == platform
        assert len(row['phases']) == (25 if platform == 'wayland' else 24) and len(row['announcementEvents']) == 2
        assert all(e['detail1'] == 2 for e in row['announcementEvents'])
        speech = read(prefix + 'speech-observations.json')
        assert all(speech['orcaSpeechOutputChecks'].values()) and all(speech['orcaBackendCommandChecks'].values())
        assert speech['serverUtteranceContentLogged'] is False and speech['physicalAudioHeard'] is False
        assert speech['engineAudioVerification'] == speech['nativeReaderComparison'] == speech['nativeTimingAcceptance'] == 'pending'
        assert len(speech['additionalFocusWaitSeconds']) == 2
        assert speech['producer'] == source['final']
        assert speech['logReadAfterSessionExit'] is True
        assert speech['assistiveMultiselectionMethod'] == 'AT-SPI Selection.selectChild'
        menu = read(prefix + 'operator-controls-v1/location-current-menu.json')
        openers = [n for n in nodes(menu['tree']) if n['name'] == 'Where:']
        assert len(openers) == 1 and openers[0]['role'] == 'push button menu'
        assert 'Press' in openers[0]['actions']
        assert any('STATE_EXPANDED ' in state for state in openers[0]['states'])
        menus = [n for n in openers[0]['children'] if n['role'] == 'popup menu']
        assert len(menus) == 1
        items = [n for n in nodes(menus[0]) if n['role'] == 'menu item']
        assert [n['name'] for n in items] == ['fixtures', 'probe', '/']
        assert all('Press' in n['actions'] for n in items)
        current = read(prefix + 'operator-controls-v1/location-current-preserves-selection.json')
        assert current['observations']['selected'] == ['one.txt']
        ancestor = read(prefix + 'operator-controls-v1/location-ancestor-clears-selection.json')
        assert ancestor['observations']['selected'] == [] and ancestor['observations']['location'] == '/probe'
        escape = read(prefix + 'operator-controls-v1/location-menu-escape-keeps-chooser.json')
        assert escape['observations']['selected'] == ['one.txt']
        assert any(n['name'] == 'Open' and n['role'] == 'dialog' for n in nodes(escape['tree']))
        assert not any(n['role'] == 'menu item' for n in nodes(escape['tree']))
        recent = read(prefix + 'operator-controls-v1/location-recent-menu-after-reopen.json')
        assert recent['observations']['matchingFolderItems'] == 2
        if platform == 'wayland':
            assert speech['applicationSwitchDismissal'] is True
            assert speech['nativeWaylandPopupSurfaces'] >= 6 and speech['nativeWaylandPopupGrabs'] == 0
            assert speech['nativeHostFocus']['keyEventsSent'] == 0
            client = (DIRECTORY / (prefix + 'client.log')).read_text()
            assert len(re.findall(r' -> xdg_surface@\d+\.get_popup\(', client)) == speech['nativeWaylandPopupSurfaces']
            assert not re.search(r' -> xdg_popup@\d+\.grab\(', client)
            switched = read(prefix + 'operator-controls-v1/location-deactivation-closes-menu.json')
            assert switched['observations']['owner'] == recent['observations']['owner']
        disclosure = read(prefix + 'operator-controls-v1/list-accessible-disclosure.json')
        cells = [n for n in nodes(disclosure['tree']) if n['name'] == 'one.txt' and n['role'] == 'table cell']
        assert len(cells) == 1 and cells[0]['tableCell']['headers'] == ['Name']
        selected = read(prefix + 'operator-controls-v1/list-cross-level-selection.json')
        names = sorted(n['name'] for n in nodes(selected['tree'])
                       if n.get('tableCell', {}).get('position', [])[-1:] == [0]
                       and any('STATE_SELECTED ' in state for state in n.get('states', [])))
        assert names == ['child.txt', 'one.txt']
        log = (DIRECTORY / (prefix + 'orca-debug.log')).read_text()
        assert "Couldn't find table-implementing ancestor" not in log
        assert not any('Expand one.txt' in line for line in log.splitlines() if 'SPEECH OUTPUT:' in line)
        assert 'ReferenceError' not in (DIRECTORY / (prefix + 'client.log')).read_text()
    assert read('attempts/file-input-qt-v47/result.json')['failedStep'] == 'ui-build'
    assert read('attempts/file-input-qt-v48/result.json')['failedStep'] == 'ui-tests'
    assert read('attempts/file-input-qt-v49/result.json')['failedStep'] == 'ui-tests'
    assert read('attempts/file-input-location-display-v3/result.json')['exitCode'] == 1
    for version in [1, 2, 11]:
        assert read(f'attempts/file-input-location-reader-v{version}/exercise-result.json')['exitCode'] == 1
    exits = read('attempts/file-input-location-reader-v15/children-before-cleanup.json')
    assert any(row['command'][0] == 'weston' and row['exitCode'] == -11 for row in exits)
    stack = (DIRECTORY / 'attempts/file-input-location-reader-v16/weston-client.log').read_text()
    assert 'Program received signal SIGSEGV' in stack and 'weston_desktop_surface_foreach_child' in stack
    toolchain = read('toolchain.json')
    assert toolchain['qtVersion'] == '6.8.3' and toolchain['imageId'] == package['imageId']
    qt = toolchain['qtLibrariesUnchanged']; assert qt['librariesUnchanged'] is True
    hashes = list(qt['files'].values()); assert len(hashes) == 2 and len(hashes[0]) == 6 and hashes[0] == hashes[1]
    for name, digest in toolchain['repositoryFiles'].items():
        assert sha((DIRECTORY / 'tools/toolchain' / Path(name).name).read_bytes()) == digest
    installer = read('attempts/location-weston13-fixed-image-v3/inputs.json')
    assert installer['installerSha256'] == toolchain['repositoryFiles']['tools/install-weston.sh']
    assert toolchain['compositorSource']['sha256'] == installer['source']['sha256'] == '66252c9c5bbc45ab402e2518b76e6d824f09ebc1d0040ee2f51b096a1bc585b1'
    assert read('attempts/location-weston13-fixed-image-v3/result.json')['exitCode'] == 0
    stock = read('attempts/location-weston-stock-tooltip/result.json')
    fixed = read('attempts/location-weston-stock-tooltip-fixed13-v1/result.json')
    assert stock['stockTooltipReproducesCrash'] is True and fixed['stockTooltipReproducesCrash'] is False
    assert stock['helperSha256'] == fixed['helperSha256']
    assert stock['avelinoLibraryLoaded'] is fixed['avelinoLibraryLoaded'] is False
    assert stock['weston'] == 'weston 13.0.0' and fixed['weston'] == 'weston 13.0.4'
    assert fixed['westonGdbExit'] is fixed['ownerExit'] is fixed['otherExit'] is None
    archived = read('replay/package.json')
    assert archived['chunkBytes'] == 16 * 1024 * 1024
    assert {name.removeprefix('install/'): row['sha256'] for name, row in archived['files'].items() if name.startswith('install/')} == package['packageFiles']
    assert archived['files']['consumer-build/InstalledConsumer']['sha256'] == package['consumerSha256']
    with tempfile.TemporaryDirectory(prefix='avelino-location-audit-') as temp:
        out = Path(temp) / 'restored'
        subprocess.run(['python3', str(DIRECTORY / 'tools/reconstruct.py'), '--output', str(out), '--source', '--package'], check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
        for name, digest in final.items(): assert sha((out / 'source' / name).read_bytes()) == digest
        for name, row in archived['files'].items(): assert sha((out / 'package' / name).read_bytes()) == row['sha256']
    portable = read('portable/runtime-result.json')
    assert portable['exitCode'] == 0 and portable['libraryAndConsumerSourceAbsent'] is True
    assert read('portable/comparison.json')['unchangedClosedImages'] == 32
    print('FileInput locations: seven Qt targets, eight source-free package/display profiles, 24/25-phase AT-SPI/Orca flows and replay; strict native parity pending')


if __name__ == '__main__':
    verify()
