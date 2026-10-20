import QtQuick

Item {
    id: control
    default property alias content: row.data
    property alias spacing: row.spacing
    readonly property Item presentationItem: row
    readonly property real proposedWidth: BleeckerLayout.proposedWidth
    BleeckerLayout.minimumWidth: row.minimumWidth
    BleeckerLayout.idealWidth: row.naturalWidth
    implicitWidth: proposedWidth < 0 ? row.naturalWidth : row.implicitWidth
    implicitHeight: row.implicitHeight
    ProposalRow {
        id: row
        objectName: "bleeckerButtonGroupContent"
        spacing: BleeckerTokens.spacing.inline
        maximumWidth: control.proposedWidth < 0 ? control.width : control.proposedWidth
        mirrored: control.LayoutMirroring.enabled
        width: implicitWidth; height: implicitHeight
        x: (control.width - width) / 2
        y: (control.height - height) / 2
    }
}
