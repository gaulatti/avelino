import QtQuick

Item {
    id: control
    required property real count
    readonly property string text: {
        if (!Number.isInteger(count)) throw new Error("Notification count must be an integer")
        return count > 99 ? "99+" : count.toLocaleString(Qt.locale(),"f",0)
    }
    implicitWidth: label.implicitWidth + 12
    implicitHeight: Math.max(18,label.height)
    Accessible.role: Accessible.StaticText
    Accessible.name: qsTr("%1 notifications").arg(count)
    Rectangle { objectName: "bleeckerNotificationBackground"; anchors.fill: parent; radius: height / 2; color: BleeckerTokens.colors.light.destructive }
    OwnedText {
        id: label
        objectName: "bleeckerNotificationLabel"
        x: 6; y: (parent.height - height) / 2
        text: control.text; color: "white"
        font.pointSize: BleeckerFonts.pointSizeForPixels(10); font.weight: Font.Bold
    }
}
