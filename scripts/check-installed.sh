#!/usr/bin/env bash
set -euo pipefail
# Run in a fresh toolchain container with only this package directory mounted.
cmake -S consumer -B consumer-build -G Ninja -DCMAKE_PREFIX_PATH="$PWD/install;/opt/qt"
cmake --build consumer-build --parallel 2
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software consumer-build/InstalledConsumer
