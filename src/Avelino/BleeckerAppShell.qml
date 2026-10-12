import QtQuick
import QtQuick.Templates as T

T.Control {
    id: control
    required property Component sidebar
    required property Component header
    required property Component content
    property real sidebarWidth: 240
    font.family: BleeckerTheme.primaryFont
    palette.windowText: BleeckerTheme.palette.textPrimary
    implicitWidth: sidebarWidth + 33 + Math.max(headerSlot.implicitWidth, contentSlot.implicitWidth) + 48
    implicitHeight: Math.max(sidebarSlot.implicitHeight + 32, headerHeight + contentSlot.implicitHeight + 49)
    readonly property real headerHeight: Math.max(64, headerSlot.implicitHeight)
    background: Rectangle { color: BleeckerTheme.palette.background }
    contentItem: Item {
        Rectangle {
            width: control.sidebarWidth + 32; height: sidebarSlot.implicitHeight + 32
            y: (parent.height - height) / 2
            color: BleeckerTheme.palette.card
            Loader {
                id: sidebarSlot
                objectName: "bleeckerAppSidebar"
                x: 16; y: 16
                width: control.sidebarWidth
                sourceComponent: control.sidebar
            }
        }
        BleeckerSeparator {
            objectName: "bleeckerAppSidebarSeparator"
            vertical: true; x: control.sidebarWidth + 32; height: parent.height
        }
        Item {
            x: control.sidebarWidth + 33
            width: Math.max(0, parent.width - x); height: parent.height
            Loader {
                id: headerSlot
                objectName: "bleeckerAppHeader"
                x: 24; y: (control.headerHeight - height) / 2
                width: Math.max(0, parent.width - 48)
                sourceComponent: control.header
            }
            BleeckerSeparator { y: control.headerHeight; width: parent.width }
            Loader {
                id: contentSlot
                objectName: "bleeckerAppContent"
                x: 24; y: control.headerHeight + 25
                width: Math.max(0, parent.width - 48)
                height: Math.max(0, parent.height - control.headerHeight - 49)
                sourceComponent: control.content
            }
        }
    }
}
