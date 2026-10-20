import QtQuick
import QtQuick.Templates as T
import Avelino

T.ApplicationWindow {
    id: window
    readonly property bool gallery:typeof consumerDark==="undefined"
    property var definition:({case:"standard",width:360,height:240,header:36,footer:24,content:"flex",hiddenHeader:false,
        tabs:[{value:"news",label:"News",systemImage:"newspaper",badge:8},
              {value:"saved",label:"Saved",systemImage:"bookmark",disabled:true,accessibilityLabel:"Stored items"}]})
    property var selection:"news"
    property var requests:[]
    property var pending:null
    property string owner:"echo"
    readonly property Item primaryFixture:fixture
    width:gallery ? 1120:Math.ceil(definition.width)
    height:gallery ? 780:Math.ceil(definition.height)+(header && header.visible ? header.height:0)
    visible:true
    title:"Avelino desktop application shell"
    background:Rectangle { color:BleeckerTheme.palette.background }
    header:fixture.toolbarItem
    function configure(value):void {
        definition=Object.assign({},value)
        if(value.dark!==undefined)BleeckerTheme.dark=value.dark
        Qt.callLater(function() { fixture.shell.synchronizeSelection() })
    }
    function request(value):void {
        requests=requests.concat([value])
        if(owner==="echo")selection=value
        else if(owner==="delay")pending=value
    }
    function ownerState():var { return {selection:selection,requests:requests,pending:pending} }
    function resetOwner(value):void { owner=value;selection="news";requests=[];pending=null;fixture.shell.synchronizeSelection() }
    function externalSelection(value):void { selection=value;Qt.callLater(function(){fixture.shell.synchronizeSelection()}) }
    function applyPending():void { if(pending!==null){selection=pending;pending=null} }
    function update(value):void { configure(Object.assign({},definition,value)) }
    Component.onCompleted: {
        BleeckerTheme.dark=gallery ? captureDark:consumerDark
        BleeckerTheme.textScale=gallery ? captureTextScale:consumerTextScale
        BleeckerTheme.reducedMotion=true
    }
    ProposalRow {
        x:24;y:24;spacing:8;visible:window.gallery
        BleeckerButton { text:"Empty content";size:"xs";onClicked:window.update({content:"empty"}) }
        BleeckerButton { text:"Zero content";size:"xs";onClicked:window.update({content:"zero"}) }
        BleeckerButton { text:"Fixed content";size:"xs";onClicked:window.update({content:"fixed"}) }
        BleeckerButton { text:"Fill content";size:"xs";onClicked:window.update({content:"flex"}) }
        BleeckerButton { text:"Footer";size:"xs";onClicked:window.update({footer:window.definition.footer===null ? 24:null}) }
    }
    ProposalRow {
        x:24;y:80;spacing:8;visible:window.gallery
        BleeckerButton { text:"Width";size:"xs";onClicked:window.update({width:window.definition.width===360 ? 100:360}) }
        BleeckerButton { text:"Height";size:"xs";onClicked:window.update({height:window.definition.height===240 ? 24:240}) }
        Repeater {
            model:["echo","ignore","delay"]
            BleeckerButton {required property string modelData;text:modelData;size:"xs";onClicked:window.resetOwner(modelData)}
        }
        BleeckerButton { text:"Apply pending";size:"xs";onClicked:window.applyPending() }
        BleeckerButton { text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark }
    }
    MobileShellCase {
        id:fixture
        x:window.gallery ? 24:0;y:window.gallery ? 160:0
        definition:window.definition
        selection:window.selection
        onSelectionRequested:requestedValue=>window.request(requestedValue)
    }
    Text {
        x:520;y:180;width:520;visible:window.gallery
        text:"Caller selection: "+window.selection+"\nDisplayed segment: "+fixture.toolbarItem.displayedIndex
            +"\nRequests: "+JSON.stringify(window.requests)+"\nPending: "+JSON.stringify(window.pending)
            +"\n\nDesktop sections live in the toolbar. Per-tab badges and disabled flags are ignored by the pinned desktop Picker."
            +"\n\nNative toolbar pixels, symbols, keyboard timing and physical/reader acceptance remain pending."
        wrapMode:Text.WordWrap
        font.family:BleeckerTheme.secondaryFont;font.pixelSize:16;color:BleeckerTheme.palette.textSecondary
    }
}
