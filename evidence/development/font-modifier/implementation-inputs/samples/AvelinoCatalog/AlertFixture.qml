import QtQuick
import Avelino
Window {
    id:window;width:900;height:640;visible:true;color:BleeckerTheme.palette.background
    title:"Avelino alerts"
    property bool showDetails:true
    Component.onCompleted:{BleeckerTheme.dark=captureDark;BleeckerTheme.textScale=captureTextScale;BleeckerTheme.reducedMotion=true}
    BleeckerEyebrow {x:28;y:26;text:"Alerts and caller content"}
    Repeater {
        model:["info","success","warning","error"]
        BleeckerAlert {
            required property string modelData
            required property int index
            x:28+(index%2)*430;y:80+Math.floor(index/2)*140
            maximumWidth:380;type:modelData;title:"Edition ready"
            content:Component {ButtonLabel {text:"Create an edition to get started.";font:parent.font;color:parent.foregroundColor;wrapWidth:parent.availableWidth}}
        }
    }
    BleeckerAlert {x:28;y:370;title:"Prepare an edition";maximumWidth:380;content:window.showDetails ? details:null}
    Component {
        id:details
        Column {
            spacing:12
            BleeckerButton {property int count:0;text:"Create "+count;onClicked:count++}
            BleeckerTextField {width:240;placeholderText:"Edition title"}
        }
    }
    BleeckerAlert {
        x:470;y:370;title:"Review needed";type:"warning";maximumWidth:320
        content:Component {ButtonLabel {text:"Create an edition to get started.";font.family:parent.font.family;font.pointSize:BleeckerFonts.pointSizeForPixels(18);font.weight:Font.DemiBold;color:parent.foregroundColor;wrapWidth:parent.availableWidth}}
    }
    BleeckerButton {x:470;y:540;text:window.showDetails ? "Hide details":"Show details";onClicked:window.showDetails=!window.showDetails}
}
