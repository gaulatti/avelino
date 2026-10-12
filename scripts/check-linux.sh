#!/usr/bin/env bash
set -euo pipefail
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
mkdir -p artifacts/linux
QML_IMPORT_PATH="$PWD/build/linux/qml" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software build/linux/samples/AvelinoCatalog/AvelinoCatalog --capture artifacts/linux/actions-light.png
QML_IMPORT_PATH="$PWD/build/linux/qml" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software build/linux/samples/AvelinoCatalog/AvelinoCatalog --dark --capture artifacts/linux/actions-dark.png
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
