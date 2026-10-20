#!/usr/bin/env python3
"""Restore exact recorded Linux sources/runtime; no sibling checkout is needed."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re

DIRECTORY = Path(__file__).resolve().parents[1]
CHUNK = 8 * 1024 * 1024


def chunk_bytes(row):
    digest = row['sha256']
    assert re.fullmatch('[0-9a-f]{64}', digest)
    assert 0 < row['bytes'] <= CHUNK
    compressed = (DIRECTORY / 'blobs' / (digest + '.gz')).read_bytes()
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        raw = stream.read(CHUNK + 1)
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == digest
    return raw


def restore(specification, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for name, row in specification.items():
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        digest, count = hashlib.sha256(), 0
        with target.open('xb') as output:
            for part in row['chunks']:
                raw = chunk_bytes(part)
                output.write(raw); digest.update(raw); count += len(raw)
        assert count == row['bytes'] and digest.hexdigest() == row['sha256'], name
        target.chmod(row['mode'])
    return len(specification)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--source', type=int, choices=[62, 63, 64], default=64)
    parser.add_argument('--runtime-only', action='store_true')
    parser.add_argument('--records', action='store_true')
    args = parser.parse_args()
    assert not args.destination.exists(), 'Refuse to overwrite a previous reconstruction'
    args.destination.mkdir(parents=True)
    sources = json.loads((DIRECTORY / 'source-specs.json').read_text())
    source_count = 0
    if not args.runtime_only:
        source_count = restore(sources['file-input-qt-v' + str(args.source)]['files'], args.destination / 'source')
    runtime_count = restore(json.loads((DIRECTORY / 'runtime-spec.json').read_text()), args.destination / 'runtime')
    if args.records:
        restore(json.loads((DIRECTORY / 'records-spec.json').read_text()), args.destination / 'records')
    (args.destination / 'runtime/output').mkdir()
    (args.destination / 'runtime/environment.json').write_bytes((DIRECTORY / 'runtime-environment.json').read_bytes())
    print(f'Restored {source_count} source files and {runtime_count + 1} runtime files; mirror acceptance remains pending')


if __name__ == '__main__':
    main()
