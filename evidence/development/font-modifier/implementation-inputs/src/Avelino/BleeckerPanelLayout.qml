import QtQuick

Item {
    id: control
    property real leadingWidth: 240
    property real trailingWidth: 300
    required property Component leading
    required property Component content
    required property Component trailing
    implicitWidth: leadingWidth + trailingWidth + 2 + center.implicitWidth
    implicitHeight: Math.max(left.implicitHeight, center.implicitHeight, right.implicitHeight)
    Row {
        anchors.fill: parent
        spacing: 0
        Loader {
            id: left
            objectName: "bleeckerPanelLeading"
            width: control.leadingWidth; height: control.height
            sourceComponent: control.leading
        }
        BleeckerSeparator { vertical: true; height: control.height }
        Loader {
            id: center
            objectName: "bleeckerPanelContent"
            width: Math.max(0, control.width - control.leadingWidth - control.trailingWidth - 2)
            height: control.height
            sourceComponent: control.content
        }
        BleeckerSeparator { vertical: true; height: control.height }
        Loader {
            id: right
            objectName: "bleeckerPanelTrailing"
            width: control.trailingWidth; height: control.height
            sourceComponent: control.trailing
        }
    }
}
