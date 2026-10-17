pragma FunctionSignatureBehavior: Enforced
import QtQuick
import QtQuick.Templates as T
import Avelino

Item {
    id:root
    required property var definition
    property int mode:0
    property bool mounted:true
    property int appearances:0
    property int disappearances:0
    property int callerInstances:0
    property int actions:0
    property int counter:0
    readonly property Item control:contents.item
    readonly property Item caller:!control ? null:mode===0 ? control.partAt(0).callerItem:control
    readonly property Item button:caller ? caller.inputItem:null
    width:definition.width;height:definition.height
    function frames():var {
        if(!caller)return {}
        const p=caller.mapToItem(root,0,0),rect={x:p.x,y:p.y,width:caller.width,height:caller.height}
        return {caller:[rect],styled:[rect],root:[rect]}
    }
    component Caller:Item {
        readonly property Item inputItem:button
        width:root.definition.content==="input-overflow" ? 80:96
        height:root.definition.content==="input-overflow" ? 44:64
        Component.onCompleted:{root.appearances++;root.callerInstances++}
        Component.onDestruction:if(root)root.disappearances++
        T.Button {
            id:button;objectName:"surfaceInputButton"
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            width:root.definition.content==="input-overflow" ? 160:96
            height:root.definition.content==="input-overflow" ? 100:64
            enabled:!root.definition.disabled;focusPolicy:Qt.StrongFocus
            padding:0;background:null
            contentItem:Rectangle {color:root.definition.content==="input-clear" ? "transparent":BleeckerTheme.palette.sea}
            Accessible.name:"Surface caller"
            onClicked:root.actions++
        }
    }
    Component {id:publicScope;BleeckerSurfaceModifier {radius:root.definition.radius===null ? BleeckerTokens.radii.card:root.definition.radius;Caller {}}}
    Component {id:bareScope;Caller {}}
    ProposalOverlay {
        anchors.fill:parent
        Loader {id:contents;active:root.mounted;BleeckerLayout.flattenChildren:true;sourceComponent:root.mode===0 ? publicScope:bareScope}
    }
}
