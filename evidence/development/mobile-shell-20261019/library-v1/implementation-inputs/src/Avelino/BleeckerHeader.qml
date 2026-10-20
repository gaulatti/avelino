import QtQuick
import QtQuick.Layouts

Item {
    id: control
    required property Component leading
    required property Component center
    required property Component trailing
    implicitWidth: row.implicitWidth
    implicitHeight: Math.max(56, row.implicitHeight)
    RowLayout {
        id: row
        anchors.fill: parent
        spacing: BleeckerTokens.spacing.inline
        Loader {
            objectName: "bleeckerHeaderLeading"
            sourceComponent: control.leading
            Layout.alignment: Qt.AlignVCenter
        }
        Item { implicitWidth: BleeckerTokens.spacing.inline; Layout.fillWidth: true }
        Loader {
            objectName: "bleeckerHeaderCenter"
            sourceComponent: control.center
            Layout.alignment: Qt.AlignVCenter
        }
        Item { implicitWidth: BleeckerTokens.spacing.inline; Layout.fillWidth: true }
        Loader {
            objectName: "bleeckerHeaderTrailing"
            sourceComponent: control.trailing
            Layout.alignment: Qt.AlignVCenter
        }
    }
}
