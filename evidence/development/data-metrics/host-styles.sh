set -euo pipefail
mkdir artifacts/data-metrics-implementation/host-styles
for style in Basic Fusion; do
 for appearance in light dark; do
  args=(--fixture data-metrics)
  if [[ "$appearance" == dark ]]; then args+=(--dark); fi
  QML_IMPORT_PATH="$PWD/build/linux/qml" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR=2 QT_QUICK_CONTROLS_STYLE="$style" build/linux/samples/AvelinoCatalog/AvelinoCatalog "${args[@]}" --capture "artifacts/data-metrics-implementation/host-styles/$style-$appearance.png"
 done
done
python3 - <<'PY'
import hashlib,json
from pathlib import Path
frozen=json.loads(Path('artifacts/data-metrics-implementation/frozen-inputs.json').read_text());env=json.loads(Path('artifacts/linux/environment.json').read_text());assert env['sourceInputs']==frozen
for name,h in frozen.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==h,name
env['catalogSha256']=hashlib.sha256(Path('build/linux/samples/AvelinoCatalog/AvelinoCatalog').read_bytes()).hexdigest()
Path('artifacts/data-metrics-implementation/host-styles/environment.json').write_text(json.dumps(env,indent=2)+'\n')
PY
