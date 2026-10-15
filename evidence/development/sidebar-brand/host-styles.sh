set -euo pipefail
mkdir artifacts/sidebar-brand/host-styles
for style in Basic Fusion; do
 for appearance in light dark; do
  args=(--fixture sidebar-brand)
  if [[ "$appearance" == dark ]]; then args+=(--dark); fi
  QML_IMPORT_PATH="$PWD/build/linux/qml" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software QT_SCALE_FACTOR=2 QT_QUICK_CONTROLS_STYLE="$style" build/linux/samples/AvelinoCatalog/AvelinoCatalog "${args[@]}" --capture "artifacts/sidebar-brand/host-styles/$style-$appearance.png"
 done
done
python3 - <<'PY'
import hashlib,json
from pathlib import Path
frozen=json.loads(Path('artifacts/sidebar-brand/frozen-inputs.json').read_text());env=json.loads(Path('artifacts/linux/environment.json').read_text());assert env['sourceInputs']==frozen
for name,digest in frozen.items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
binary=Path('build/linux/samples/AvelinoCatalog/AvelinoCatalog');env['catalogSha256']=hashlib.sha256(binary.read_bytes()).hexdigest()
Path('artifacts/sidebar-brand/host-styles/environment.json').write_text(json.dumps(env,indent=2)+'\n')
PY
