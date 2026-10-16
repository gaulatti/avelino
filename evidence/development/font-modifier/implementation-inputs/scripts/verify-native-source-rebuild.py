#!/usr/bin/env python3
"""Audit preserved desktop source-rebuild evidence without accepting Qt parity."""
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'evidence/reference-investigations/native-source-rebuild-20261016'
SOURCE = ROOT / 'evidence/reference-investigations/data-metrics-20261015'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(name):
    path = PurePosixPath(name)
    assert name and path.parts and str(path) == name and not path.is_absolute() and '..' not in path.parts, 'Unsafe evidence path'
    return path


def tree_hash(files):
    """Reconstruct the pinned Git tree from all recorded blob IDs and modes."""
    root = {}
    for row in files:
        parts = relative(row['path']).parts
        node = root
        for part in parts[:-1]:
            node = node.setdefault(part, {})
            assert isinstance(node, dict), 'Conflicting source paths'
        assert parts[-1] not in node, 'Duplicate source path'
        assert row['mode'] in {'100644', '100755'}
        assert len(row['gitBlob']) == 40
        node[parts[-1]] = (row['mode'], bytes.fromhex(row['gitBlob']))

    def encode(node):
        entries = []
        for name, value in node.items():
            directory = isinstance(value, dict)
            mode, oid = ('40000', encode(value)) if directory else value
            key = name.encode() + (b'/' if directory else b'')
            entries.append((key, mode.encode() + b' ' + name.encode() + b'\0' + oid))
        payload = b''.join(data for _, data in sorted(entries))
        return hashlib.sha1(b'tree ' + str(len(payload)).encode() + b'\0' + payload).digest()

    return encode(root).hex()


def verify(directory=DIRECTORY):
    directory = Path(directory)
    report = json.loads((directory / 'investigation.json').read_text())
    reference = json.loads((ROOT / 'reference/source-manifest.json').read_text())['references']['desktop']
    assert report['referenceRevision'] == reference['revision'] and report['referenceTree'] == reference['tree']
    assert report['accepted'] is False and report['existingExpectedImagesChanged'] is False
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual == set(report['files']) | {'investigation.json'}, 'Missing or extra rebuild evidence'
    for name, expected in report['files'].items():
        relative(name)
        assert digest(directory / name) == expected, name

    source = json.loads((directory / 'source-identity.json').read_text())
    files = source['files']
    assert len(files) == source['unchangedAfterFirstBuild'] == source['unchangedAfterArchiveReplay'] == 89
    assert tree_hash(files) == reference['tree'], 'Complete source tree differs from pinned Git tree'
    bypath = {row['path']: row for row in files}
    assert source['originalArchiveInputsVerified'] == len(reference['files']) == 53
    assert source['unchangedHistoricalScopedInputsAfterFailedBuild'] == 53
    for row in reference['files']:
        assert all(bypath[row['path']][key] == row[key] for key in ['mode', 'gitBlob', 'sha256']), row['path']

    build = json.loads((directory / 'build-provenance.json').read_text())
    artifact = build['sourceOnlyArtifact']
    assert build['compiledInputs'] == [], 'Compiled Sabella inputs cannot prove a source rebuild'
    assert set(artifact['files']) == {'reference-source.tar', 'rebuild.py', 'tool/Sources/NativeCapture/main.swift', 'tool/run-capture.py', 'inputs.json'}
    assert artifact['files']['reference-source.tar'] == source['fullArchiveSha256']
    assert build['automaticResolution'] is False and build['target'] == 'arm64-apple-macosx26.0'
    assert build['buildTarget'] == 'Sabella' and build['sourceArchiveSha256'] == reference['sha256']
    assert build['firstBuildExitCode'] == build['archiveReplayExitCode'] == 0
    assert build['historicalScopedArchiveBuildExitCode'] == 1
    assert {p['identity']: p['revision'] for p in build['dependencies']} == {
        'ksplayer': '10a40a1c0001d75307ad5922d1d1bc0cb01c89b4',
        'ffmpegkit': 'c32be9bfb628042737ad3ef622e930c5c7b15954',
    }, 'Native dependency lock changed'
    original = json.loads((SOURCE / 'tooling-provenance.json').read_text())['toolArtifact']['files']
    for name in ['tool/Sources/NativeCapture/main.swift', 'tool/run-capture.py']:
        assert artifact['files'][name] == original[name], 'Capture helper changed during source rebuild'
    for name in ['firstBuildProducts', 'archiveReplayProducts']:
        assert 'Sabella.o' in build[name] and any(p.endswith('.swiftmodule') for p in build[name])

    comparison = json.loads((directory / 'comparison.json').read_text())
    previous = json.loads((SOURCE / 'clean-replay.json').read_text())
    expected = {r['path']: r['sha256'] for r in previous['results']}
    rows = comparison['results']
    assert len(rows) == comparison['filesCompared'] == comparison['firstBuildIdenticalFiles'] == comparison['archiveReplayIdenticalFiles'] == 3160
    assert len({r['path'] for r in rows}) == len(rows) and {r['path'] for r in rows} == set(expected), 'Rebuild output coverage changed'
    for row in rows:
        name = row['path']
        relative(name)
        assert row['expectedSha256'] == row['freshSha256'] == row['archiveReplaySha256'] == expected[name] == digest(SOURCE / name), 'Rebuilt output differs: ' + name
    assert report['nativeCaptures'] == 1048 and report['localeFormatterWitnesses'] == 1330
    return {'pinnedSourceFiles': len(files), 'nativeCaptures': 1048, 'localeFormatterWitnesses': 1330,
            'firstBuildIdenticalFiles': 3160, 'sourceOnlyArchiveReplayIdenticalFiles': 3160, 'accepted': False}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
