#!/usr/bin/env bash
set -euo pipefail
# Execute in the installed-package-only container after check-installed.sh.
evidence="${1:-$PWD/display-evidence}"
# Refuse stale readiness markers or capture overwrites from an earlier run.
mkdir "$evidence"
cp environment.json "$evidence/environment.json"
runtime="$(mktemp -d)"
chmod 700 "$runtime"
export XDG_RUNTIME_DIR="$runtime"
export LIBGL_ALWAYS_SOFTWARE=1
export QSG_INFO=1
xpid= wpid= client=
cleanup() {
  for pid in "$client" "$wpid" "$xpid"; do
    if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; fi
  done
  rm -rf "$runtime"
}
trap cleanup EXIT
# Keep the largest gallery (1100 x 850 logical units) within the output at DPR 2.
Xvfb -displayfd 3 -screen 0 2560x1920x24 -nolisten tcp 3>"$runtime/display" >"$evidence/xvfb.log" 2>&1 &
xpid=$!
for ((i=0;i<100;i++)); do
  if [[ -s "$runtime/display" ]]; then break; fi
  kill -0 "$xpid"
  sleep 0.1
done
export DISPLAY=":$(cat "$runtime/display")"
xdpyinfo >"$evidence/x11-server.txt"
weston --version >"$evidence/weston-version.txt"
import -version >"$evidence/capture-tool-version.txt"
for protocol in xcb wayland; do
  if [[ "$protocol" == wayland ]]; then
    cat >"$runtime/weston.ini" <<'INI'
