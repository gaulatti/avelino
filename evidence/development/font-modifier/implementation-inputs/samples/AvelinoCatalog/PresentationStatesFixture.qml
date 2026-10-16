import QtQuick
import Avelino
Window {
    id:window;width:900;height:640;visible:true
    color:BleeckerTheme.palette.background;title:"Avelino presentation states"
    property bool busy:true
    Component.onCompleted:{BleeckerTheme.dark=captureDark;BleeckerTheme.textScale=captureTextScale;BleeckerTheme.reducedMotion=true}
    BleeckerEyebrow {x:28;y:26;text:"Empty, error and loading states"}
    BleeckerEmptyState {
        x:28;y:64;width:390;title:"No editions yet";message:"Create an edition and invite the team to prepare its articles for publication."
        actions:Component {BleeckerButton {property int count:0;text:"Create "+count;maximumWidth:parent.availableWidth;onClicked:count++}}
    }
    BleeckerErrorState {
        x:462;y:64;width:390;message:"We couldn't load the latest edition. Check the connection and try again."
        actions:Component {BleeckerButton {text:"Try again";maximumWidth:parent.availableWidth}}
    }
    Item {
        x:28;y:352;width:390;height:240
        BleeckerButton {anchors.centerIn:parent;text:"Prepare editions";onClicked:window.busy=true}
        BleeckerLoadingOverlay {anchors.fill:parent;visible:window.busy;message:"Preparing editions"}
    }
    BleeckerEmptyState {x:462;y:364;width:180;title:"Nothing selected";message:"Select an edition to see its details.";LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true}
    BleeckerButton {x:684;y:512;text:window.busy ? "Finish loading" : "Show loading";onClicked:window.busy=!window.busy}
}
