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
cmp assets/secure-field-symbols.json "$stage/install/share/avelino/secure-field-symbols.json"
cmp assets/search-field-symbols.json "$stage/install/share/avelino/search-field-symbols.json"
cmp assets/filter-chip-symbols.json "$stage/install/share/avelino/filter-chip-symbols.json"
cmp assets/navigation-symbols.json "$stage/install/share/avelino/navigation-symbols.json"
cmp assets/presentation-symbols.json "$stage/install/share/avelino/presentation-symbols.json"
cmp assets/spinner-presentation.json "$stage/install/share/avelino/spinner-presentation.json"
cmp assets/alert-symbols.json "$stage/install/share/avelino/alert-symbols.json"
cmp assets/brand-presentation.json "$stage/install/share/avelino/brand-presentation.json"
cmp assets/data-metrics-presentation.json "$stage/install/share/avelino/data-metrics-presentation.json"
cmp assets/sidebar-symbols.json "$stage/install/share/avelino/sidebar-symbols.json"
cmp assets/stepper-presentation.json "$stage/install/share/avelino/stepper-presentation.json"
cmp assets/radio-presentation.json "$stage/install/share/avelino/radio-presentation.json"
cmp assets/activity-presentation.json "$stage/install/share/avelino/activity-presentation.json"
cmp assets/modal-presentation.json "$stage/install/share/avelino/modal-presentation.json"
cmp assets/tooltip-presentation.json "$stage/install/share/avelino/tooltip-presentation.json"
cmp assets/unicode/LICENSE.txt "$stage/install/share/avelino/unicode/LICENSE.txt"
cmp assets/unicode/provenance.json "$stage/install/share/avelino/unicode/provenance.json"
cmp assets/brand/BleeckerLogo.png "$stage/install/share/avelino/brand/BleeckerLogo.png"
cp -R tests/consumer "$stage/consumer"
cmake -S "$stage/consumer" -B "$stage/build" -G Ninja -DCMAKE_PREFIX_PATH="$stage/install;/opt/qt"
cmake --build "$stage/build" --parallel 2
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer")
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --controls)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --composition)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --selection)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --checkbox)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --secure-field)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --search-field)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --collection-filters)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --slider)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --tabs)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --pagination)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --pagination-integers)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --accordion)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --presentation-states)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --spinner)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --alert)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --clipping)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --navigation)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --sidebar-brand)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --data-metrics)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --stepper)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --radio-group)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --otp-input)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --activity-item)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --modal)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --tooltip)
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --button-style)
format_report="$PWD/artifacts/linux/number-formatting.json"
set +e
(cd "$stage" && QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software "$stage/build/InstalledConsumer" --data-metrics --format-diagnostics "$format_report")
format_result=$?
set -e
if [[ "$format_result" != 0 && "$format_result" != 244 ]]; then exit "$format_result"; fi
cp scripts/check-installed-catalog.sh "$stage/check-installed-catalog.sh"
(cd "$stage" && bash check-installed-catalog.sh "$stage/catalog-evidence")
mkdir -p artifacts
# Always publish the already-verified fresh stage. Repeated cp into an existing
# directory nests the consumer and leaves obsolete source/install files behind.
if [[ -e artifacts/package ]]; then mv artifacts/package "$stage/previous-package"; fi
mkdir artifacts/package
cp -R "$stage/install" "$stage/consumer" artifacts/package/
cp scripts/check-installed.sh artifacts/package/check-installed.sh
cp scripts/check-installed-catalog.sh artifacts/package/check-installed-catalog.sh
if [[ -e artifacts/linux/catalog-installed ]]; then mv artifacts/linux/catalog-installed "$stage/previous-catalog-installed"; fi
cp -R "$stage/catalog-evidence" artifacts/linux/catalog-installed
cp scripts/check-display-sessions.sh artifacts/package/check-display-sessions.sh
cp artifacts/linux/environment.json artifacts/package/environment.json
mkdir -p artifacts/linux
QML_IMPORT_PATH="$PWD/build/linux/qml" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software build/linux/samples/AvelinoCatalog/AvelinoCatalog --capture artifacts/linux/actions-light.png
QML_IMPORT_PATH="$PWD/build/linux/qml" QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=software build/linux/samples/AvelinoCatalog/AvelinoCatalog --dark --capture artifacts/linux/actions-dark.png
for fixture in foundations surfaces data-display controls composition selection checkbox secure-field search-field collection-filters slider tabs pagination pagination-integers accordion presentation-states spinner alert clipping navigation sidebar-brand data-metrics stepper radio-group otp-input activity-item modal tooltip button-style; do
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
# Capture implemented APIs covered by the isolated native proposal definitions.
QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/desktop-20261012 \
  --output "$stage/proposals"
