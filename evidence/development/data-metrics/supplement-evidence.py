import hashlib,json,re,shutil
from pathlib import Path

root=Path('evidence/development/data-metrics')
work=Path('artifacts/resumed-avelino-20261016')
frozen=json.loads((root/'frozen-inputs.json').read_text())
files=sorted([Path('CMakeLists.txt'),Path('CMakePresets.json')]+
    [p for folder in ['src','samples','assets','tokens','tests','scripts','cmake','tools','evidence/geometry']
     for p in Path(folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts])
current={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
assert all(current[name]==digest for name,digest in frozen.items())
extra={name:digest for name,digest in current.items() if name not in frozen}
assert set(extra)=={'tests/components/tst_action_text.qml'}
native=root/'native-action-text.json'
rows=json.loads(native.read_text())
expected=[{'text':v['text'],'dpr':v['dpr'],'proposal':v['proposal'],
    'rect':{'width':v['rect']['width'],'height':v['rect']['height']}} for v in rows if not v['numeric']]
fixture=Path('tests/components/tst_action_text.qml');text=fixture.read_text()
start=text.index('readonly property var nativeRows: ')+len('readonly property var nativeRows: ')
end=text.index('\n    PixelAlignment',start)
assert json.loads(text[start:end])==expected and len(expected)==64
assert hashlib.sha256(native.read_bytes()).hexdigest() in text
base=(root/'qt-tests.log').read_text();latest=(work/'qt-tests-with-action.log').read_text()
totals=lambda s:[int(x) for x in re.findall(r'Totals: (\d+) passed, 0 failed',s)]
assert len(totals(base))==len(totals(latest))==2
assert sum(totals(latest))-sum(totals(base))==70
assert 'NativeActionText::test_narrow_action' in latest
shutil.copy2(work/'qt-tests-with-action.log',root/'supplemental-qt-tests.log')
shutil.copy2(work/'action-regression-full-ctest.log',root/'supplemental-ctest.log')
shutil.copy2(fixture,root/'tst_action_text.qml')
value={'capturedSourceInputs':len(frozen),'unchangedCapturedInputs':len(frozen),
    'additionalTestInputs':extra,'currentTestInputs':len(current),'currentInputSnapshot':current,
    'nativeOracleSha256':hashlib.sha256(native.read_bytes()).hexdigest(),
    'nativeOracleRows':len(expected),'oracleMatchesSealedNativeEvidence':True,
    'originalQtChecks':sum(totals(base)),'currentQtChecks':sum(totals(latest)),
    'additionalQtChecks':70,'ctestTargetsPassed':8,
    'scope':'Only a regression fixture was added after capture; all 293 recorded capture/build inputs and product binaries were preserved. The full Qt suite was rerun with this fixture.'}
(root/'supplemental-test-inputs.json').write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
p=root/'verification-summary.json';summary=json.loads(p.read_text());summary.update(
    qtChecks=value['currentQtChecks'],originalQtChecks=value['originalQtChecks'],
    supplementalQtChecks=70,supplementalTestInputs=1,currentTestInputs=len(current),
    qtTestLog='supplemental-qt-tests.log')
p.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print('Verified all',len(frozen),'capture inputs unchanged; one added fixture passes 70 Qt checks')
