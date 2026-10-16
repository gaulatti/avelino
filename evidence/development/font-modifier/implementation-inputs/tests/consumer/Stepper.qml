import QtQuick
import Avelino

Window {
    id:window;width:840;height:540;visible:true;title:"Avelino Stepper"
    color:BleeckerTheme.palette.background
    property var model:({value:"2",lower:"1",upper:"10",step:"1",offset:"0",label:"Quantity",disabled:false,observeOnly:false,parentFont:13,rtl:false})
    property int calls:0
    property string requested:""
    readonly property real fixtureTextScale:typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
    Component.onCompleted:{BleeckerTheme.dark=typeof consumerDark!=="undefined" ? consumerDark:captureDark;BleeckerTheme.textScale=fixtureTextScale;BleeckerTheme.reducedMotion=true}
    BleeckerStepper {
        objectName:"consumerStepper";x:24;y:30
        label:window.model.label;value:window.model.value;lowerBound:window.model.lower;upperBound:window.model.upper
        step:window.model.step;displayOffset:window.model.offset;enabled:!window.model.disabled
        font.pointSize:BleeckerFonts.pointSizeForPixels(window.model.parentFont)
        LayoutMirroring.enabled:window.model.rtl;LayoutMirroring.childrenInherit:true
        onValueRequested:value => {window.calls++;window.requested=value;if(!window.model.observeOnly)window.model=Object.assign({},window.model,{value:value})}
    }
    BleeckerStepper {objectName:"stepperNarrow";x:24;y:100;width:60;label:"A long quantity label";value:2;lowerBound:1;upperBound:10}
    BleeckerStepper {objectName:"stepperDisabled";x:420;y:30;label:"Unavailable";value:2;lowerBound:1;upperBound:10;enabled:false}
    BleeckerStepper {objectName:"stepperZero";x:420;y:100;label:"Zero step";value:2;lowerBound:1;upperBound:10;step:0}
    BleeckerStepper {objectName:"stepperInt64";x:24;y:180;label:"Exact Int64";value:"9223372036854775807";lowerBound:"-9223372036854775808";upperBound:"9223372036854775807"}
    BleeckerStepper {objectName:"stepperNegative";x:24;y:250;label:"Negative step";value:9;lowerBound:1;upperBound:10;step:-4}
    BleeckerStepper {objectName:"stepperRtl";x:420;y:250;label:"RTL quantity";value:2;lowerBound:1;upperBound:10;LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true}
    BleeckerTextField {objectName:"stepperOutsideField";x:24;y:410;width:320;placeholderText:"Continue editing"}
}