if [[ -e artifacts/linux/proposals ]]; then mv artifacts/linux/proposals "$stage/previous-proposals"; fi
mv "$stage/proposals" artifacts/linux/proposals
QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/composition-20261012-v1 \
  --output "$stage/composition-proposals"
if [[ -e artifacts/linux/composition-proposals ]]; then mv artifacts/linux/composition-proposals "$stage/previous-composition-proposals"; fi
mv "$stage/composition-proposals" artifacts/linux/composition-proposals
QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/selectors-20261013 \
  --output "$stage/selector-proposals"
if [[ -e artifacts/linux/selector-proposals ]]; then mv artifacts/linux/selector-proposals "$stage/previous-selector-proposals"; fi
mv "$stage/selector-proposals" artifacts/linux/selector-proposals
QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/checkbox-20261013 \
  --output "$stage/checkbox-proposals"
if [[ -e artifacts/linux/checkbox-proposals ]]; then mv artifacts/linux/checkbox-proposals "$stage/previous-checkbox-proposals"; fi
mv "$stage/checkbox-proposals" artifacts/linux/checkbox-proposals
QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/secure-field-20261014 \
  --output "$stage/secure-field-proposals"
if [[ -e artifacts/linux/secure-field-proposals ]]; then mv artifacts/linux/secure-field-proposals "$stage/previous-secure-field-proposals"; fi
mv "$stage/secure-field-proposals" artifacts/linux/secure-field-proposals
QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/search-field-20261014 \
  --output "$stage/search-field-proposals"
if [[ -e artifacts/linux/search-field-proposals ]]; then mv artifacts/linux/search-field-proposals "$stage/previous-search-field-proposals"; fi
mv "$stage/search-field-proposals" artifacts/linux/search-field-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/collection-filters-20261014 \
  --output "$stage/collection-filters-proposals"
if [[ -e artifacts/linux/collection-filters-proposals ]]; then mv artifacts/linux/collection-filters-proposals "$stage/previous-collection-filters-proposals"; fi
mv "$stage/collection-filters-proposals" artifacts/linux/collection-filters-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/slider-20261014-v2 \
  --output "$stage/slider-proposals"
if [[ -e artifacts/linux/slider-proposals ]]; then mv artifacts/linux/slider-proposals "$stage/previous-slider-proposals"; fi
mv "$stage/slider-proposals" artifacts/linux/slider-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/tabs-20261014 \
  --output "$stage/tabs-proposals"
if [[ -e artifacts/linux/tabs-proposals ]]; then mv artifacts/linux/tabs-proposals "$stage/previous-tabs-proposals"; fi
mv "$stage/tabs-proposals" artifacts/linux/tabs-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/pagination-20261014 \
  --output "$stage/pagination-proposals"
if [[ -e artifacts/linux/pagination-proposals ]]; then mv artifacts/linux/pagination-proposals "$stage/previous-pagination-proposals"; fi
mv "$stage/pagination-proposals" artifacts/linux/pagination-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/pagination-integers-20261014 \
  --output "$stage/pagination-integer-proposals"
if [[ -e artifacts/linux/pagination-integer-proposals ]]; then mv artifacts/linux/pagination-integer-proposals "$stage/previous-pagination-integer-proposals"; fi
mv "$stage/pagination-integer-proposals" artifacts/linux/pagination-integer-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/accordion-20261014 \
  --output "$stage/accordion-proposals"
if [[ -e artifacts/linux/accordion-proposals ]]; then mv artifacts/linux/accordion-proposals "$stage/previous-accordion-proposals"; fi
mv "$stage/accordion-proposals" artifacts/linux/accordion-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/presentation-states-20261015-v2 \
  --output "$stage/presentation-state-proposals"
if [[ -e artifacts/linux/presentation-state-proposals ]]; then mv artifacts/linux/presentation-state-proposals "$stage/previous-presentation-state-proposals"; fi
mv "$stage/presentation-state-proposals" artifacts/linux/presentation-state-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/alert-20261015 \
  --output "$stage/alert-proposals"
if [[ -e artifacts/linux/alert-proposals ]]; then mv artifacts/linux/alert-proposals "$stage/previous-alert-proposals"; fi
mv "$stage/alert-proposals" artifacts/linux/alert-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/navigation-layout-20261015 \
  --output "$stage/navigation-proposals"
if [[ -e artifacts/linux/navigation-proposals ]]; then mv artifacts/linux/navigation-proposals "$stage/previous-navigation-proposals"; fi
mv "$stage/navigation-proposals" artifacts/linux/navigation-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/sidebar-brand-20261015 \
  --output "$stage/sidebar-brand-proposals"
