#!/usr/bin/env bash
set -euo pipefail
python3 scripts/verify-references.py
mkdir -p .cache/reference-desktop artifacts/reference
python3 - <<'PY'
import json, tarfile
from pathlib import Path
record=json.loads(Path('reference/source-manifest.json').read_text())['references']['desktop']
with tarfile.open(record['artifact']) as artifact:
    artifact.extractall('.cache/reference-desktop',filter='data')
PY
sw_vers > artifacts/reference/os.txt
xcodebuild -version > artifacts/reference/xcode.txt
xcrun swift --version > artifacts/reference/compiler.txt 2>&1
xcrun --sdk macosx --show-sdk-version > artifacts/reference/sdk.txt
git rev-parse HEAD > artifacts/reference/capture-tool-revision.txt
shasum -a 256 reference/capture/Package.swift reference/capture/Sources/AvelinoReferenceCapture/main.swift > artifacts/reference/capture-tool-checksums.txt
swift run --package-path reference/capture AvelinoReferenceCapture "$PWD/artifacts/reference"
cp reference/capture/Package.resolved artifacts/reference/capture-Package.resolved
