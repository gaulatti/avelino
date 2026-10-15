import QtQuick
import Avelino
Window {
    id:window;width:900;height:640;visible:true;color:BleeckerTheme.palette.background
    title:"Avelino loading indicators"
    property bool busy:true
    Component.onCompleted:{BleeckerTheme.dark=captureDark;BleeckerTheme.textScale=captureTextScale;BleeckerTheme.reducedMotion=true}
    BleeckerEyebrow {x:28;y:26;text:"Loading indicators"}
    Row {x:48;y:100;spacing:64
        BleeckerLoadingSpinner {size:"sm"}
        BleeckerLoadingSpinner {}
        BleeckerLoadingSpinner {size:"lg"}
        BleeckerLoadingSpinner {color:BleeckerTheme.palette.sea}
    }
    Row {x:28;y:220;spacing:20
        BleeckerButton {text:"Publish";loading:window.busy}
        BleeckerButton {text:"Save changes";variant:"secondary";loading:window.busy}
        BleeckerButton {text:"Remove";variant:"destructive";loading:window.busy}
    }
    Item {x:28;y:340;width:390;height:240
        BleeckerLoadingOverlay {anchors.fill:parent;visible:window.busy;message:"Preparing editions"}
    }
    BleeckerButton {x:500;y:440;text:window.busy ? "Finish loading" : "Start loading";onClicked:window.busy=!window.busy}
}
