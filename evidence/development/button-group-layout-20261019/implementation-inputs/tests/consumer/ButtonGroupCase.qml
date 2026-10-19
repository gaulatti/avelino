import QtQuick
import Avelino

BleeckerButtonGroup {
    id: control
    required property var definition
    readonly property string contentKind: definition.variant || "mixed-buttons"
    readonly property real offeredWidth: contentKind === "constrained-110" ? 110
        : contentKind === "wide-300" ? 300 : contentKind === "constrained-zero" ? 0
        : contentKind === "constrained-20" ? 20 : -1
    width: offeredWidth < 0 ? implicitWidth : offeredWidth
    spacing: contentKind === "spacing-zero" ? 0 : contentKind === "spacing-fractional" ? 3.5
        : contentKind === "spacing-negative" ? -4 : contentKind === "spacing-overlap" ? -200
        : contentKind === "spacing-very-large" ? 500 : BleeckerTokens.spacing.inline
    LayoutMirroring.enabled: contentKind.startsWith("rtl-")
    LayoutMirroring.childrenInherit: true
    readonly property var rows: contentRows()
    function block(name, width, height, role, hidden) {
        return {kind:"block",name:name,width:width,height:height,role:role,hidden:hidden}
    }
    function contentRows() {
        const first=block("first",80,20,"sea",false)
        const pair=[first,block("second",40,30,"desert",false)]
        switch(contentKind) {
        case "default": case "mixed-buttons": case "constrained-110": case "wide-300":
        case "constrained-zero": case "constrained-20": case "rtl-buttons":
            return [{kind:"button",name:"first",text:"Short",size:"xs"},
                    {kind:"button",name:"second",text:"Tall",size:"lg"}]
        case "absent": case "empty-group": case "conditional-absent": return []
        case "zero": return [block("first",0,0,"transparent",false)]
        case "block": case "conditional-block": return [first]
        case "two-blocks": case "group-blocks": case "spacing-zero": case "spacing-fractional":
        case "spacing-negative": case "spacing-overlap": case "spacing-very-large": case "rtl-blocks": return pair
        case "hidden-block": return [block("first",80,20,"sea",true)]
        case "zero-then-block": return [block("first",0,0,"transparent",false),block("second",80,20,"sea",false)]
        case "fractional-blocks": return [block("first",80.5,20.5,"sea",false),block("second",40.5,30.5,"desert",false)]
        default: throw new Error("Unknown button group source case: "+contentKind)
        }
    }
    component Slot: Loader {
        id: slot
        required property var modelData
        BleeckerLayout.flattenChildren: true
        sourceComponent: modelData.kind === "button" ? buttonContent : blockContent
        Component {
            id: buttonContent
            BleeckerButton { objectName:slot.modelData.name; text:slot.modelData.text; size:slot.modelData.size }
        }
        Component {
            id: blockContent
            Rectangle {
                objectName:slot.modelData.name
                width:slot.modelData.width; height:slot.modelData.height
                visible:!slot.modelData.hidden
                color:slot.modelData.role === "transparent" ? "transparent" : BleeckerTheme.palette[slot.modelData.role]
            }
        }
    }
    Repeater { model:control.contentKind === "group-blocks" ? [] : control.rows; delegate:Slot {} }
    Item {
        BleeckerLayout.flattenChildren: true
        BleeckerLayout.participates: control.contentKind === "group-blocks" || control.contentKind === "empty-group"
        Repeater { model:control.contentKind === "group-blocks" ? control.rows : []; delegate:Slot {} }
    }
}
