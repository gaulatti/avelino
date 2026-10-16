import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

Item {
    id:root;width:760;height:560
    T.TextField {id:outside;x:500;y:450;width:200;height:40}
    TestCase {
        id:testCase;name:"OTPInput";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
        Component {
            id:factory
            BleeckerOTPInput {
                x:50;y:30
                property bool observeOnly:false
                property bool deferredOwner:false
                property bool manualDeferred:false
                property bool publishesWrites:false
                property var pendingWrites:[]
                property var requests:[]
                code:""
                onCodeRequested:value=>{
                    requests=requests.concat([value])
                    if(observeOnly)return
                    if(deferredOwner && manualDeferred)pendingWrites=pendingWrites.concat([value])
                    else if(deferredOwner)Qt.callLater(function(){code=value;if(publishesWrites)notifyCodeWrite()})
                    else {code=value;if(publishesWrites)notifyCodeWrite()}
                }
                function flushWrites(){const values=pendingWrites;pendingWrites=[];for(const value of values){code=value;if(publishesWrites)notifyCodeWrite()}}
            }
        }
        function create(properties){const otp=createTemporaryObject(factory,root,properties || {});verify(otp);waitForPolish(otp);return otp}
        function focusEditor(otp){otp.editor.forceActiveFocus(Qt.OtherFocusReason);tryCompare(otp.editor,"activeFocus",true)}
        function replace(otp,text){otp.editor.selectAll();fixtureSetup.commitText(otp.editor,text);wait(1)}
        function blur(otp){outside.forceActiveFocus();tryCompare(otp.editor,"activeFocus",false)}
        function test_initialGetterAndLength() {
            const otp=create({code:"A123456789",length:0})
            compare(otp.code,"A123456789");compare(otp.editor.text,otp.code);compare(otp.requests.length,0);compare(otp.placeholder,"")
            otp.length=2;compare(otp.editor.text,"A123456789");compare(otp.placeholder,"••");compare(otp.requests.length,0)
            otp.code="X987654321";compare(otp.editor.text,otp.code)
            focusEditor(otp);compare(otp.code,"98");compare(otp.editor.text,"98")
        }
        function test_rawEditorAndGetterCommit() {
            const otp=create();focusEditor(otp)
            replace(otp,"a1b٢Ⅳ1́2");compare(otp.editor.text,"a1b٢Ⅳ1́2");compare(otp.code,"1٢Ⅳ1́2")
            otp.code="X987654321";compare(otp.editor.text,"X987654321")
            otp.length=2;compare(otp.editor.text,"X987654321")
            replace(otp,"1️⃣٢Ⅳ³一");compare(otp.code,"1️⃣٢");compare(otp.editor.text,"1️⃣٢Ⅳ³一")
            keyClick(Qt.Key_Return);compare(otp.editor.text,"1️⃣٢");verify(otp.editor.activeFocus)
            blur(otp);compare(otp.editor.text,otp.code)
        }
        function test_rejectedAndUnchangedWrites() {
            for(const config of [{code:"12",observeOnly:true},{code:"",length:0}]) {
                const otp=create(config);focusEditor(otp)
                replace(otp,"a1b٢Ⅳ1́2");compare(otp.code,config.code);compare(otp.editor.text,"a1b٢Ⅳ1́2")
                otp.code="X987654321";compare(otp.editor.text,"a1b٢Ⅳ1́2")
                otp.length=2;compare(otp.editor.text,"X987654321")
                replace(otp,"1️⃣٢Ⅳ³一");compare(otp.editor.text,"1️⃣٢Ⅳ³一")
                keyClick(Qt.Key_Return);compare(otp.editor.text,otp.code)
                blur(otp);compare(otp.editor.text,otp.code)
            }
        }
        function test_deferredOwner() {
            const otp=create({code:"12",deferredOwner:true});focusEditor(otp);wait(5)
            replace(otp,"a1b٢Ⅳ1́2");tryCompare(otp,"code","1٢Ⅳ1́2");compare(otp.editor.text,"a1b٢Ⅳ1́2")
            otp.code="X987654321";compare(otp.editor.text,otp.code)
            blur(otp)
        }
        Component {
            id:traversalFactory
            Item {
                width:700;height:120
                readonly property Item before:beforeItem
                readonly property Item otp:otpItem
                readonly property Item after:afterItem
                T.Button {id:beforeItem;x:5;y:5;width:100;height:40;text:"Before";focusPolicy:Qt.StrongFocus}
                BleeckerOTPInput {id:otpItem;x:130;y:5;code:"";onCodeRequested:value=>code=value}
                T.Button {id:afterItem;x:400;y:5;width:100;height:40;text:"After";focusPolicy:Qt.StrongFocus}
            }
        }
        function test_tabAndBacktabTraversal() {
            const host=createTemporaryObject(traversalFactory,root);verify(host)
            host.before.forceActiveFocus();verify(host.before.activeFocus)
            keyClick(Qt.Key_Tab);verify(host.otp.editor.activeFocus)
            keyClick(Qt.Key_Tab);verify(host.after.activeFocus)
            keyClick(Qt.Key_Backtab);verify(host.otp.editor.activeFocus)
            keyClick(Qt.Key_Backtab);verify(host.before.activeFocus)
            host.otp.forceActiveFocus();verify(host.otp.editor.activeFocus)
            outside.forceActiveFocus()
        }
        function test_largeInput() {
            const otp=create();focusEditor(otp);const raw="a".repeat(40000)+"1"
            replace(otp,raw);compare(otp.editor.text.length,40001);compare(otp.editor.text,raw);compare(otp.code,"1")
            blur(otp);compare(otp.editor.text,"1")
        }
        function test_composition() {
            const otp=create({code:"12"});focusEditor(otp);otp.editor.selectAll()
            fixtureSetup.preeditText(otp.editor,"一");verify(otp.editor.inputMethodComposing);compare(otp.code,"12");compare(otp.editor.preeditText,"一")
            fixtureSetup.preeditText(otp.editor,"一二");compare(otp.code,"12");compare(otp.editor.preeditText,"一二")
            fixtureSetup.commitText(otp.editor,"一二");wait(5);compare(otp.code,"一二");verify(!otp.editor.inputMethodComposing)
            replace(otp,"a𝟙1️⃣一b٢");compare(otp.code,"𝟙1️⃣一٢");compare(otp.editor.text,"a𝟙1️⃣一b٢")
            blur(otp);compare(otp.editor.text,otp.code)
        }
        function test_geometryAndNativeTemplate() {
            const otp=create({code:"123"});compare(otp.implicitWidth,240);compare(otp.implicitHeight,40)
            compare(otp.editor.font.family,BleeckerFonts.monospace);compare(otp.editor.font.weight,Font.DemiBold)
            fuzzyCompare(otp.editor.font.pointSize,BleeckerFonts.pointSizeForPixels(20),0.000001)
            compare(otp.editor.horizontalAlignment,TextInput.AlignHCenter);compare(otp.editor.placeholderElide,Text.ElideNone)
            compare(otp.editor.Accessible.name,"Verification code");compare(otp.editor.maximumLength,2147483647)
            compare(otp.editor.inputMethodHints,Qt.ImhNone);compare(otp.editor.validator,null)
            BleeckerTheme.textScale=1.5;compare(otp.implicitHeight,60)
            fuzzyCompare(otp.editor.font.pointSize,BleeckerFonts.pointSizeForPixels(20),0.000001)
            otp.width=12;compare(otp.editor.width,28);fuzzyCompare(otp.editor.x,-8,0.000001)
            otp.enabled=false;const calls=otp.requests.length
            mouseClick(otp.editor,20,20);verify(!otp.editor.activeFocus);compare(otp.requests.length,calls)
        }
        function test_nativeTraceSnapshots() {
            compare(nativeOTPTraces.length,19)
            let results=[],stateFailures=0
            for(const trace of nativeOTPTraces) {
                const events=trace.events || trace.steps
                const initial=events[0].state
                const observed=trace.sourceFile!=="state-bindings/state-bindings.json"
                const otp=create({code:trace.initialCode!==undefined ? trace.initialCode:initial.code,
                                  length:trace.initialLength!==undefined ? trace.initialLength:6,
                                  enabled:!trace.disabled && trace.fixture!=="disabled",
                                  observeOnly:!!trace.observeOnly,deferredOwner:!!trace.deferredOwner,
                                  manualDeferred:!!trace.deferredOwner,publishesWrites:observed})
                let snapshots=[]
                for(const event of events) {
                    const action=event.action
                    if(action==="focus")otp.editor.forceActiveFocus(Qt.OtherFocusReason)
                    else if(action==="select-all")otp.editor.selectAll()
                    else if(action==="insert-mixed" || action==="insert-keycap" || action==="commit-mixed" || action==="insert-40001") {
                        otp.editor.selectAll()
                        const raw=action==="insert-mixed" ? "a1b٢Ⅳ1́2":action==="insert-keycap" ? "1️⃣٢Ⅳ³一":action==="commit-mixed" ? "a𝟙1️⃣一b٢":"a".repeat(40000)+"1"
                        fixtureSetup.commitText(otp.editor,raw)
                    } else if(action==="delete-backward")keyClick(Qt.Key_Backspace)
                    else if(action==="external-unfiltered")otp.code="X987654321"
                    else if(action==="external-length-two" || action==="length-two")otp.length=2
                    else if(action==="return-command")keyClick(Qt.Key_Return)
                    else if(action==="blur")outside.forceActiveFocus()
                    else if(action==="mark-one"){otp.editor.selectAll();fixtureSetup.preeditText(otp.editor,"一")}
                    else if(action==="mark-two")fixtureSetup.preeditText(otp.editor,"一二")
                    else if(action==="unmark")fixtureSetup.commitText(otp.editor,"一二")
                    else if(action==="settled" || action.endsWith("-settled"))wait(20)
                    else compare(action,"initial","Unmapped native OTP action")
                    // The native owners use wall-clock delayed writes (50ms
                    // observed object, 100ms state) around a 50ms settle. The
                    // observed snapshots straddle those timer deadlines. Replay
                    // their owner-acknowledgement order explicitly, from queued
                    // actual requests; never assign an expected model value.
                    const flush=trace.deferredOwner && (action==="settled" || action.endsWith("-settled")
                        || observed && ["focus","delete-backward","insert-keycap","return-command","blur"].indexOf(action)>=0)
                    if(flush)otp.flushWrites()
                    const expected=event.state
                    const actual={code:otp.code,fieldValue:otp.editor.displayText,requests:otp.requests,
                                  hasMarkedText:otp.editor.inputMethodComposing,
                                  selection:{location:otp.editor.selectionStart,length:otp.editor.selectionEnd-otp.editor.selectionStart}}
                    const stateMatch=actual.code===expected.code && actual.fieldValue===expected.fieldValue
                        && (expected.hasMarkedText===undefined || actual.hasMarkedText===expected.hasMarkedText)
                    if(!stateMatch)stateFailures++
                    const sourceSelection=expected.editorSelection || expected.selection
                    snapshots.push({action:action,native:expected,actual:actual,modelAndEditorMatch:stateMatch,
                                    callbackComparison:trace.bindingMode==="projected-state" ? "not observed by native projected-state trace":JSON.stringify(actual.requests)===JSON.stringify(expected.requests),
                                    ownerQueueFlushed:!!flush,
                                    selectionMatch:sourceSelection===undefined ? null:actual.selection.location===sourceSelection.location && actual.selection.length===sourceSelection.length})
                }
                results.push({fixture:trace.fixture,sourceFile:trace.sourceFile,bindingMode:trace.bindingMode || "functional-observed",snapshots:snapshots})
                outside.forceActiveFocus();otp.destroy();wait(1)
            }
            const report=fixtureSetup.saveOTPTraceReport(results)
            console.info("Native OTP replay report: "+report)
            compare(stateFailures,0,"Native model/editor mismatches; see "+report)
        }
    }
}
