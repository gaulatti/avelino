#!/usr/bin/env python3
"""Verify the CI contract repair without granting application parity acceptance."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import shlex
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/development/ci-runtime-contracts-20261018'


def verify():
    read = lambda name: json.loads((DIRECTORY / name).read_text())
    digest = lambda raw: hashlib.sha256(raw).hexdigest()
    files = read('files.json')
    assert set(files) == {str(path.relative_to(DIRECTORY)) for path in DIRECTORY.rglob('*')
        if path.is_file() and path.name != 'files.json'}
    for name, row in files.items():
        raw = (DIRECTORY / name).read_bytes()
        assert len(raw) == row['bytes'] and digest(raw) == row['sha256'], name
    result = read('result.json')
    assert result['accepted'] is False and result['exitCode'] == 0
    assert result['applicationSourcesChanged'] is False
    assert result['baselineDisplayFailures'] == result['fixedDisplayProfiles'] == 8
    assert result['catalogCaptures'] == 159 and result['unprivilegedArtifactRead'] == 'passed'
    steps = read('commands.json')
    assert all(step['exitCode'] == step['expectedExitCode'] for step in steps)
    assert sum(step['name'].startswith('before-file-input-') for step in steps) == 8
    assert sum(step['name'].startswith('after-file-input-') for step in steps) == 8
    assert {step['name'] for step in steps if step['name'].startswith('catalog-')} == {
        'catalog-missing-capture', 'catalog-unexpected-capture'}
    earlier = read('attempts/v1/commands.json')
    assert earlier[-1]['name'] == 'artifact-permissions' and earlier[-1]['exitCode'] == 1
    for name in ['scripts/check-installed-catalog.sh', 'scripts/check-display-sessions.sh', '.github/workflows/linux.yml']:
        actual = (subprocess.check_output(['git', 'show', '2b837a5fd52b462b59d8d66dae4a71a3a88bce20:'+name], cwd=ROOT)
                  if name == '.github/workflows/linux.yml' else (ROOT / name).read_bytes())
        assert (DIRECTORY / 'after' / name).read_bytes() == actual, name
    source = ROOT / 'evidence/development/file-input-go-to-suggestions-20261018/display/output'
    inputs = read('input-reports.json')
    assert len(inputs) == 8
    for name, checksum in inputs.items():
        path = source / name
        assert digest(path.read_bytes()) == checksum
        report = json.loads(path.read_text())
        assert report['images'] == 49 and len(report['actions']) == 30
        assert report['pointerEvents'] == 62 and report['keyEvents'] == 164
    catalog = read('catalog-evidence/catalog-results.json')
    text = (DIRECTORY / 'after/scripts/check-installed-catalog.sh').read_text()
    fixtures = shlex.split(re.search(r'^fixtures=\((.*)\)$', text, re.M)[1])
    assert len(fixtures) == len(set(fixtures)) == 39
    expected = {f'{fixture}-{appearance}-dpr{dpr}.png' for fixture in fixtures
        for appearance in ['light', 'dark'] for dpr in [1, 2]}
    expected.update({'actions-light.png', 'actions-dark.png', 'button-light-primary-md-enabled.png'})
    assert {row['path'] for row in catalog['captures']} == expected
    for row in catalog['captures']:
        image = DIRECTORY / 'catalog-evidence' / row['path']
        metadata = image.with_name(image.name + '.json')
        assert digest(image.read_bytes()) == row['sha256']
        assert digest(metadata.read_bytes()) == row['metadataSha256']
        value = json.loads(metadata.read_text())
        assert value['qt'] == '6.8.3' and value['platform'] == 'offscreen'
        assert struct.unpack('>II', image.read_bytes()[16:24]) == (value['width'] * value['dpr'], value['height'] * value['dpr'])
    permission = read('permissions/result.json')
    assert permission['beforeExit'] != 0 and permission['afterExit'] == 0 and permission['bytesUnchanged'] is True
    assert permission['filesystem'] == 'container Linux filesystem'
    assert {row['tree'] for row in permission['paths']} == {
        'artifacts/linux', 'artifacts/package', 'build/linux/Testing/Temporary'}
    assert all(row['beforeExit'] != 0 and row['afterExit'] == 0
        and 'PermissionError' in row['beforeError'] for row in permission['paths'])
    for name in ['older-linux-amd64-raw.log.gz', 'hero-linux-arm64-raw.log.gz']:
        raw = gzip.decompress((DIRECTORY / 'ci-logs' / name).read_bytes())
        assert b'EACCES: permission denied, scandir' in raw
    assert b'AssertionError: 159' in gzip.decompress((DIRECTORY / 'ci-logs/hero-linux-arm64-raw.log.gz').read_bytes())
    print('CI runtime contracts: eight stale display failures reproduced, eight current profiles accepted, 159 catalog captures and unprivileged artifact access verified; mirror acceptance pending')


if __name__ == '__main__':
    verify()
