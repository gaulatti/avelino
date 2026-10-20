import QtQuick
import Avelino

BleeckerFooter {
    id: control
    required property var definition
    width: 300
    readonly property string contentKind: definition.variant === "empty" ? "empty-text" : definition.variant
    readonly property var rows: contentRows()
    function textRow(name, text) { return {kind:"text",name:name,text:text} }
    function blockRow(name, width, height, colorRole, hidden) {
        return {kind:"block",name:name,width:width,height:height,colorRole:colorRole,hidden:hidden}
    }
    function contentRows() {
        const block = blockRow("first",180,40,"sea",false)
        const two = [blockRow("first",80,20,"sea",false),blockRow("second",40,30,"desert",false)]
        switch(contentKind) {
        case "absent": case "empty-group": case "conditional-absent": return []
        case "zero": return [blockRow("first",0,0,"transparent",false)]
        case "empty-text": return [textRow("first","")]
        case "text": case "long-text": return [textRow("first",definition.text)]
        case "block": case "conditional-block": return [block]
        case "two-blocks": case "group-blocks": return two
        case "hidden-block": return [blockRow("first",180,40,"sea",true)]
        case "zero-then-block": return [blockRow("first",0,0,"transparent",false),blockRow("second",180,40,"sea",false)]
        case "two-texts": return [textRow("first","First"),textRow("second","Second")]
        case "text-and-block": return [textRow("first",definition.text),blockRow("second",180,40,"sea",false)]
        default: throw new Error("Unknown footer source case: "+contentKind)
        }
    }
    component Slot: Loader {
        id: slot
        required property var modelData
        BleeckerLayout.flattenChildren: true
        sourceComponent: slot.modelData.kind === "text" ? textContent : blockContent
        Component {
            id: textContent
            BleeckerText { objectName:slot.modelData.name; text:slot.modelData.text }
        }
        Component {
            id: blockContent
            Rectangle {
                objectName:slot.modelData.name
                width:slot.modelData.width; height:slot.modelData.height
                visible:!slot.modelData.hidden
                color:slot.modelData.colorRole === "transparent" ? "transparent" : BleeckerTheme.palette[slot.modelData.colorRole]
            }
        }
    }
    Repeater {
        model: control.contentKind === "group-blocks" ? [] : control.rows
        delegate: Slot {}
    }
    Item {
        BleeckerLayout.flattenChildren: true
        BleeckerLayout.participates: control.contentKind === "group-blocks" || control.contentKind === "empty-group"
        Repeater {
            model: control.contentKind === "group-blocks" ? control.rows : []
            delegate: Slot {}
        }
    }
}
