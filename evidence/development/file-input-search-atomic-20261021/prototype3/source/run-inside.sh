#!/usr/bin/env bash
set -euo pipefail
cmake -S /prototype -B /output/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/opt/Qt/6.8.3/gcc_arm64
cmake --build /output/build --parallel 2
/output/build/AtomicTokenDocument
