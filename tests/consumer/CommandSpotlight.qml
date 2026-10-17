import QtQuick
import Avelino

Window {
    id:window
    readonly property bool gallery:typeof consumerDark==="undefined"
    width:gallery ? 1120:720;height:gallery ? 860:520
    visible:true;title:"Avelino command spotlight";color:BleeckerTheme.palette.background
    function initialEntries(){return Array.from({length:80},(_,i)=>({id:String(i),key:String(i),title:"Command "+i,detail:"Details "+i,kind:"button",height:20,disabled:false}))}
    property var model:({id:"default",entries:initialEntries(),query:"",owner:"echo",valueKind:"string",rtl:false,disabled:false,parentFont:false,parentRed:false})
    property string query:model.query
    property var requests:[]
    property var pending:null
    property bool mounted:true
    readonly property Item primaryFixture:fixtureLoader.item
    function ownerState(){return {query:query,requests:requests,pending:pending}}
    function flushOwner(){if(pending!==null){query=pending;pending=null}}
    function configure(value):void {model=Object.assign({},value);query=value.query;requests=[];pending=null}
    function update(value):void {model=Object.assign({},model,value)}
    function environment(dark,scale):void {BleeckerTheme.dark=dark;BleeckerTheme.textScale=scale}
    function request(value):void {
        requests=requests.concat([value])
        if(model.owner==="echo")query=value
        else if(model.owner==="delayed")pending=value
        else if(model.owner==="redirect")query="Owner redirect"
    }
    function blur():void {focusSink.forceActiveFocus()}
    Component.onCompleted:{BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=gallery ? captureDark:consumerDark;BleeckerTheme.textScale=gallery ? captureTextScale:consumerTextScale}
    Item {id:focusSink}
    ProposalRow {
        x:24;y:24;spacing:8;visible:window.gallery
        Repeater {model:["echo","observe","delayed","redirect"]
            BleeckerButton {required property string modelData;objectName:"spotlightOperator-owner-"+modelData;text:modelData;size:"xs";onClicked:window.update({owner:modelData})}}
        BleeckerButton {objectName:"spotlightOperator-flush";text:"Apply pending";size:"xs";onClicked:window.flushOwner()}
        BleeckerButton {objectName:"spotlightOperator-external";text:"Change query";size:"xs";onClicked:window.query="No matching commands"}
        BleeckerButton {objectName:"spotlightOperator-reorder";text:"Reverse";size:"xs";onClicked:window.update({entries:window.model.entries.slice().reverse()})}
        BleeckerButton {objectName:"spotlightOperator-empty";text:"Empty / restore";size:"xs";onClicked:window.update({entries:window.model.entries.length ? []:window.initialEntries()})}
    }
    ProposalRow {
        x:24;y:80;spacing:8;visible:window.gallery
        BleeckerButton {objectName:"spotlightOperator-width";text:"Caller width";size:"xs";onClicked:window.update({callerWidth:window.model.callerWidth===30 ? 520:30})}
        BleeckerButton {objectName:"spotlightOperator-disabled";text:"Disabled";size:"xs";onClicked:window.update({disabled:!window.model.disabled})}
        BleeckerButton {objectName:"spotlightOperator-rtl";text:"RTL";size:"xs";onClicked:window.update({rtl:!window.model.rtl})}
        BleeckerButton {objectName:"spotlightOperator-theme";text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
        BleeckerButton {objectName:"spotlightOperator-scale";text:"Text scale";size:"xs";onClicked:BleeckerTheme.textScale=BleeckerTheme.textScale===1 ? 1.5:1}
        BleeckerButton {objectName:"spotlightOperator-bottom";text:"Bottom";size:"xs";onClicked:window.primaryFixture.control.scrollTo(window.primaryFixture.control.rowContainer.contentHeight)}
        BleeckerButton {objectName:"spotlightOperator-top";text:"Top";size:"xs";onClicked:window.primaryFixture.control.scrollTo(0)}
    }
    Loader {
        id:fixtureLoader;x:0;y:window.gallery ? 180:0;active:window.mounted
        sourceComponent:Component {CommandSpotlightCase {definition:window.model;query:window.query;onQueryRequested:value=>window.request(value)}}
    }
    Text {
        x:750;y:240;width:330;visible:window.gallery;wrapMode:Text.WordWrap
        text:"Query: "+window.query+"\nRequests: "+JSON.stringify(window.requests)+"\nPending: "+JSON.stringify(window.pending)
        font.family:BleeckerTheme.secondaryFont;font.pixelSize:16;color:BleeckerTheme.palette.textSecondary
    }
}
