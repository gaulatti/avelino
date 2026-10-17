import QtQuick
import Avelino

Window {
    id:window
    readonly property bool gallery:typeof consumerDark==="undefined"
    readonly property real fixtureTextScale:BleeckerTheme.textScale
    width:gallery ? 1100:640;height:gallery ? 820:400;visible:true;title:"Avelino pill modifier"
    color:BleeckerTheme.palette.background
    property var model:({id:"default",text:"Ready",style:"plain",offer:null,lineLimit:null,parentLayout:"center",rtl:false,parentFont:false,parentRed:false,hidden:false,disabled:false})
    readonly property Item primaryFixture:fixture
    function configure(value):void {model=value}
    function update(value):void {model=Object.assign({},model,value)}
    function environment(dark,scale):void {BleeckerTheme.dark=dark;BleeckerTheme.textScale=scale}
    Component.onCompleted:{BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=gallery ? captureDark:consumerDark;BleeckerTheme.textScale=gallery ? captureTextScale:consumerTextScale}
    ProposalRow {
        x:24;y:24;spacing:8;visible:window.gallery
        Repeater {model:["plain","primary19","secondary19","red","concat","markdown","image-text"]
            BleeckerButton {required property string modelData;objectName:"pillOperator-style-"+modelData;text:modelData;size:"xs";onClicked:window.update({style:modelData})}
        }
    }
    ProposalRow {
        x:24;y:80;spacing:8;visible:window.gallery
        Repeater {model:["center","hstack","vstack","baseline"]
            BleeckerButton {required property string modelData;objectName:"pillOperator-layout-"+modelData;text:modelData;size:"xs";onClicked:window.update({parentLayout:modelData})}
        }
        BleeckerButton {objectName:"pillOperator-text";text:"Text";size:"xs";onClicked:window.update({text:window.model.text==="Ready" ? "Review edition":"Ready"})}
        BleeckerButton {objectName:"pillOperator-offer";text:"Offer";size:"xs";onClicked:window.update({offer:window.model.offer===null ? 35:null})}
        BleeckerButton {objectName:"pillOperator-rtl";text:"RTL";size:"xs";onClicked:window.update({rtl:!window.model.rtl})}
    }
    ProposalRow {
        x:24;y:136;spacing:8;visible:window.gallery
        BleeckerButton {objectName:"pillOperator-theme";text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
        BleeckerButton {objectName:"pillOperator-scale";text:"Scale";size:"xs";onClicked:BleeckerTheme.textScale=BleeckerTheme.textScale===1 ? 1.5:1}
        BleeckerButton {objectName:"pillOperator-hidden";text:"Hidden";size:"xs";onClicked:window.update({hidden:!window.model.hidden})}
        BleeckerButton {objectName:"pillOperator-disabled";text:"Disabled";size:"xs";onClicked:window.update({disabled:!window.model.disabled})}
    }
    PillModifierCase {id:fixture;x:window.gallery ? 24:0;y:window.gallery ? 200:0;definition:window.model}
    Text {x:720;y:230;width:340;visible:window.gallery;text:"A retained text caller with fixed 7 × 4 padding, a muted capsule and sea foreground. Caller fonts and rich spans retain their own formatting.\n\nNative font, symbol and raster parity remain pending.";wrapMode:Text.WordWrap;font.family:BleeckerFonts.secondary;font.pixelSize:16;color:BleeckerTheme.palette.textSecondary}
}
