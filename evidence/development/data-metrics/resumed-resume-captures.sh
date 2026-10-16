#!/usr/bin/env bash
set -euo pipefail
root="$PWD/artifacts/resumed-avelino-20261016"
mkdir -p "$root/capture-staging" "$root/previous-capture-groups"
export QML_IMPORT_PATH="$PWD/build/linux/qml"
while read -r group folder reference; do
  if python3 - "$folder" <<'PY'
import json, sys
from pathlib import Path
root=Path('artifacts/linux')/sys.argv[1]
frozen=json.loads(Path('artifacts/data-metrics-implementation/frozen-inputs.json').read_text())
try:
    env=json.loads((root/'environment.json').read_text())
    result=json.loads((root/'capture-results.json').read_text())
except FileNotFoundError:
    raise SystemExit(1)
raise SystemExit(0 if env['sourceInputs']==frozen and result['status']=='captured' else 1)
PY
  then
    printf 'Preserved verified capture group: %s\n' "$group"
    continue
  fi
  python3 scripts/capture-proposals.py \
    --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
    --reference "evidence/reference-proposals/$reference" \
    --output "$root/capture-staging/$group"
  if [[ -e "artifacts/linux/$folder" ]]; then
    mv "artifacts/linux/$folder" "$root/previous-capture-groups/$folder"
  fi
  mv "$root/capture-staging/$group" "artifacts/linux/$folder"
done <<'GROUPS'
desktop proposals desktop-20261012
composition composition-proposals composition-20261012-v1
selectors selector-proposals selectors-20261013
checkbox checkbox-proposals checkbox-20261013
secure-field secure-field-proposals secure-field-20261014
search-field search-field-proposals search-field-20261014
collection-filters collection-filters-proposals collection-filters-20261014
slider slider-proposals slider-20261014-v2
tabs tabs-proposals tabs-20261014
pagination pagination-proposals pagination-20261014
pagination-integers pagination-integer-proposals pagination-integers-20261014
accordion accordion-proposals accordion-20261014
presentation-states presentation-state-proposals presentation-states-20261015-v2
alert alert-proposals alert-20261015
navigation navigation-proposals navigation-layout-20261015
sidebar-brand sidebar-brand-proposals sidebar-brand-20261015
data-metrics data-metrics-proposals data-metrics-20261015
GROUPS
python3 artifacts/data-metrics-implementation/audit-progress.py
