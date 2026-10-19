import QtQuick
import Avelino

Window {
    id:window;width:840;height:560;visible:true;color:BleeckerTheme.palette.background
    title:"Avelino navigation and caller actions"
    property string heading:"Éditions 東京"
    property bool showHeader:true
    property bool replaceAction:false
    property var path:[{title:"Home",icon:house},{title:"Workspace"},{title:"Editions"}]
    property var requests:[]
    property int mounts:0
    property int unmounts:0
    property int count:0
    property int actions:0
    readonly property bool dark:typeof consumerDark!=="undefined" ? consumerDark:captureDark
    readonly property real textScale:typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
    Component.onCompleted:{BleeckerTheme.dark=dark;BleeckerTheme.textScale=textScale;BleeckerTheme.reducedMotion=true}
    Component {id:house;BreadcrumbHouse {}}
    Loader {id:header;objectName:"headerLoader";x:24;y:40;sourceComponent:window.showHeader ? headerFactory:null}
    Component {
        id:headerFactory
        BleeckerPageHeader {
            objectName:"consumerPageHeader";width:760;eyebrow:"Workspace";title:window.heading;description:"Prepare the next edition."
            Loader {
                id:action;sourceComponent:window.replaceAction ? replacement:stateful
                readonly property real availableWidth:BleeckerLayout.proposedWidth
                BleeckerLayout.minimumWidth:item ? item.BleeckerLayout.minimumWidth:0
                BleeckerLayout.idealWidth:item ? item.BleeckerLayout.idealWidth:0
            }
            BleeckerTextField {objectName:"headerChildField";implicitWidth:180;placeholderText:"Edition title"}
        }
    }
    Component {
        id:stateful
        BleeckerButton {
            objectName:"headerChildAction";property int counter:0;text:"Create "+counter;maximumWidth:parent.availableWidth
            onClicked:{counter++;window.actions++}
            onCounterChanged:window.count=counter
            Component.onCompleted:{window.mounts++;window.count=counter}
            Component.onDestruction:window.unmounts++
        }
    }
    Component {id:replacement;BleeckerButton {text:"Replacement";maximumWidth:parent.availableWidth}}
    BleeckerBreadcrumb {objectName:"consumerBreadcrumb";x:24;y:190;items:window.path;onSelected:index=>window.requests=window.requests.concat([index])}
    BleeckerBreadcrumb {objectName:"disabledBreadcrumb";x:24;y:245;enabled:false;items:window.path}
    BleeckerBreadcrumb {objectName:"narrowBreadcrumb";x:430;y:190;maximumWidth:140;items:window.path}
    BleeckerBreadcrumb {objectName:"rtlBreadcrumb";x:24;y:310;items:window.path;LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true}
    BleeckerTextField {objectName:"navigationOutsideField";x:24;y:420;width:300;placeholderText:"Continue editing"}
}
