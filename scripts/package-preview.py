#!/usr/bin/env python3
"""Package an existing Linux installation and its independent smoke consumer."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import tarfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', type=Path, required=True)
    parser.add_argument('--consumer', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?', args.version)
    assert re.fullmatch(r'[0-9a-f]{40}', args.commit)
    assert not args.output.exists(), 'Use a fresh output directory'
    assert (args.prefix / 'bin/AvelinoCatalog').is_file()
    assert (args.prefix / 'lib/qml/Avelino/libAvelino.so').is_file()
    assert args.consumer.is_file()
    for binary in [args.prefix / 'bin/AvelinoCatalog', args.prefix / 'lib/qml/Avelino/libAvelino.so', args.consumer]:
        with binary.open('rb') as stream: header = stream.read(20)
        assert header[:6] == b'\x7fELF\x02\x01' and struct.unpack_from('<H', header, 18)[0] == 183, f'Expected Linux arm64 ELF: {binary}'
    args.output.mkdir(parents=True)
    name = f'avelino-{args.version}-linux-arm64'
    root = args.output / name
    root.mkdir()
    shutil.copytree(args.prefix, root / 'install', symlinks=True)
    (root / 'consumer-build').mkdir()
    shutil.copy2(args.consumer, root / 'consumer-build/InstalledConsumer')
    for command, target in [('catalog', 'install/bin/AvelinoCatalog'), ('smoke', 'consumer-build/InstalledConsumer')]:
        script = root / command
        script.write_text('''#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
: "${AVELINO_QT_PREFIX:?Set AVELINO_QT_PREFIX to your Qt 6.8.3 SDK directory}"
version=$("$AVELINO_QT_PREFIX/bin/qmake" -query QT_VERSION)
if [ "$version" != 6.8.3 ]; then
    echo "Avelino requires Qt 6.8.3; found $version" >&2
    exit 2
fi
export LD_LIBRARY_PATH="$root/install/lib/qml/Avelino:$AVELINO_QT_PREFIX/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export QML_IMPORT_PATH="$root/install/lib/qml:$AVELINO_QT_PREFIX/qml"
export QT_PLUGIN_PATH="$AVELINO_QT_PREFIX/plugins"
exec "$root/''' + target + '" "$@"\n')
        script.chmod(0o755)
    readme = Path(__file__).resolve().parents[1] / 'docs/desktop-preview.md'
    shutil.copy2(readme, root / 'README.md')
    info = {'version':args.version, 'sourceCommit':args.commit, 'platform':'Ubuntu 24.04 arm64',
            'qt':'6.8.3', 'qtBundled':False, 'kind':'desktop SDK/catalog preview',
            'strictNativeParity':'pending', 'tvSupport':'not included',
            'knownIssues':'https://github.com/gaulatti/avelino/issues?q=is%3Aissue+is%3Aopen'}
    (root / 'BUILD-INFO.json').write_text(json.dumps(info, indent=2) + '\n')
    files = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            assert path.resolve().is_relative_to(root.resolve()), f'Nonportable symlink: {path}'
        if path.is_file(): files[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    (root / 'FILES-SHA256.json').write_text(json.dumps(files, indent=2) + '\n')
    archive = args.output / (name + '.tar.gz')
    with tarfile.open(archive, 'w:gz') as output: output.add(root, arcname=name)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (args.output / 'SHA256SUMS').write_text(f'{digest}  {archive.name}\n')
    print(json.dumps({'archive':str(archive), 'sha256':digest, 'files':len(files),
                      'bytes':archive.stat().st_size, 'sourceCommit':args.commit}, indent=2))


if __name__ == '__main__': main()
