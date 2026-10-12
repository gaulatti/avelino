#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/linux
python3 - <<'PY'
import hashlib, json, subprocess
from pathlib import Path
def command(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()
files = sorted([Path('CMakeLists.txt'), Path('CMakePresets.json')] +
    [p for folder in ['src', 'samples', 'assets', 'tokens', 'tests', 'scripts', 'cmake', 'tools', 'evidence/geometry']
     for p in Path(folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts])
# The CI bind mount belongs to the runner UID, while the toolchain runs as root.
# Trust only this explicit checkout for these read-only provenance commands.
git = ['git', '-c', f'safe.directory={Path.cwd()}']
metadata = {
    'sourceRevision': command(*git, 'rev-parse', 'HEAD'),
    'uncommittedChanges': bool(command(*git, 'status', '--porcelain')),
    'compiler': command('c++', '--version'),
    'qt': command('qmake', '-query', 'QT_VERSION'),
    'cmake': command('cmake', '--version'),
    'installedPackages': command('dpkg-query', '-W'),
    'sourceInputs': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
}
Path('artifacts/linux/environment.json').write_text(json.dumps(metadata, indent=2)+'\n')
PY
cmake --preset linux
cmake --build --preset linux
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software ctest --preset linux
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
cmake --install build/linux --prefix "$stage/install"
cp -R tests/consumer "$stage/consumer"
cmake -S "$stage/consumer" -B "$stage/build" -G Ninja -DCMAKE_PREFIX_PATH="$stage/install;/opt/qt"
cmake --build "$stage/build" --parallel 2
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer")
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --controls)
mkdir -p artifacts
# Always publish the already-verified fresh stage. Repeated cp into an existing
# directory nests the consumer and leaves obsolete source/install files behind.
if [[ -e artifacts/package ]]; then mv artifacts/package "$stage/previous-package"; fi
mkdir artifacts/package
cp -R "$stage/install" "$stage/consumer" artifacts/package/
cp scripts/check-installed.sh artifacts/package/check-installed.sh
cp scripts/check-display-sessions.sh artifacts/package/check-display-sessions.sh
cp artifacts/linux/environment.json artifacts/package/environment.json
mkdir -p artifacts/linux
QML_IMPORT_PATH="$PWD/build/linux/qml" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software build/linux/samples/AvelinoCatalog/AvelinoCatalog --capture artifacts/linux/actions-light.png
QML_IMPORT_PATH="$PWD/build/linux/qml" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software build/linux/samples/AvelinoCatalog/AvelinoCatalog --dark --capture artifacts/linux/actions-dark.png
for fixture in foundations surfaces data-display controls; do
for appearance in light dark; do
  for dpr in 1 2; do
    args=(--fixture "$fixture")
    if [[ "$appearance" == dark ]]; then args+=(--dark); fi
    QML_IMPORT_PATH="$PWD/build/linux/qml" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR="$dpr" \
      build/linux/samples/AvelinoCatalog/AvelinoCatalog "${args[@]}" --capture "artifacts/linux/$fixture-$appearance-dpr$dpr.png"
  done
done
done
for appearance in light dark; do
  for variant in primary secondary outline subtle ghost link destructive; do
    for size in xs sm md lg; do
      for state in enabled disabled; do
        args=(--fixture button --variant "$variant" --size "$size")
        if [[ "$appearance" == dark ]]; then args+=(--dark); fi
        if [[ "$state" == disabled ]]; then args+=(--disabled); fi
        QML_IMPORT_PATH="$PWD/build/linux/qml" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR=2 \
          build/linux/samples/AvelinoCatalog/AvelinoCatalog "${args[@]}" --capture "artifacts/linux/button-$appearance-$variant-$size-$state.png"
      done
    done
  done
done