[shell]
panel-position=none
background-color=0xffdbe1e7
locking=false
INI
    weston --backend=x11 --renderer=pixman --width=2400 --height=1800 --socket=avelino-wayland \
      --idle-time=0 --config="$runtime/weston.ini" --log="$evidence/weston.log" >"$evidence/weston-client.log" 2>&1 &
    wpid=$!
    for ((i=0;i<100;i++)); do
      if [[ -S "$runtime/avelino-wayland" ]]; then break; fi
      kill -0 "$wpid"
      sleep 0.1
    done
    [[ -S "$runtime/avelino-wayland" ]]
    export WAYLAND_DISPLAY=avelino-wayland
  fi
  for backend in software opengl; do
    for configuration in standard scaled; do
    for fixture in font-modifier; do
      prefix="$evidence/$protocol-$backend-$configuration"
      if [[ "$fixture" == controls ]]; then prefix="$evidence/controls-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == composition ]]; then prefix="$evidence/composition-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == checkbox ]]; then prefix="$evidence/checkbox-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == secure-field ]]; then prefix="$evidence/secure-field-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == search-field ]]; then prefix="$evidence/search-field-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == selection ]]; then prefix="$evidence/selection-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == collection-filters ]]; then prefix="$evidence/collection-filters-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == slider ]]; then prefix="$evidence/slider-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == tabs ]]; then prefix="$evidence/tabs-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == pagination ]]; then prefix="$evidence/pagination-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == pagination-integers ]]; then prefix="$evidence/pagination-integers-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == modal ]]; then prefix="$evidence/modal-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == tooltip ]]; then prefix="$evidence/tooltip-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == font-modifier ]]; then prefix="$evidence/font-modifier-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == button-style ]]; then prefix="$evidence/button-style-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == activity-item ]]; then prefix="$evidence/activity-item-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == otp-input ]]; then prefix="$evidence/otp-input-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == radio-group ]]; then prefix="$evidence/radio-group-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == stepper ]]; then prefix="$evidence/stepper-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == data-metrics ]]; then prefix="$evidence/data-metrics-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == sidebar-brand ]]; then prefix="$evidence/sidebar-brand-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == navigation ]]; then prefix="$evidence/navigation-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == clipping ]]; then prefix="$evidence/clipping-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == alert ]]; then prefix="$evidence/alert-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == spinner ]]; then prefix="$evidence/spinner-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == presentation-states ]]; then prefix="$evidence/presentation-states-$protocol-$backend-$configuration"; fi
      if [[ "$fixture" == accordion ]]; then prefix="$evidence/accordion-$protocol-$backend-$configuration"; fi
      args=(--evidence "$prefix")
      if [[ "$fixture" == controls ]]; then args+=(--controls); fi
      if [[ "$fixture" == composition ]]; then args+=(--composition); fi
      if [[ "$fixture" == checkbox ]]; then args+=(--checkbox); fi
      if [[ "$fixture" == secure-field ]]; then args+=(--secure-field); fi
      if [[ "$fixture" == search-field ]]; then args+=(--search-field); fi
      if [[ "$fixture" == selection ]]; then args+=(--selection); fi
      if [[ "$fixture" == collection-filters ]]; then args+=(--collection-filters); fi
      if [[ "$fixture" == slider ]]; then args+=(--slider); fi
      if [[ "$fixture" == tabs ]]; then args+=(--tabs); fi
      if [[ "$fixture" == pagination ]]; then args+=(--pagination); fi
      if [[ "$fixture" == pagination-integers ]]; then args+=(--pagination-integers); fi
      if [[ "$fixture" == modal ]]; then args+=(--modal); fi
      if [[ "$fixture" == tooltip ]]; then args+=(--tooltip); fi
      if [[ "$fixture" == font-modifier ]]; then args+=(--font-modifier); fi
      if [[ "$fixture" == button-style ]]; then args+=(--button-style); fi
      if [[ "$fixture" == activity-item ]]; then args+=(--activity-item); fi
      if [[ "$fixture" == otp-input ]]; then args+=(--otp-input); fi
      if [[ "$fixture" == radio-group ]]; then args+=(--radio-group); fi
      if [[ "$fixture" == stepper ]]; then args+=(--stepper); fi
      if [[ "$fixture" == data-metrics ]]; then args+=(--data-metrics); fi
      if [[ "$fixture" == sidebar-brand ]]; then args+=(--sidebar-brand); fi
      if [[ "$fixture" == navigation ]]; then args+=(--navigation); fi
      if [[ "$fixture" == clipping ]]; then args+=(--clipping); fi
      if [[ "$fixture" == alert ]]; then args+=(--alert); fi
      if [[ "$fixture" == spinner ]]; then args+=(--spinner); fi
      if [[ "$fixture" == presentation-states ]]; then args+=(--presentation-states); fi
      if [[ "$fixture" == accordion ]]; then args+=(--accordion); fi
      export QT_SCALE_FACTOR=1
      if [[ "$configuration" == scaled ]]; then
        export QT_SCALE_FACTOR=2
        args+=(--dark --text-scale 1.5)
      fi
      if [[ "$backend" == software ]]; then
        export QT_QUICK_BACKEND=software
        unset QSG_RHI_BACKEND
      else
        unset QT_QUICK_BACKEND
        export QSG_RHI_BACKEND=opengl
      fi
      QT_QPA_PLATFORM="$protocol" consumer-build/InstalledConsumer "${args[@]}" >"$prefix.log" 2>&1 &
      client=$!
      # Each consumer owns its bounded runtime assertions. Observing it for a
      # fixed number of polls must not terminate a still-running replay.
      readiness_started=$SECONDS
      readiness_notice=$((SECONDS+30))
      while [[ ! -f "$prefix.json" ]]; do
        if ! kill -0 "$client" 2>/dev/null; then
          result=0
          wait "$client" || result=$?
          client=
          cat "$prefix.log" >&2
          echo "Installed consumer exited with status $result before producing session evidence: $prefix" >&2
          exit 1
        fi
        if ((SECONDS>=readiness_notice)); then
          echo "Waiting for session evidence after $((SECONDS-readiness_started))s: $prefix (live consumer $client)" >&2
          readiness_notice=$((SECONDS+30))
        fi
        sleep 0.1
      done
      # Capture the entire displayed output, including independent surfaces.
      # Wayland surfaces are composited by Weston into this X11 output.
      import -window root "$prefix-session.png"
      python3 - "$prefix" "$protocol" "$backend" "$configuration" "$fixture" <<'PY'
