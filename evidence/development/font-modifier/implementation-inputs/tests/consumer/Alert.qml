import QtQuick
import Avelino
Window {
    id:window;width:840;height:560;visible:true;color:BleeckerTheme.palette.background
    title:"Avelino installed alerts"
    property string heading:"Edition ready"
    property string kind:"info"
    property bool showContent:true
    property bool replacement:false
    property int mounts:0
    property int unmounts:0
    property int counter:0
    property int actions:0
    Component.onCompleted:{BleeckerTheme.dark=consumerDark;BleeckerTheme.textScale=consumerTextScale;BleeckerTheme.reducedMotion=true}
    BleeckerEyebrow {x:24;y:24;text:"Alerts and content"}
    BleeckerAlert {
        objectName:"consumerAlert";x:24;y:68;width:420;height:280
        title:window.heading;type:window.kind;maximumWidth:380
        content:!window.showContent ? null:window.replacement ? replacementBody:form
    }
    Component {
        id:form
        Item {
            property int count:0
            implicitWidth:240;implicitHeight:action.height+12+field.height
            onCountChanged:window.counter=count
            Component.onCompleted:{window.mounts++;window.counter=count}
            Component.onDestruction:window.unmounts++
            BleeckerButton {id:action;objectName:"alertChildAction";text:"Create "+parent.count;onClicked:{parent.count++;window.actions++}}
            BleeckerTextField {id:field;objectName:"alertChildField";y:action.height+12;width:240;placeholderText:"Edition title"}
        }
    }
    Component {id:replacementBody;ButtonLabel {text:"Replacement content";font:parent.font;color:parent.foregroundColor;wrapWidth:parent.availableWidth}}
    BleeckerAlert {
        objectName:"consumerNarrowAlert";x:500;y:80;maximumWidth:180;type:"warning";title:"Review needed"
        content:Component {ButtonLabel {text:"Create an edition to get started.";font:parent.font;color:parent.foregroundColor;wrapWidth:parent.availableWidth}}
    }
    BleeckerTextField {objectName:"alertOutsideField";x:24;y:420;width:320;placeholderText:"Continue editing"}
}
