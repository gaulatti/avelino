import QtQuick

BleeckerCard {
    id: control
    default property alias panelContent: host.data
    property string title: ""
    property bool hasTitle: title !== ""
    implicitWidth: padding * 2 + Math.max(hasTitle ? label.unwrappedWidth : 0,host.implicitWidth)
    Item {
        implicitWidth: Math.max(control.hasTitle ? label.unwrappedWidth : 0,host.implicitWidth)
        implicitHeight: (control.hasTitle ? label.height + BleeckerTokens.spacing.component : 0) + host.implicitHeight
        width: parent.width; height: implicitHeight
        OwnedText {
            id: label
            objectName: "bleeckerPanelTitle"
            text: control.title; visible: control.hasTitle
            // A present empty title retains the pinned reference's 14-unit line box.
            height: control.title === "" ? 14 : naturalHeight
            width: parent.width; wrapWidth: width
            font.pointSize: BleeckerFonts.pointSizeForPixels(16)
            font.weight: Font.DemiBold
            Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
        }
        Item {
            id: host
            objectName: "bleeckerPanelContent"
            y: control.hasTitle ? label.height + BleeckerTokens.spacing.component : 0
            width: parent.width; height: implicitHeight
            implicitWidth: childrenRect.width; implicitHeight: childrenRect.height
        }
    }
}
