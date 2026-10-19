import QtQuick

Item {
    id: control
    default property alias content: host.data
    required property string title
    property alias subtitle: header.subtitle
    property alias hasSubtitle: header.hasSubtitle
    property alias actions: header.actions
    implicitWidth: Math.max(header.implicitWidth, host.implicitWidth)
    implicitHeight: header.height + BleeckerTokens.spacing.component + host.implicitHeight
    BleeckerSectionHeader {
        id: header
        objectName: "bleeckerDashboardHeader"
        title: control.title; width: control.width
    }
    Item {
        id: host
        objectName: "bleeckerDashboardContent"
        y: header.height + BleeckerTokens.spacing.component
        width: control.width; height: implicitHeight
        implicitWidth: childrenRect.width; implicitHeight: childrenRect.height
    }
}
