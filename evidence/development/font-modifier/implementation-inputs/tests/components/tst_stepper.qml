import QtQuick
import QtTest
import Avelino

Item {
    id:root
    width:800;height:240
    property var amount:"2"
    property var lower:"1"
    property var upper:"10"
    property var step:1
    property var offset:0
    property string label:"Quantity"
    property bool disabled:false
    property bool applyRequest:true
    property var requests:[]
    Component {
        id:factory
        BleeckerStepper {
            x:20;y:20
            label:root.label;value:root.amount;lowerBound:root.lower;upperBound:root.upper
            step:root.step;displayOffset:root.offset;enabled:!root.disabled
            onValueRequested:requested => {root.requests=root.requests.concat([requested]);if(root.applyRequest)root.amount=requested}
        }
    }
    TestCase {
        name:"StepperContracts";when:windowShown
        function init(){root.amount="2";root.lower="1";root.upper="10";root.step=1;root.offset=0;root.label="Quantity";root.disabled=false;root.applyRequest=true;root.requests=[];fixtureSetup.setProcessLocale("en_US");BleeckerTheme.dark=false;BleeckerTheme.textScale=1;failOnWarning(/Binding loop/)}
        function cleanup(){fixtureSetup.setProcessLocale("en_US")}
        function test_native_traces_data(){return nativeStepperBehavior.map(row => ({tag:row.fixture,row}))}
        function test_native_traces(d){
            const source=d.row
            root.amount=source.initialValue;root.lower=source.lowerBound;root.upper=source.upperBound;root.step=source.step;root.offset=source.displayOffset;root.disabled=source.disabled;root.applyRequest=!source.observeOnly
            const item=createTemporaryObject(factory,root)
            verify(item)
            for(const action of source.actions){
                verify(waitForPolish(findChild(item,"bleeckerStepperContent")))
                compare(item.value,action.before)
                if(action.action==="cancel"){
                    mousePress(item.incrementInput);mouseMove(root,700,200);mouseRelease(root,700,200)
                }else mouseClick(action.action==="increment" ? item.incrementInput:item.decrementInput)
                compare(root.amount,action.after)
            }
            compare(root.requests,source.requests)
            root.amount="6";root.lower="5";root.upper="7";root.step=2;root.offset=100;root.label="Updated copies";root.disabled=false
            compare(root.requests.length,source.externalUpdate.requestCountAfter)
            compare(findChild(item,"bleeckerStepperValue").text,source.externalUpdate.formattedValue)
            for(const action of source.afterExternalActions){
                verify(waitForPolish(findChild(item,"bleeckerStepperContent")))
                mouseClick(action.action==="increment" ? item.incrementInput:item.decrementInput)
                compare(root.amount,action.after)
            }
            compare(item.value,source.finalValue);compare(findChild(item,"bleeckerStepperValue").text,source.finalFormattedValue)
        }
        function test_native_integer_formatting_data(){return nativeStepperFormatting.map(row => ({tag:row.locale+"-"+row.value,row}))}
        function test_native_integer_formatting(d){
            const row=d.row
            fixtureSetup.setProcessLocale(row.locale)
            root.amount=row.value;root.lower="-9223372036854775808";root.upper="9223372036854775807"
            const item=createTemporaryObject(factory,root,{locale:Qt.locale("de_DE")})
            compare(findChild(item,"bleeckerStepperValue").text,row.text)
            compare(item.valueState.displayValue,row.value)
        }
        function test_pointer_phase_hold_and_cancel(){
            const item=createTemporaryObject(factory,root)
            mousePress(item.incrementInput);compare(root.requests.length,0);wait(1200);compare(root.requests.length,0)
            mouseRelease(item.incrementInput);compare(root.requests,["3"])
            mousePress(item.decrementInput);mouseMove(root,700,200);mouseRelease(root,700,200);compare(root.requests,["3"])
            const point=item.decrementInput.mapToItem(item,Qt.point(item.decrementInput.width/2,-2))
            mouseClick(item,point.x,point.y);compare(root.requests,["3"])
        }
        function test_external_updates_and_process_locale(){
            root.amount="1234";root.lower="-9999";root.upper="9999"
            const item=createTemporaryObject(factory,root,{locale:Qt.locale("de_DE")}),text=findChild(item,"bleeckerStepperValue")
            compare(text.text,"1,234");fixtureSetup.setProcessLocale("de_DE");compare(text.text,"1.234")
            item.locale=Qt.locale("ar_EG");compare(text.text,"1.234");root.offset="1000";compare(text.text,"2.234")
            root.applyRequest=false;mouseClick(item.incrementInput);compare(root.requests,["1235"]);compare(item.value,"1234")
            root.amount="7";compare(text.text,"1.007");root.offset=0;compare(text.text,"7")
        }
        function test_keyboard_disabled_and_fixed_fonts(){
            const item=createTemporaryObject(factory,root),label=findChild(item,"bleeckerStepperLabel"),value=findChild(item,"bleeckerStepperValue")
            item.incrementInput.forceActiveFocus(Qt.TabFocusReason);keyClick(Qt.Key_Space);compare(root.requests,["3"])
            item.enabled=false;mouseClick(item.incrementInput);compare(root.requests,["3"])
            root.amount="4";compare(item.value,"4")
            compare(item.height,36);compare(item.incrementInput.height,12.5);compare(item.decrementInput.height,3.5)
            compare(label.font.pointSize,BleeckerFonts.pointSizeForPixels(13));compare(value.font.pointSize,BleeckerFonts.pointSizeForPixels(12))
            const width=item.width;BleeckerTheme.textScale=1.5;compare(item.width,width)
            item.font.pointSize=BleeckerFonts.pointSizeForPixels(30)
            compare(label.font.pointSize,BleeckerFonts.pointSizeForPixels(13));compare(value.font.pointSize,BleeckerFonts.pointSizeForPixels(12))
            verify(item.incrementInput.width>30)
        }
        function test_narrow_layout_and_empty_label(){
            const item=createTemporaryObject(factory,root,{width:12}),label=findChild(item,"bleeckerStepperLabel")
            compare(label.width,0);verify(item.presentationItem.width>item.width)
            root.label="";compare(label.width,0);compare(label.height,14)
            item.width=300;root.label="Quantity";compare(item.presentationItem.width,item.naturalWidth)
        }
    }
}
