import QtQuick
import QtQuick.Templates as T
import Avelino
Window {
    property int invocations: 0
    property int groupedInvocations: 0
    property int dataInvocations: 0
    width: 680; height: 448; visible: true
    title: "Avelino installed consumer"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark = consumerDark
        BleeckerTheme.textScale = consumerTextScale
        BleeckerTheme.reducedMotion = true
    }
    BleeckerCard {
        objectName: "card"
        x: 16; y: 8; width: 368; height: 200; paddingSize: "none"
        Column {
            x: 8.23; y: 16.17; spacing: 16
            BleeckerButton { objectName: "button"; text: "Installed package"; onClicked: invocations++ }
            BleeckerButton { objectName: "fractionalButton"; text: "Fractional size"; size: "sm" }
            BleeckerTextField { objectName: "field"; placeholderText: "Edit here" }
        }
    }
    Component { id: leadingSlot; Rectangle { implicitWidth: 20; implicitHeight: 16; color: BleeckerTheme.palette.sea } }
    Component { id: centerSlot; Rectangle { implicitWidth: 30; implicitHeight: 24; color: BleeckerTheme.palette.desert } }
    Component { id: trailingSlot; Rectangle { implicitWidth: 20; implicitHeight: 16; color: BleeckerTheme.palette.live } }
    BleeckerPanel {
        objectName: "panelSurface"
        x: 16; y: 208; width: 368; height: 174; paddingSize: "none"
        variant: "transparent"
        Row {
        x: 8; y: 2; spacing: 16
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
    Row {
        x: 24; y: 392; spacing: 16
        BleeckerAttentionSurface {
            objectName: "attentionSurface"
            hue: 210; intensity: 5; width: 150; height: 44
            BleeckerEyebrow { objectName: "eyebrow"; text: "Queue" }
        }
        BleeckerStatusBadge { objectName: "statusBadge"; text: "Live"; variant: "live" }
        BleeckerNotificationBadge { objectName: "notificationBadge"; count: 100 }
    }
    Row {
        x: 412; y: 16; spacing: 12
        BleeckerAvatar { objectName: "avatar"; name: "Jane Doe"; size: "xl" }
        BleeckerAvatar { objectName: "imageAvatar"; name: "Portrait"; source: "qrc:/avelino/fixtures/avatar-wide.ppm"; size: "xl" }
    }
    Component {
        id: dataSlot
        BleeckerButton { objectName: "dataAction"+rowIndex; text: row.label; size: "sm"; onClicked: dataInvocations++ }
    }
    BleeckerDataList {
        objectName: "dataList"
        x: 412; y: 104; width: 244
        rows: [{id:1,label:"First action"},{id:2,label:"Second action"}]
        rowContent: dataSlot
    }
    BleeckerTimelineItem {
        objectName: "timeline"
        x: 412; y: 250; width: 244; title: "Published"; date: "12 Oct"; last: true
        T.Label { objectName: "timelineContentLabel"; text: "Bulletin ready"; color: palette.windowText }
    }
    BleeckerSurface {
        objectName: "surfaceModifier"
        x: 412; y: 328; width: 244; height: 80; radius: 18
        Rectangle { anchors.fill: parent; color: BleeckerTheme.palette.sea }
        BleeckerEyebrow { x: 16; y: 16; text: "Surface slot"; color: "white" }
    }
}
