#!/usr/bin/env bash
set -euo pipefail
# Additional installed catalog route; the sealed 39-route audit stays intact.
evidence="${1:?fresh output directory required}"
mkdir "$evidence"
for appearance in light dark; do
  for dpr in 1 2; do
    args=(--fixture date-range)
    if [[ "$appearance" == dark ]]; then args+=(--dark); fi
    env -u QML_IMPORT_PATH -u QML2_IMPORT_PATH QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR="$dpr" \
      "$PWD/install/bin/AvelinoCatalog" "${args[@]}" --capture "$evidence/$appearance-dpr$dpr.png" >"$evidence/$appearance-dpr$dpr.log" 2>&1
  done
done
python3 - "$evidence" <<'PY'
import hashlib,json,struct,sys
from pathlib import Path
root=Path(sys.argv[1]);rows=[]
expected={f'{appearance}-dpr{dpr}.png' for appearance in ['light','dark'] for dpr in [1,2]}
assert {p.name for p in root.glob('*.png')}==expected
for image in sorted(root.glob('*.png')):
    meta=json.loads(image.with_name(image.name+'.json').read_text())
    assert meta['qt']=='6.8.3' and meta['platform']=='offscreen' and meta['fixture']=='date-range'
    assert struct.unpack('>II',image.read_bytes()[16:24])==(meta['width']*meta['dpr'],meta['height']*meta['dpr'])
    actual=meta['dateRange'];assert actual['ready'] and actual['model']['requests']==[]
    assert actual['model']['start']==1710000000.625 and actual['model']['end']==1710864000.125
    assert actual['model']['appearances']==1 and actual['model']['wrapperInstances']==1 and actual['model']['disappearances']==0
    rows.append(dict(path=image.name,sha256=hashlib.sha256(image.read_bytes()).hexdigest(),metadata=meta))
(root/'result.json').write_text(json.dumps(dict(accepted=False,installedCatalogStartup='passed',captures=rows,strictParity='pending'),indent=2)+'\n')
print('DateRangePicker installed catalog: four unmodified captures; strict parity pending')
PY
