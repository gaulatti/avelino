import QtQuick
import Avelino

Window {
    id:window;width:760;height:460;visible:true;title:"Avelino caller surfaces"
    color:BleeckerTheme.palette.background
    readonly property Item flatModifier:flat
    readonly property Item stackModifier:stack
    readonly property Item inputModifier:inputSurface
    readonly property Item callerItem:caller
    readonly property Item inputItem:caller.inputItem
    readonly property Item fontCaller:fontCaller
    readonly property int activations:caller.localValue
    Component.onCompleted:{
        BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=consumerDark;BleeckerTheme.textScale=consumerTextScale
    }
    BleeckerSurfaceModifier {
        id:flat;x:24;y:24;width:200;height:100
        Rectangle {width:56;height:16;color:BleeckerTheme.palette.terracotta}
        Rectangle {width:72;height:44;color:BleeckerTheme.palette.sea}
    }
    BleeckerSurfaceModifier {
        id:stack;x:260;y:24;width:220;height:100
        ProposalRow {
            spacing:5
            Rectangle {width:56;height:16;color:BleeckerTheme.palette.terracotta}
            Rectangle {width:72;height:44;color:BleeckerTheme.palette.sea}
        }
    }
    BleeckerSurfaceModifier {
        x:24;y:170;width:440;height:100
        BleeckerFont {family:"primary";size:32;textScale:1;BleeckerText {id:fontCaller;text:"Retained caller"}}
    }
    BleeckerSurfaceModifier {
        id:inputSurface;x:24;y:320;width:300;height:100
        BleeckerButton {
            id:caller;text:"Caller "+localValue
            property int localValue:0
            onClicked:localValue++
        }
    }
}
