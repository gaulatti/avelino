import QtQuick
import Avelino

Window {
    id:window
    readonly property bool gallery:typeof consumerDark==="undefined"
    width:gallery ? 1120:600;height:gallery ? 720:300
    visible:true;title:"Avelino dropdown menu";color:BleeckerTheme.palette.background
    property var model:({id:"default",title:"Actions",label:"text",itemMode:"normal",controlSize:"regular"})
    property bool mounted:true
    readonly property Item primaryFixture:fixtureLoader.item
    function configure(value):void {model=Object.assign({},value);if(primaryFixture){primaryFixture.actions=[];primaryFixture.labelActions=0}}
    function update(value):void {configure(Object.assign({},model,value))}
    function environment(dark,scale):void {BleeckerTheme.dark=dark;BleeckerTheme.textScale=scale}
    Component.onCompleted:{BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=gallery ? captureDark:consumerDark;BleeckerTheme.textScale=gallery ? captureTextScale:consumerTextScale}
    ProposalRow {
        x:24;y:24;spacing:8;visible:window.gallery
        Repeater {
            model:[{title:"Text",label:"text"},{title:"Icon",label:"icon"},{title:"Text + image",label:"stack"},{title:"Rectangle",label:"rect"},{title:"Empty label",label:"empty"}]
            BleeckerButton {required property var modelData;text:modelData.title;size:"xs";objectName:"dropdownOperator-label-"+modelData.label;onClicked:window.update({label:modelData.label})}
        }
        BleeckerButton {objectName:"dropdownOperator-many";text:"40 commands";size:"xs";onClicked:window.update({itemMode:window.model.itemMode==="many" ? "normal":"many"})}
        BleeckerButton {objectName:"dropdownOperator-empty";text:"Empty / restore";size:"xs";onClicked:window.update({empty:!window.model.empty})}
        BleeckerButton {objectName:"dropdownOperator-repeated";text:"Repeated titles";size:"xs";onClicked:window.update({itemMode:window.model.itemMode==="duplicate-titles" ? "normal":"duplicate-titles"})}
    }
    ProposalRow {
        x:24;y:80;spacing:8;visible:window.gallery
        BleeckerButton {objectName:"dropdownOperator-open";text:"Open menu";size:"xs";onClicked:window.primaryFixture.control.open()}
        BleeckerButton {objectName:"dropdownOperator-title";text:"Change title";size:"xs";onClicked:window.update({title:window.model.title==="Actions" ? "Document actions":"Actions"})}
        BleeckerButton {objectName:"dropdownOperator-disabled";text:"Disabled";size:"xs";onClicked:window.update({disabled:!window.model.disabled})}
        BleeckerButton {objectName:"dropdownOperator-rtl";text:"RTL";size:"xs";onClicked:window.update({rtl:!window.model.rtl})}
        BleeckerButton {objectName:"dropdownOperator-theme";text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
        BleeckerButton {objectName:"dropdownOperator-size";text:"Control size";size:"xs";onClicked:window.update({controlSize:window.model.controlSize==="regular" ? "small":window.model.controlSize==="small" ? "mini":"regular"})}
        BleeckerButton {objectName:"dropdownOperator-scale";text:"Text scale";size:"xs";onClicked:BleeckerTheme.textScale=BleeckerTheme.textScale===1 ? 1.5:1}
    }
    Loader {
        id:fixtureLoader;y:window.gallery ? 180:0;active:window.mounted
        sourceComponent:Component {DropdownMenuCase {configuration:window.model}}
    }
    BleeckerText {
        x:650;y:240;width:420;visible:window.gallery
        text:window.primaryFixture&&window.primaryFixture.actions.length ? "Actions: "+window.primaryFixture.actions.join(" → "):"Choose a command to invoke its owner action."
        font.pixelSize:16;color:BleeckerTheme.palette.textSecondary
    }
}
