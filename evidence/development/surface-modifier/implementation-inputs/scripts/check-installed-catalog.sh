#!/usr/bin/env bash
set -euo pipefail
# Run from a package root containing install/; no source/build import override.
evidence="${1:-$PWD/catalog-evidence}"
mkdir "$evidence"
catalog="$PWD/install/bin/AvelinoCatalog"
fixtures=(foundations surfaces data-display controls composition selection checkbox secure-field search-field collection-filters slider tabs pagination pagination-integers accordion presentation-states spinner alert clipping navigation sidebar-brand data-metrics stepper radio-group otp-input activity-item modal tooltip button-style font-modifier surface-modifier)
for fixture in "${fixtures[@]}"; do
  for appearance in light dark; do
    for dpr in 1 2; do
      args=(--fixture "$fixture")
      if [[ "$appearance" == dark ]]; then args+=(--dark); fi
      env -u QML_IMPORT_PATH -u QML2_IMPORT_PATH LANG=C.UTF-8 QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR="$dpr" \
        "$catalog" "${args[@]}" --capture "$evidence/$fixture-$appearance-dpr$dpr.png"
    done
  done
done
for appearance in light dark; do
  args=(); if [[ "$appearance" == dark ]]; then args+=(--dark); fi
  env -u QML_IMPORT_PATH -u QML2_IMPORT_PATH LANG=C.UTF-8 QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1 \
    "$catalog" "${args[@]}" --capture "$evidence/actions-$appearance.png"
done
env -u QML_IMPORT_PATH -u QML2_IMPORT_PATH LANG=C.UTF-8 QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR=2 \
  "$catalog" --fixture button --capture "$evidence/button-light-primary-md-enabled.png"
# An executable without its installed module must still fail visibly.
missing="$(mktemp -d)"
trap 'rm -rf "$missing"' EXIT
mkdir "$missing/bin"
cp "$catalog" "$missing/bin/AvelinoCatalog"
set +e
env -u QML_IMPORT_PATH -u QML2_IMPORT_PATH LANG=C.UTF-8 QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software \
  "$missing/bin/AvelinoCatalog" --fixture pagination --capture "$missing/unexpected.png" >"$evidence/missing-module.log" 2>&1
missing_result=$?
set -e
if [[ "$missing_result" == 0 ]]; then echo 'Catalog unexpectedly started without its installed module' >&2;exit 1;fi
python3 - "$evidence/missing-module.log" <<'PYCODE'
from pathlib import Path
import sys
assert 'module "Avelino" is not installed' in Path(sys.argv[1]).read_text()
PYCODE
python3 - "$evidence" <<'PY'
import hashlib,json,struct,sys
from pathlib import Path
root=Path(sys.argv[1]);records=[]
for image in sorted(root.glob('*.png')):
 meta=json.loads(image.with_name(image.name+'.json').read_text())
 assert meta['qt']=='6.8.3' and meta['platform']=='offscreen'
 assert struct.unpack('>II',image.read_bytes()[16:24])==(meta['width']*meta['dpr'],meta['height']*meta['dpr'])
 records.append({'path':image.name,'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'metadataSha256':hashlib.sha256(image.with_name(image.name+'.json').read_bytes()).hexdigest()})
assert len(records)==127,len(records)
(root/'catalog-results.json').write_text(json.dumps({'status':'passed','method':'installed executable; QML_IMPORT_PATH and QML2_IMPORT_PATH explicitly unset; offscreen software','captures':records,'missingModuleRefusal':'passed','acceptance':'startup/relocation evidence only; strict mirror and physical/session gates remain separate'},indent=2)+'\n')
print('Installed catalog: 127 fixture captures passed without source/build import paths')
PY
