import QtQuick
import Avelino
Window {
    property int invocations: 0
    property int groupedInvocations: 0
    width: 400; height: 400; visible: true
    title: "Avelino installed consumer"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark = consumerDark
        BleeckerTheme.textScale = consumerTextScale
        BleeckerTheme.reducedMotion = true
    }
    Column {
        x: 24.23; y: 24.17; spacing: 16
        BleeckerButton { objectName: "button"; text: "Installed package"; onClicked: invocations++ }
        BleeckerButton { objectName: "fractionalButton"; text: "Fractional size"; size: "sm" }
        BleeckerTextField { objectName: "field"; placeholderText: "Edit here" }
    }
    Component { id: leadingSlot; Rectangle { implicitWidth: 20; implicitHeight: 16; color: BleeckerTheme.palette.sea } }
    Component { id: centerSlot; Rectangle { implicitWidth: 30; implicitHeight: 24; color: BleeckerTheme.palette.desert } }
    Component { id: trailingSlot; Rectangle { implicitWidth: 20; implicitHeight: 16; color: BleeckerTheme.palette.live } }
    Row {
        x: 24; y: 210; spacing: 16
        Column {
            width: 168; spacing: 8
            BleeckerSeparator { objectName: "separator"; width: parent.width }
            BleeckerProgress { objectName: "progress"; width: parent.width; value: 0.375; accessibleName: "Download" }
            BleeckerSkeleton { objectName: "skeleton"; width: parent.width; height: 16 }
            BleeckerBauhausBackground { objectName: "bauhaus"; width: parent.width; height: 90 }
        }
        Column {
            width: 168; spacing: 8
            BleeckerHeader { objectName: "header"; width: parent.width; leading: leadingSlot; center: centerSlot; trailing: trailingSlot }
            BleeckerPanelLayout {
                objectName: "panelLayout"; width: parent.width; height: 70
                leadingWidth: 32; trailingWidth: 48
                leading: leadingSlot; content: centerSlot; trailing: trailingSlot
            }
            BleeckerButtonGroup {
                objectName: "buttonGroup"
                BleeckerButton { objectName: "groupFirst"; text: "One"; size: "xs"; onClicked: groupedInvocations++ }
                BleeckerButton { objectName: "groupSecond"; text: "Two"; size: "xs"; onClicked: groupedInvocations++ }
            }
        }
    }
}
