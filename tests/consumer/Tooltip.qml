import QtQuick
import Avelino

Window {
    id:window;width:960;height:720;visible:true;title:"Avelino contextual help"
    color:BleeckerTheme.palette.background
    property string hint:"Publishes the selected edition"
    property var model:({fixture:"gallery",content:"button",disabled:false,rtl:false,parentFont:0,parentRed:false,width:640,height:400})
    readonly property TooltipCase primaryFixture:primary
    readonly property Item primaryCaller:primary.control
    readonly property BleeckerTooltip primaryHelp:primary.help
    readonly property BleeckerTooltip secondaryHelp:fieldHelp
    function configure(values){model=Object.assign({},model,values)}
    Component.onCompleted:{
        // Disable fixture animations before changing the initial palette.
        BleeckerTheme.reducedMotion=true
        BleeckerTheme.dark=typeof consumerDark!=="undefined" ? consumerDark:captureDark
        BleeckerTheme.textScale=typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
    }
    BleeckerButton {objectName:"tooltipBefore";x:24;y:24;text:"Previous";size:"xs"}
    BleeckerButton {objectName:"tooltipAfter";x:140;y:24;text:"Continue";size:"xs"}
    Text {x:24;y:100;text:"Hover the caller button or the field. Help keeps the caller's own layout and input.";font.family:BleeckerTheme.secondaryFont;font.pixelSize:13;color:BleeckerTheme.palette.textPrimary}
    BleeckerTextField {id:hintEditor;objectName:"tooltipHintEditor";x:24;y:138;width:620;placeholderText:"Help text";text:window.hint;onTextEdited:window.hint=text}
    BleeckerTooltip {id:fieldHelp;target:hintEditor;text:"Changes the help text shown on the Publish button"}
    TooltipCase {id:primary;objectName:"consumerTooltip";x:24;y:200;definition:Object.assign({},window.model,{hint:window.hint})}
    Text {x:720;y:235;width:210;text:"A plain caller item also retains its own geometry.";wrapMode:Text.WordWrap;font.family:BleeckerTheme.secondaryFont;font.pixelSize:13;color:BleeckerTheme.palette.textSecondary}
    Rectangle {id:plain;x:720;y:310;width:200;height:80;color:BleeckerTheme.alpha(BleeckerTheme.palette.sea,0.18)}
    BleeckerTooltip {target:plain;text:"Reviews the selected area"}
    Text {x:24;y:640;width:900;text:"Update the hint, activate the caller, and move away. The help adapter adds no layout or focus control.";wrapMode:Text.WordWrap;font.family:BleeckerTheme.secondaryFont;font.pixelSize:13;color:BleeckerTheme.palette.textSecondary}
}
