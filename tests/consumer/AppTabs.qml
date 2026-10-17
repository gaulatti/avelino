import QtQuick
import Avelino

Window {
    id:window
    readonly property bool gallery:typeof consumerDark==="undefined"
    width:gallery ? 1120:640;height:gallery ? 820:400
    visible:true;title:"Avelino app tabs";color:BleeckerTheme.palette.background
    function initialTabs(){return [{value:"a",label:"Home",systemImage:"house"},{value:"b",label:"Inbox",systemImage:"tray",badge:"7"},{value:"c",label:"Settings",systemImage:"gearshape"}]}
    property var model:({id:"default",tabs:initialTabs(),selection:"a",valueKind:"string",width:300,height:null,rtl:false,disabled:false,parentFont:false,parentRed:false,owner:"echo"})
    property var requests:[]
    property var pending:null
    property string selection:model.selection
    property bool mounted:true
    readonly property Item primaryFixture:fixtureLoader.item
    function ownerState(){return {selection:selection,requests:requests,pending:pending}}
    function flushOwner(){if(pending!==null){selection=pending;pending=null}}
    function configure(value):void {model=Object.assign({},value);selection=value.selection;requests=[];pending=null}
    function update(value):void {model=Object.assign({},model,value)}
    function environment(dark,scale):void {BleeckerTheme.dark=dark;BleeckerTheme.textScale=scale}
    function request(value):void {
        requests=requests.concat([value])
        if(model.owner==="echo")selection=value
        else if(model.owner==="delayed")pending=value
        else if(model.owner==="redirect")selection=model.tabs[0].value
    }
    Component.onCompleted:{BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=gallery ? captureDark:consumerDark;BleeckerTheme.textScale=gallery ? captureTextScale:consumerTextScale}
    ProposalRow {
        x:24;y:24;spacing:8;visible:window.gallery
        Repeater {model:["echo","observe","delayed","redirect"]
            BleeckerButton {required property string modelData;objectName:"appTabsOperator-owner-"+modelData;text:modelData;size:"xs";onClicked:window.update({owner:modelData})}
        }
        BleeckerButton {objectName:"appTabsOperator-flush";text:"Apply pending";size:"xs";onClicked:if(window.pending!==null){window.selection=window.pending;window.pending=null}}
        BleeckerButton {objectName:"appTabsOperator-external";text:"Settings";size:"xs";onClicked:window.selection="c"}
        BleeckerButton {objectName:"appTabsOperator-reorder";text:"Reverse";size:"xs";onClicked:window.update({tabs:window.model.tabs.slice().reverse()})}
        BleeckerButton {objectName:"appTabsOperator-empty";text:"Empty / restore";size:"xs";onClicked:window.update({tabs:window.model.tabs.length ? []:window.initialTabs()})}
    }
    ProposalRow {
        x:24;y:80;spacing:8;visible:window.gallery
        BleeckerButton {objectName:"appTabsOperator-width";text:"Width";size:"xs";onClicked:window.update({width:window.model.width===300 ? 30:window.model.width===30 ? 150:300})}
        BleeckerButton {objectName:"appTabsOperator-badges";text:"Badges";size:"xs";onClicked:window.update({tabs:window.model.tabs.map(t=>Object.assign({},t,{badge:t.badge==="100" ? "0":"100"}))})}
        BleeckerButton {objectName:"appTabsOperator-disabled";text:"Disabled";size:"xs";onClicked:window.update({disabled:!window.model.disabled})}
        BleeckerButton {objectName:"appTabsOperator-rtl";text:"RTL";size:"xs";onClicked:window.update({rtl:!window.model.rtl})}
        BleeckerButton {objectName:"appTabsOperator-theme";text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
        BleeckerButton {objectName:"appTabsOperator-scale";text:"Text scale";size:"xs";onClicked:BleeckerTheme.textScale=BleeckerTheme.textScale===1 ? 1.5:1}
    }
    Loader {
        id:fixtureLoader;x:0;y:window.gallery ? 180:0;active:window.mounted
        sourceComponent:Component {AppTabsCase {definition:window.model;selection:window.selection;onSelectionRequested:value=>window.request(value)}}
    }
    Text {
        x:720;y:230;width:340;visible:window.gallery;wrapMode:Text.WordWrap
        text:"Selection: "+window.selection+"\nRequests: "+JSON.stringify(window.requests)+"\nPending: "+JSON.stringify(window.pending)+"\n\nThe owner can apply, delay or redirect a request. Native symbols, label fitting, focus timing and reader equivalence remain pending."
        font.family:BleeckerTheme.secondaryFont;font.pixelSize:16;color:BleeckerTheme.palette.textSecondary
    }
}
