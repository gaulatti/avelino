pragma Singleton
pragma FunctionSignatureBehavior: Enforced
import QtQuick
import QtQuick.Templates as T

QtObject {
    id:host
    property QtObject owner:null
    readonly property TooltipWindowLifecycle windowLifecycle:TooltipWindowLifecycle {target:popup.contentItem}
    readonly property T.ToolTip presentation:T.ToolTip {
        id:popup;objectName:"bleeckerTooltipPresentation"
        popupType:T.Popup.Window
        focus:false;modal:false;dim:false;margins:0
        padding:0;leftPadding:6.5;rightPadding:6.5;topPadding:4;bottomPadding:4
        implicitWidth:Math.ceil(label.implicitWidth)+leftPadding+rightPadding
        implicitHeight:Math.max(13,Math.ceil(label.naturalHeight))+topPadding+bottomPadding
        onClosed:host.owner=null
        onParentChanged:if(!parent)close()
        contentItem:OwnedText {
            id:label;objectName:"bleeckerTooltipText"
            text:popup.text
            font.family:BleeckerTheme.primaryFont
            font.pointSize:BleeckerFonts.pointSizeForPixels(11)
            font.weight:Font.Normal
            color:BleeckerTheme.nativeTooltipForeground
            Accessible.ignored:true
        }
        background:Rectangle {
            objectName:"bleeckerTooltipBackground"
            color:BleeckerTheme.nativeTooltipBackground
            radius:5;antialiasing:true
            Accessible.ignored:true
        }
    }
    function present(next:QtObject,target:Item,text:string,point:point):void {
        if(owner===next && presentation.visible)return
        if(presentation.visible)presentation.close()
        presentation.parent=target;presentation.text=text
        presentation.x=point.x;presentation.y=point.y+18
        owner=next;presentation.open()
    }
    function dismiss(previous:QtObject):void {
        if(owner!==previous)return
        presentation.close();owner=null
    }
}
