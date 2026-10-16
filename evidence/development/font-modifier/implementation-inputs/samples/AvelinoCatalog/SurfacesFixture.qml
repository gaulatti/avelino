import QtQuick
import Avelino

Window {
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    width: 760; height: 720; visible: true
    title: "Avelino — cards and badges"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark = captureDark
        BleeckerTheme.textScale = captureTextScale
        BleeckerTheme.reducedMotion = true
    }
    Column {
        x: 24; y: 24; spacing: 24
        BleeckerEyebrow { text: "Cards and badges" }
        Row {
            spacing: 16
            Repeater {
                model: ["surface","elevated","subtle","transparent"]
                BleeckerCard {
                    id: card
                    required property string modelData
                    width: 164; height: 84; variant: modelData; paddingSize: "sm"
                    BleeckerEyebrow { text: card.modelData }
                }
            }
        }
        Row {
            spacing: 16
            BleeckerPanel { width: 340; title: "Titled panel"; BleeckerStatusBadge { text: "Ready"; variant: "live" } }
            BleeckerPanel { width: 340; BleeckerStatusBadge { text: "Title omitted"; variant: "info" } }
        }
        Row {
            spacing: 16
            Repeater {
                model: [0,5,10]
                BleeckerAttentionSurface {
                    id: attention
                    required property real modelData
                    width: 220; height: 80; hue: 210; intensity: modelData
                    BleeckerEyebrow { text: "Intensity " + attention.modelData; color: attention.labelAccent }
                }
            }
        }
        Row {
            spacing: 12
            Repeater {
                model: ["default","live","offline","warning","info"]
                BleeckerStatusBadge { required property string modelData; text: modelData; variant: modelData }
            }
        }
        Row {
            spacing: 16
            Repeater { model: [0,1,99,100]; BleeckerNotificationBadge { required property real modelData; count: modelData } }
        }
        BleeckerCard {
            width: 220; height: 90; paddingSize: "none"; variant: "transparent"
            Rectangle { anchors.fill: parent; color: BleeckerTheme.palette.sea }
            BleeckerEyebrow { x: 16; y: 16; text: "Clipped content"; color: "white" }
        }
        BleeckerCard {
            width: 220; height: 60; paddingSize: "sm"; variant: "outlined"
            BleeckerEyebrow { text: "Outlined — no shadow" }
        }
    }
}
