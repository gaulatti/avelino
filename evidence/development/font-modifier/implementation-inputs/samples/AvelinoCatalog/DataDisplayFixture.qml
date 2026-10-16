import QtQuick
import QtQuick.Templates as T
import Avelino

Window {
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    width: 760; height: 620; visible: true
    title: "Avelino — data display"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark = captureDark
        BleeckerTheme.textScale = captureTextScale
        BleeckerTheme.reducedMotion = true
    }
    Component { id: rowSlot; T.Label { text: row.label; font.family: BleeckerTheme.secondaryFont; font.pixelSize: 13; color: BleeckerTheme.palette.textSecondary } }
    Column {
        x: 24; y: 24; spacing: 24
        BleeckerEyebrow { text: "Data display" }
        Row {
            spacing: 16
            Repeater { model: ["xs","sm","md","lg","xl"]; BleeckerAvatar { required property string modelData; name: "Jane Doe"; size: modelData } }
            BleeckerAvatar { name: "Emoji Developer"; source: "qrc:/avelino/fixtures/avatar-wide.ppm"; size: "xl" }
            BleeckerAvatar { name: "👩‍💻 Developer"; size: "xl" }
        }
        Row {
            spacing: 32
            BleeckerDataList {
                width: 260
                rows: [{id:1,label:"First row"},{id:2,label:"Second row"},{id:3,label:"Final row"}]
                rowContent: rowSlot
            }
            Column {
                spacing: 0
                BleeckerTimelineItem {
                    width: 390; title: "Published"; date: "12 Oct"
                    T.Label { text: "Bulletin ready"; color: palette.windowText }
                }
                BleeckerTimelineItem {
                    width: 390; title: "A longer timeline title wraps when its column is constrained"; date: "13 Oct"; last: true
                    T.Label { text: "Final entry"; color: palette.windowText }
                }
            }
        }
        Row {
            spacing: 32
            BleeckerSurface {
                width: 320; height: 100
                BleeckerEyebrow { x: 16; y: 16; text: "Default surface" }
            }
            BleeckerSurface {
                width: 320; height: 100; radius: 24
                Rectangle { anchors.fill: parent; color: BleeckerTheme.palette.sea }
                BleeckerEyebrow { x: 16; y: 16; text: "Opaque clipped slot"; color: "white" }
            }
        }
    }
}
