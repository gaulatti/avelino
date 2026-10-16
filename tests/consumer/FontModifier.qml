import QtQuick
import QtQuick.Templates as T
import Avelino

Window {
    id:window;width:1100;height:820;visible:true;title:"Avelino inherited caller fonts"
    color:BleeckerTheme.palette.background
    property var model:({fixture:"gallery",family:"primary",size:14,weight:"regular",content:"text",text:"Keep edition",offer:null,
        parentFont:false,outerSystem:false,outerFontModifier:false,parentLayout:"zstack",rtl:false,width:640,height:400})
    property bool baselineParent:false
    property int activations:0
    property int passthroughActivations:0
    readonly property FontModifierCase primaryFixture:primary
    readonly property Item inputItem:callerButton
    readonly property Item transparentItem:transparentText
    function configure(values){model=Object.assign({},model,values)}
    Component.onCompleted:{
        BleeckerTheme.reducedMotion=true
        BleeckerTheme.dark=typeof consumerDark!=="undefined" ? consumerDark:captureDark
        BleeckerTheme.textScale=typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
    }
    ProposalRow {
        x:24;y:24;spacing:10
        Repeater {model:["primary","secondary","mono"]
            BleeckerButton {required property string modelData;text:modelData;size:"sm";onClicked:window.configure({family:modelData})}
        }
        BleeckerButton {text:"Larger";size:"sm";onClicked:window.configure({size:window.model.size===14 ? 24:14})}
        BleeckerButton {text:"Weight";size:"sm";onClicked:window.configure({weight:window.model.weight==="regular" ? "bold":"regular"})}
        BleeckerButton {text:"Baseline";size:"sm";onClicked:window.baselineParent=!window.baselineParent}
    }
    ProposalRow {
        x:24;y:88;spacing:8
        Repeater {model:["text","own-font","nested-font","scaled-subtree","multi","vstack","hstack"]
            BleeckerButton {required property string modelData;text:modelData;size:"xs";onClicked:window.configure({content:modelData})}
        }
    }
    ProposalRow {
        x:24;y:142;spacing:8
        BleeckerButton {text:"Overlay";size:"xs";onClicked:window.configure({parentLayout:"zstack"})}
        BleeckerButton {text:"Row";size:"xs";onClicked:window.configure({parentLayout:"hstack"})}
        BleeckerButton {text:"Column";size:"xs";onClicked:window.configure({parentLayout:"vstack"})}
        BleeckerButton {text:"Scale";size:"xs";onClicked:BleeckerTheme.textScale=BleeckerTheme.textScale===1 ? 1.5:1}
        BleeckerButton {text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
    }
    FontModifierCase {id:primary;objectName:"consumerFontModifier";x:24;y:202;definition:window.model;baselineParent:window.baselineParent}
    Text {x:24;y:644;text:window.model.family+" / "+window.model.size+" / "+window.model.weight+" / scale "+BleeckerTheme.textScale;font.family:BleeckerFonts.secondary;font.pixelSize:14;color:BleeckerTheme.palette.textPrimary}
    Text {x:730;y:205;width:320;text:"Font defaults reach retained caller content. Explicit inner fonts and independently scaled subtrees keep their own scope.";wrapMode:Text.WordWrap;font.family:BleeckerFonts.secondary;font.pixelSize:15;color:BleeckerTheme.palette.textSecondary}
    BleeckerFont {
        x:740;y:354;family:window.model.family;size:window.model.size;weight:window.model.weight
        T.Button {
            id:callerButton;objectName:"fontModifierCallerButton";implicitWidth:220;implicitHeight:56
            text:"Activate "+window.activations;focusPolicy:Qt.StrongFocus
            background:Rectangle {color:BleeckerTheme.palette.card;border.color:BleeckerTheme.palette.border}
            contentItem:Item {BleeckerText {anchors.centerIn:parent;anchors.alignWhenCentered:false;text:callerButton.text;color:BleeckerTheme.palette.textPrimary}}
            Accessible.name:text;onClicked:window.activations++
        }
    }
    Item {
        x:740;y:482;width:300;height:100
        MouseArea {anchors.fill:parent;onClicked:window.passthroughActivations++}
        BleeckerFont {anchors.centerIn:parent;family:"primary";size:14;BleeckerText {id:transparentText;text:"Transparent text scope"}}
    }
    Text {x:730;y:620;width:320;text:"Caller activations: "+window.activations+"\nText pass-through: "+window.passthroughActivations;wrapMode:Text.WordWrap;font.family:BleeckerFonts.secondary;font.pixelSize:14;color:BleeckerTheme.palette.textPrimary}
}