if [[ -e artifacts/linux/sidebar-brand-proposals ]]; then mv artifacts/linux/sidebar-brand-proposals "$stage/previous-sidebar-brand-proposals"; fi
mv "$stage/sidebar-brand-proposals" artifacts/linux/sidebar-brand-proposals

QML_IMPORT_PATH="$PWD/build/linux/qml" python3 scripts/capture-proposals.py \
  --catalog build/linux/samples/AvelinoCatalog/AvelinoCatalog \
  --reference evidence/reference-proposals/data-metrics-20261015 \
  --output "$stage/data-metrics-proposals"
if [[ -e artifacts/linux/data-metrics-proposals ]]; then mv artifacts/linux/data-metrics-proposals "$stage/previous-data-metrics-proposals"; fi
mv "$stage/data-metrics-proposals" artifacts/linux/data-metrics-proposals

# Hosted source investigations use the installed catalog and keep failed
# attempts outside the disposable stage. Existing baselines are not updated.
stepper_attempt="$(mktemp -d "$PWD/artifacts/linux/stepper-attempt.XXXXXX")"
python3 scripts/capture-stepper-cases.py \
  "$stage/install/bin/AvelinoCatalog" "$stepper_attempt/captures"
if [[ -e artifacts/linux/stepper-source-candidates ]]; then mv artifacts/linux/stepper-source-candidates "$stage/previous-stepper-candidates"; fi
mv "$stepper_attempt/captures" artifacts/linux/stepper-source-candidates
rmdir "$stepper_attempt"

radio_attempt="$(mktemp -d "$PWD/artifacts/linux/radio-attempt.XXXXXX")"
python3 scripts/capture-radio-cases.py \
  "$stage/install/bin/AvelinoCatalog" "$radio_attempt/captures"
if [[ -e artifacts/linux/radio-source-candidates ]]; then mv artifacts/linux/radio-source-candidates "$stage/previous-radio-candidates"; fi
mv "$radio_attempt/captures" artifacts/linux/radio-source-candidates
rmdir "$radio_attempt"

otp_attempt="$(mktemp -d "$PWD/artifacts/linux/otp-attempt.XXXXXX")"
python3 scripts/capture-otp-cases.py \
  "$stage/install/bin/AvelinoCatalog" "$otp_attempt/captures"
if [[ -e artifacts/linux/otp-source-candidates ]]; then mv artifacts/linux/otp-source-candidates "$stage/previous-otp-candidates"; fi
mv "$otp_attempt/captures" artifacts/linux/otp-source-candidates
rmdir "$otp_attempt"

activity_attempt="$(mktemp -d "$PWD/artifacts/linux/activity-attempt.XXXXXX")"
python3 scripts/capture-activity-cases.py \
  "$stage/install/bin/AvelinoCatalog" "$activity_attempt/captures"
if [[ -e artifacts/linux/activity-source-candidates ]]; then mv artifacts/linux/activity-source-candidates "$stage/previous-activity-candidates"; fi
mv "$activity_attempt/captures" artifacts/linux/activity-source-candidates
rmdir "$activity_attempt"

modal_attempt="$(mktemp -d "$PWD/artifacts/linux/modal-attempt.XXXXXX")"
python3 scripts/capture-modal-cases.py \
  "$stage/install/bin/AvelinoCatalog" "$modal_attempt/captures"
if [[ -e artifacts/linux/modal-source-candidates ]]; then mv artifacts/linux/modal-source-candidates "$stage/previous-modal-candidates"; fi
mv "$modal_attempt/captures" artifacts/linux/modal-source-candidates
rmdir "$modal_attempt"

tooltip_attempt="$(mktemp -d "$PWD/artifacts/linux/tooltip-attempt.XXXXXX")"
python3 scripts/capture-tooltip-cases.py \
  "$stage/install/bin/AvelinoCatalog" "$tooltip_attempt/captures"
if [[ -e artifacts/linux/tooltip-source-candidates ]]; then mv artifacts/linux/tooltip-source-candidates "$stage/previous-tooltip-candidates"; fi
mv "$tooltip_attempt/captures" artifacts/linux/tooltip-source-candidates
rmdir "$tooltip_attempt"

button_style_attempt="$(mktemp -d "$PWD/artifacts/linux/button-style-attempt.XXXXXX")"
python3 scripts/capture-button-style-cases.py \
  "$stage/install/bin/AvelinoCatalog" "$button_style_attempt/captures"
if [[ -e artifacts/linux/button-style-source-candidates ]]; then mv artifacts/linux/button-style-source-candidates "$stage/previous-button-style-candidates"; fi
mv "$button_style_attempt/captures" artifacts/linux/button-style-source-candidates
rmdir "$button_style_attempt"
