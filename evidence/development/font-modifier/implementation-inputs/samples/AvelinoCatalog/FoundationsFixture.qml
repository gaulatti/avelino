import QtQuick
import Avelino

Window {
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    width: 760; height: 640; visible: true
    title: "Avelino — surfaces and layouts"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark = captureDark
        BleeckerTheme.textScale = captureTextScale
        BleeckerTheme.reducedMotion = true
    }
    Component { id: leadingSlot; Rectangle { implicitWidth: 32; implicitHeight: 20; color: BleeckerTheme.palette.sea } }
    Component { id: centerSlot; Rectangle { implicitWidth: 160; implicitHeight: 24; color: BleeckerTheme.palette.desert } }
    Component { id: trailingSlot; Rectangle { implicitWidth: 90; implicitHeight: 16; color: BleeckerTheme.palette.live } }
    Component { id: panelLeading; Rectangle { color: BleeckerTheme.palette.muted } }
    Component { id: panelCenter; BleeckerBauhausBackground {} }
    Component { id: panelTrailing; Rectangle { color: BleeckerTheme.palette.card } }
    Column {
        x: 24; y: 24; width: parent.width - 48; spacing: 16
        Text {
            text: "Surfaces and layouts"
            font.family: BleeckerTheme.primaryFont; font.pixelSize: 20 * BleeckerTheme.textScale
            font.weight: Font.DemiBold; color: BleeckerTheme.palette.textPrimary
        }
        BleeckerHeader { width: parent.width; leading: leadingSlot; center: centerSlot; trailing: trailingSlot }
        BleeckerSeparator { width: parent.width }
        BleeckerPanelLayout {
            width: parent.width; height: 92; leadingWidth: 140; trailingWidth: 180
            leading: panelLeading; content: panelCenter; trailing: panelTrailing
        }
        BleeckerButtonGroup {
            BleeckerButton { text: "Short"; size: "xs" }
            BleeckerButton { text: "Tall"; size: "lg" }
        }
        Row {
            spacing: 24
            BleeckerBauhausBackground { width: 200; height: 120 }
            BleeckerSeparator { vertical: true; height: 120 }
            Column {
                spacing: 16
                BleeckerSkeleton { width: 180; height: 16; radius: 0 }
                BleeckerSkeleton { width: 180; height: 24 }
                BleeckerSkeleton { width: 180; height: 48; radius: 14 }
            }
        }
        Column {
            spacing: 12
            Repeater {
                model: ["sm", "md", "lg"]
                Row {
                    required property string modelData
                    spacing: 16
                    Repeater {
                        model: ["default", "success", "warning", "destructive"]
                        BleeckerProgress {
                            required property string modelData
                            width: 150; value: 0.45
                            size: parent.modelData; variant: modelData
                            accessibleName: variant + " progress"
                        }
                    }
                }
            }
        }
    }
}
