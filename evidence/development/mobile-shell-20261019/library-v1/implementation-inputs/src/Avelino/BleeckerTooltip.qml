pragma FunctionSignatureBehavior: Enforced
import QtQuick

QtObject {
    id:control
    required property Item target
    required property string text
    readonly property bool visible:TooltipHost.owner===control && TooltipHost.presentation.visible
    readonly property QtObject presentation:TooltipHost.presentation
    readonly property TooltipAccess accessibility:TooltipAccess {target:control.target;text:control.text}
    property HoverHandler hover:null
    property bool componentReady:false
    readonly property Component hoverFactory:Component {
        HoverHandler {
            acceptedDevices:PointerDevice.Mouse | PointerDevice.TouchPad
            blocking:false
            onHoveredChanged:{
                if(hovered && control.target && control.text.length>0)
                    TooltipHost.present(control,control.target,control.text,point.position)
                else TooltipHost.dismiss(control)
            }
        }
    }
    readonly property Connections lifecycle:Connections {
        target:control.target
        function onVisibleChanged(){if(!control.target || !control.target.visible)TooltipHost.dismiss(control)}
        function onWindowChanged(){TooltipHost.dismiss(control)}
    }
    readonly property Connections windowLifecycle:Connections {
        id:windowEvents
        target:control.target ? control.target.Window.window:null
        function onVisibleChanged(){if(windowEvents.target && !windowEvents.target.visible)TooltipHost.dismiss(control)}
    }
    function retarget():void {
        TooltipHost.dismiss(control)
        if(hover){hover.destroy();hover=null}
        // Pointer handlers must be constructed with an Item parent in Qt 6.8.3.
        if(target){hover=hoverFactory.createObject(target);if(!hover)throw new Error("Tooltip hover adapter could not be created")}
    }
    onTargetChanged:if(componentReady)retarget()
    Component.onCompleted:{componentReady=true;retarget()}
    Component.onDestruction:{TooltipHost.dismiss(control);if(hover)hover.destroy()}
}