import hashlib, json, math, struct, sys
from pathlib import Path
prefix, protocol, backend, configuration, fixture = sys.argv[1:]
path = Path(prefix+'.json')
record = json.loads(path.read_text())
assert record['platform'] == protocol, record
assert record['graphicsApi'] == (1 if backend == 'software' else 3), record
assert record['fixture'] == fixture, record
if fixture == 'base':
    assert record['buttonSurfaceRendererType'] == (3 if backend == 'software' else 4), record
    assert record['buttonSurfaceRadius'] == 7 and record['buttonSurfaceOuterPath'], record
    assert record['paintPlacementChecks'] == 'passed', record
    for key in ['buttonSurfaceX', 'buttonSurfaceY', 'buttonLabelBaselineX', 'buttonLabelBaselineY']:
        physical = record[key] * record['dpr']
        assert math.isfinite(physical) and abs(physical - round(physical)) <= 0.00001, (key, physical)
    assert record['fractionalButtonGlyphPixels'] == 13 * record['textScale'], record
    assert record['sourceFontMetricChecks'] == 'passed', record
    assert record['resolvedFractionalFontPixels'] == (13 if configuration == 'standard' else 20), record
    assert record['fractionalFontLineHeight'] == (16 if configuration == 'standard' else 25), record
    assert record['fractionalFontBaseline'] == (13 if configuration == 'standard' else 21), record
    assert record['foundationChecks'] == 'passed' and record['groupKeyboardChecks'] == 'passed', record
    assert record['cardBadgeChecks'] == 'passed', record
    assert record['dataDisplayChecks'] == 'passed' and record['dataListInputChecks'] == 'passed', record
    assert record['roundedContentClipping'] is True, record
elif fixture == 'controls':
    assert record['controlsChecks'] == 'passed' and record['focusRestorationChecks'] == 'passed', record
    assert 0 < record['scrollbarSize'] < 1 and record['textareaContentHeight'] > 100, record
elif fixture == 'composition':
    assert record['compositionChecks'] == 'passed' and record['focusResizeChecks'] == 'passed', record
    assert record['gridColumns'] == 2 and record['tileWidth'] == 251.5, record
elif fixture == 'checkbox':
    assert record['checkboxChecks'] == 'passed' and record['focusChecks'] == 'passed', record
    assert record['qtAccessibilityChecks'] == 'passed' and record['checkedValue'] is True, record
    assert record['changes'] == 2 and record['wrappedLabelHeight'] > 18, record
    assert record['wrappedLabelHeight'] == record['wrappedControlHeight'], record
