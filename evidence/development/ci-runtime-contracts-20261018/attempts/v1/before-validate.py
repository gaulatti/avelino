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
    assert record['asyncShapeFrameChecks'] == 'passed', record
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
elif fixture in ['surface-baseline','surface-input']:
    assert record['structuralChecks']=='passed' and record['accepted'] is False,record
    assert record['nativeComparisonStatus'] in ['passed','failed'],record
    assert len(record['rows'])==(55 if fixture=='surface-baseline' else 36),record
    assert record['physicalInputAcceptance']==record['readerAcceptance']==record['rasterAcceptance']=='pending',record
elif fixture == 'command-spotlight':
    assert record['structuralChecks']=='passed' and record['accepted'] is False,record
    assert len(record['closed'])==32 and len(record['histories'])==8 and len(record['sizing'])==32 and record['images']==224,record
    assert record['pointerDeliveries']==40 and record['keyDeliveries']==8,record
    assert all(len(h['steps'])==24 for h in record['histories']),record
    assert record['retainedRestores']==sum(h['steps'][22]['matchesInitialPixels'] for h in record['histories']),record
    assert record['nativeRasterAcceptance']==record['physicalInputAcceptance']==record['readerAcceptance']=='pending',record
    assert record['nativeAccessibilityAcceptance']=='unobserved',record
elif fixture == 'file-input':
    assert record['structuralChecks']=='passed' and record['accepted'] is False,record
    assert len(record['closed'])==len(record['sizing'])==32 and record['images']==44,record
    assert record['nativeContractStatesMatch']==32 and len(record['actions'])==24,record
    assert record['pointerEvents']==54 and record['keyEvents']==40,record
    assert record['nativeRasterAcceptance']==record['physicalInputAcceptance']==record['readerAcceptance']=='pending',record
    assert record['nativeAccessibilityAcceptance']=='unobserved',record
elif fixture == 'dropdown-menu':
    assert record['structuralChecks']=='passed' and record['accepted'] is False,record
    assert len(record['closed'])==len(record['sizing'])==record['images']==32,record
    assert record['pointerDeliveries']==11 and record['keyDeliveries']==1 and len(record['actions'])==6,record
    assert record['nativeRasterAcceptance']==record['physicalInputAcceptance']==record['readerAcceptance']=='pending',record
    assert record['nativeAccessibilityAcceptance']=='unobserved',record
elif fixture == 'app-tabs':
    assert record['structuralChecks']=='passed' and record['accepted'] is False,record
    assert len(record['closed'])==43 and len(record['histories'])==6 and len(record['sizing'])==43 and record['images']==151,record
    assert record['pointerDeliveries']==24 and record['stateMatches']==151 and record['qtButtonInterfaces']>0,record
    assert all(len(h['steps'])==18 for h in record['histories']),record
    assert record['retainedRestores']==sum(h['steps'][16]['matchesInitialPixels'] for h in record['histories']),record
    assert record['nativeRasterAcceptance']==record['physicalInputAcceptance']==record['readerAcceptance']=='pending',record
    assert record['nativeAccessibilityAcceptance']=='unobserved',record
elif fixture == 'media-library':
    assert record['structuralChecks']=='passed' and record['accepted'] is False,record
    assert len(record['closed'])==62 and len(record['edges'])==14 and len(record['histories'])==6 and record['images']==201,record
    assert record['geometryObservations']==201 and record['pointerDeliveries']==12 and len(record['sizing'])==62,record
    assert record['nativeGeometryComparisonStatus'] in ['passed','failed'],record
    assert record['nativeRasterAcceptance']==record['physicalInputAcceptance']==record['readerAcceptance']=='pending',record
    assert all(len(h['steps'])==21 and isinstance(h['steps'][13]['matchesInitialPixels'],bool) for h in record['histories']),record
    assert record['retainedRestorePixelMatches']==sum(h['steps'][13]['matchesInitialPixels'] for h in record['histories']),record
    assert record['retainedRestoreRasterStatus']==('passed' if record['retainedRestorePixelMatches']==6 else 'failed'),record
elif fixture == 'charts':
    assert record['structuralChecks']=='passed' and record['accepted'] is False,record
    assert len(record['closed'])==120 and len(record['edges'])==50 and len(record['histories'])==6 and record['images']==218,record
    assert record['nativeGeometryComparisonStatus'] in ['passed','failed'],record
    assert record['inputContexts']==10 and record['qtAccessibilityChecks'].startswith('passed') and record['inputChecks'].startswith('passed'),record
    assert record['nativeRasterAcceptance']==record['physicalInputAcceptance']==record['readerAcceptance']=='pending',record
    assert all(len(h['steps'])==8 and h['steps'][-1]['restoredInitialPixelsAndGeometry'] for h in record['histories']),record
elif fixture == 'pill-modifier':
    assert record['structuralChecks']=='passed' and record['accepted'] is False,record
    assert len(record['rows'])==111 and len(record['histories'])==7 and record['measurements']==264,record
    assert record['nativeComparisonStatus'] in ['passed','failed'],record
    assert record['nativeRasterAcceptance']==record['physicalInputAcceptance']==record['readerAcceptance']=='pending',record
    assert all(len(h['steps'])==6 and h['steps'][-1]['restoredInitialPixelsAndGeometry'] for h in record['histories']),record
elif fixture == 'surface-modifier':
    for key in ['surfaceModifierChecks','callerStateChecks','focusChecks','qtAccessibilityChecks','liveRadiusPaintChecks','asyncShapeFrameChecks']:assert record[key]=='passed',record
    assert record['flatParts']==2 and record['stackParts']==1 and record['activations']==3 and record['accepted'] is False,record
    assert record['closedContextCount']==52 and len(record['closedContexts'])==52 and record['requestedBaselineContexts']==0,record
    assert len(record['retainedHistories'])==5 and all(len(h['steps'])==6 and h['restoredPixelsIdentical'] for h in record['retainedHistories']),record
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
    'nativePointerControl': 'parked outside clients and nested compositor; consumer pointer input is synthetic Qt input',
    'nativePointerRecord': 'native-pointer.txt',
    'sessionOutputSize': list(session_size),
    'clientOutputSize': list(client_output),
    'sessionCapture': Path(prefix+'-session.png').name,
    'sessionCaptureSha256': hashlib.sha256(Path(prefix+'-session.png').read_bytes()).hexdigest(),
    'windowCaptureSha256': hashlib.sha256(Path(prefix+'.png').read_bytes()).hexdigest(),
})
path.write_text(json.dumps(record, indent=2)+'\n')
