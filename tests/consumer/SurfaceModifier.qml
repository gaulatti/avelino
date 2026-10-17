import QtQuick
import Avelino

Window {
    id:window;width:1160;height:860;visible:true;title:"Avelino caller surfaces"
    color:BleeckerTheme.palette.background
    property var model:({fixture:"surface-default",radius:null,resolvedRadius:12,content:"clear",offer:null,parentLayout:"zstack",parentFont:false,parentRed:false,rtl:false,text:"Review edition",width:640,height:400})
    readonly property SurfaceModifierCase primaryFixture:primary
    function configure(values){model=Object.assign({},model,values)}
    readonly property Item flatModifier:flat
    readonly property Item stackModifier:stack
    readonly property Item inputModifier:inputSurface
    readonly property Item callerItem:caller
    readonly property Item inputItem:caller.inputItem
    readonly property Item fontCaller:fontCaller
    readonly property int activations:caller.localValue
    Component.onCompleted:{
        BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=typeof consumerDark!=="undefined" ? consumerDark:captureDark;BleeckerTheme.textScale=typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
    }
    ProposalRow {
        x:490;y:24;spacing:8
        Repeater {model:[0,12,48]
            BleeckerButton {required property real modelData;text:"Radius "+modelData;size:"xs";onClicked:window.configure({radius:modelData,resolvedRadius:modelData})}
        }
        BleeckerButton {text:"Default";size:"xs";onClicked:window.configure({radius:null,resolvedRadius:12})}
    }
    ProposalRow {
        x:490;y:76;spacing:8
        Repeater {model:["clear","opaque","text","multi","hstack","vstack"]
            BleeckerButton {required property string modelData;text:modelData;size:"xs";onClicked:window.configure({content:modelData})}
        }
    }
    SurfaceModifierCase {id:primary;x:490;y:160;definition:window.model}
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