elif fixture == 'secure-field':
    for key in ['secureFieldChecks','maskingChecks','clipboardChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key] == 'passed', record
    assert record['sourceHeight'] == 40 and record['fontPointSize'] == 10.5, record
    assert record['revealed'] is True, record
elif fixture == 'font-modifier':
    for key in ['fontModifierChecks','callerStateChecks','liveFontPaintChecks','focusChecks','qtAccessibilityChecks']:assert record[key]=='passed',record
    assert record['closedContextCount']==207 and len(record['closedContexts'])==207,record
    assert record['accepted'] is False and len(record['retainedUpdates'])==3,record
elif fixture == 'button-style':
    for key in ['buttonStyleChecks','callerStateChecks','focusChecks','qtAccessibilityChecks']:assert record[key]=='passed',record
    assert record['liveCurvePaintChecks']=='passed',record
    assert record['closedContextCount']==88 and len(record['closedContexts'])==88,record
    assert record['exactFrameSets']==85 and len(record['unresolvedSourceContexts'])==3,record
    assert record['pointerPhases']==13 and len(record['nativeTraces'])==2,record
    assert record['sharedHeldPixelsIdentical'] and record['accepted'] is False,record
elif fixture == 'tooltip':
    for key in ['tooltipChecks','focusChecks','qtAccessibilityChecks']:assert record[key]=='passed',record
    assert record['closedBodyIdentical'] and record['shownHintPixelsIdentical'],record
    assert record['separateTooltipWindow'] and record['tooltipWindowType']==13,record
    assert record['popupText']=='q' and record['delay']==0 and record['timeout']==-1,record
    popup=Path(prefix+'-tooltip.png')
    assert struct.unpack('>II',popup.read_bytes()[16:24])==(record['tooltipWidth']*record['dpr'],record['tooltipHeight']*record['dpr']),record
    shown=Path(prefix+'-native-default-tooltip.png');updated=Path(prefix+'-updated-hint-tooltip.png')
    assert shown.read_bytes()==updated.read_bytes(),record
    assert struct.unpack('>II',shown.read_bytes()[16:24])==(record['defaultTooltipPhysicalWidth'],record['defaultTooltipPhysicalHeight']),record
elif fixture == 'modal':
    for key in ['modalChecks','callerStateChecks','focusChecks','qtAccessibilityChecks','qtEditorChecks']:assert record[key]=='passed',record
    assert record['qtEditedAndReopenedValue']=='q' and record['nativeTypingAcceptance']=='pending',record
    assert record['nativeSnapshots']==80 and len(record['nativeTraces'])==17 and record['accepted'] is False,record
    assert record['clippingQueries']==170 and record['glyphQueries']==142,record
    assert record['peakSourceWindows']<=3,record
    assert record['separatePresentationWindow'] is True and record['popupWidth']==480,record
    popup=Path(prefix+'-popup.png')
    assert popup.is_file() and struct.unpack('>II',popup.read_bytes()[16:24])==(record['popupWidth']*record['dpr'],record['popupHeight']*record['dpr']),record
elif fixture == 'activity-item':
    for key in ['activityChecks','callerStateChecks','focusChecks','qtAccessibilityChecks']:assert record[key]=='passed',record
    assert record['nativeSnapshots']==94 and len(record['nativeTraces'])==13 and record['accepted'] is False,record
    assert record['producerFramesAwaited']>=len(record['nativeTraces']),record
elif fixture == 'otp-input':
    for key in ['otpChecks','callerBindingChecks','focusChecks','qtAccessibilityChecks']:assert record[key]=='passed',record
    assert record['nativeModelEditorSnapshots']==200 and len(record['nativeTraces'])==19 and record['accepted'] is False,record
elif fixture == 'radio-group':
    for key in ['radioChecks','callerBindingChecks','focusChecks','qtAccessibilityChecks']:assert record[key]=='passed',record
    assert len(record['nativeBehaviorTraces'])==24 and len(record['nativePointerPhaseTraces'])==11 and record['matchingNativeStringPairs']==13762,record
elif fixture == 'stepper':
    for key in ['stepperChecks','callerBindingChecks','focusChecks','qtAccessibilityChecks']:assert record[key]=='passed',record
    assert len(record['nativeBehaviorTraces'])==25 and record['matchingNativeIntegerFormatterWitnesses']==126,record
elif fixture == 'data-metrics':
    for key in ['dataMetricsChecks','focusChecks','qtAccessibilityChecks']:assert record[key]=='passed',record
    assert record['updates']==1 and record['formattedValue']=='12.345679%' and record['deltaLocale']=='de_DE',record
elif fixture == 'sidebar-brand':
    for key in ['sidebarBrandChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key]=='passed',record
    assert record['requests']==4 and record['callerSelection']=='editions' and record['logoSize']==64.5,record
    assert record['pinnedAssetSha256']=='3eadafd84a1f3b37261bad85b8a8e5512ed7aa9b3baae38aa8321cc3a6cbb9c2',record
elif fixture == 'navigation':
    for key in ['navigationChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key]=='passed',record
    assert (record['mounts'],record['unmounts'])==(3,2) and record['requests']==[2,2,2,0],record
    assert record['narrowHeight']==60 and record['narrowWidth']==(140 if record['dpr']<2 else 138.5),record
    assert record['rtlVisualOrder']=='logical first at right' and record['modelRestoredForCapture'] is True,record
elif fixture == 'clipping':
    for key in ['clippingChecks','layerLifecycleChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key]=='passed',record
    assert record['actions']==3 and record['outlineKinds']==3 and record['roundedContentClipping'] is True,record
elif fixture == 'alert':
    for key in ['alertChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key]=='passed',record
    assert (record['mounts'],record['unmounts'],record['actions'],record['counter'])==(3,2,4,0),record
    assert record['narrowWidth']<=180 and record['roundedContentClipping'] is True,record
elif fixture == 'spinner':
    for key in ['spinnerChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key]=='passed',record
    assert (record['smallEdge'],record['mediumEdge'],record['largeEdge'])==(16,32,32),record
    assert record['frameCount']==24 and record['cycleMilliseconds']==800 and record['actions']==3,record
    assert record['sourceAnimationAcceptance'].startswith('pending;'),record
elif fixture == 'presentation-states':
    for key in ['presentationChecks','focusChecks','qtAccessibilityChecks','overlayPointerChecks']:
        assert record[key] == 'passed', record
    assert record['created'] == 2 and record['destroyed'] == 1 and record['actions'] == 4, record
    assert record['underlying'] == 2 and record['outside'] == 1, record
    assert record['roundedContentClipping'] is True, record
elif fixture == 'accordion':
    for key in ['accordionChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key] == 'passed', record
    assert record['created'] == 3 and record['destroyed'] == 2 and record['actions'] == 1 and record['expanded'] is True, record
    assert record['narrowHeight'] == 104, record
elif fixture == 'pagination-integers':
    for key in ['paginationIntegerChecks','callerBindingChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key] == 'passed', record
    assert record['exactPage'] == '9223372036854775806' and record['requests'] == 4, record
    assert record['wrappedBodyWidth'] == (260 if record['dpr'] == 1 else 259.5) and record['wrappedBodyHeight'] == 45, record
elif fixture == 'pagination':
    for key in ['paginationChecks','callerBindingChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key] == 'passed', record
    assert record['page'] == 4 and record['requests'] == 7, record
elif fixture == 'tabs':
    for key in ['tabsChecks','callerBindingChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key] == 'passed', record
    assert record['selectedValue'] == 'c' and record['activations'] == 4, record
elif fixture == 'slider':
    for key in ['sliderChecks','callerBindingChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key] == 'passed', record
    assert record['sourceHeight'] == 16, record
    assert record['sourceKeyboardAcceptance'].startswith('pending;'), record
elif fixture == 'collection-filters':
    for key in ['collectionFilterChecks','callerBindingChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key] == 'passed', record
    assert record['sourceHeight'] == 40*record['textScale'] and record['wrappedChipHeight'] == 45, record
    assert record['roundedContentClipping'] is True, record
elif fixture == 'search-field':
    for key in ['searchFieldChecks','clearBindingChecks','focusChecks','qtAccessibilityChecks']:
        assert record[key] == 'passed', record
    assert record['sourceHeight'] == 40*record['textScale'], record
    assert record['leadingWidth'] == 16.5 and record['clearWidth'] == 18.5, record
else:
    assert record['fixture'] == 'selection' and record['selectionChecks'] == 'passed', record
    assert record['focusRestorationChecks'] == 'passed' and record['popupVisible'] is True, record
    assert record['popupType'] == 0 and record['popupHeight'] == 314 and record['selectedValue'] == 38, record
    assert record['disabledRowVisible'] is True, record
    assert 0 < record['scrollbarSize'] < 1, record
    assert record['popupContentX'] >= 0 and record['popupContentY'] >= 0, record
    assert record['popupContentX'] + record['popupContentWidth'] <= record['width'], record
    assert record['popupContentY'] + record['popupContentHeight'] <= record['height'], record
assert record['dpr'] == (1 if configuration == 'standard' else 2), record
assert record['textScale'] == (1 if configuration == 'standard' else 1.5), record
assert record['appearance'] == ('light' if configuration == 'standard' else 'dark'), record
window_bytes = Path(prefix+'.png').read_bytes()
assert window_bytes[:8] == b'\x89PNG\r\n\x1a\n'
physical = struct.unpack('>II', window_bytes[16:24])
assert physical == (record['width']*record['dpr'], record['height']*record['dpr']), record
session_bytes = Path(prefix+'-session.png').read_bytes()
session_size = struct.unpack('>II', session_bytes[16:24])
assert session_size == (2560, 1920), session_size
client_output = (2560, 1920) if protocol == 'xcb' else (2400, 1800)
# Reserve room for native window decorations as well as the complete client.
assert physical[0] + 40 <= client_output[0] and physical[1] + 60 <= client_output[1], (physical, client_output)
record.update({
    'environmentRecord': 'environment.json',
    'session': 'Xvfb X11' if protocol == 'xcb' else 'Weston Wayland nested on Xvfb X11',
    'sessionCaptureMethod': 'ImageMagick import -window root (full X11 output)',
    'physicalDisplay': False,
    'hardwareAcceleration': False,
    'sessionOutputSize': list(session_size),
    'clientOutputSize': list(client_output),
    'sessionCapture': Path(prefix+'-session.png').name,
    'sessionCaptureSha256': hashlib.sha256(Path(prefix+'-session.png').read_bytes()).hexdigest(),
    'windowCaptureSha256': hashlib.sha256(Path(prefix+'.png').read_bytes()).hexdigest(),
})
path.write_text(json.dumps(record, indent=2)+'\n')
PY
      touch "$prefix.captured"
      wait "$client"
      client=
    done
    done
  done
done
echo 'Installed consumer exercised X11 and nested Wayland with software and OpenGL renderers; mirror, overlays, physical input and accessibility remain pending.'
