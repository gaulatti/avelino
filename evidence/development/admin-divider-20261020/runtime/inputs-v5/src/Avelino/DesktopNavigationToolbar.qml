import QtQuick
import QtQuick.Window
import QtQuick.Templates as T
import Avelino as A

Item {
    id: toolbar
    required property bool navigationPresented
    required property bool displayedNavigation
    signal callerToggleRequested()
    signal nativeToggleRequested()
    readonly property Item visibilityButton: nativeButton
    readonly property Item requestButton: callerButton
    implicitWidth: 104
    implicitHeight: 52
    Accessible.ignored: true

    // The native split controller and the source's explicit toolbar action are
    // separate controls. The latter toggles the caller value, even if an
    // ignoring owner leaves that value different from the displayed column.
    T.Button {
        id: nativeButton
        objectName: "bleeckerAdminNativeToggle"
        x: 8; y: (toolbar.height - height) / 2
        width: 36; height: 36
        focusPolicy: Qt.StrongFocus
        Accessible.name: qsTr("Toggle Sidebar")
        onClicked: toolbar.nativeToggleRequested()
        background: Rectangle {
            radius: height / 2
            color: A.BleeckerTheme.palette.background
            border.color: nativeButton.visualFocus ? A.BleeckerTheme.palette.ring : A.BleeckerTheme.palette.border
        }
        contentItem: Item {
            DesktopSidebarGlyph { anchors.centerIn: parent; width: 18; height: 18; color: A.BleeckerTheme.nativeTextPrimary }
        }
    }
    Rectangle {
        x: 51; y: (toolbar.height - height) / 2
        width: 1; height: 28
        color: A.BleeckerTheme.palette.border
        Accessible.ignored: true
    }
    T.Button {
        id: callerButton
        objectName: "bleeckerAdminCallerToggle"
        x: 60; y: (toolbar.height - height) / 2
        width: 36; height: 36
        focusPolicy: Qt.StrongFocus
        Accessible.name: toolbar.navigationPresented ? qsTr("Hide navigation") : qsTr("Show navigation")
        onClicked: toolbar.callerToggleRequested()
        background: Rectangle {
            radius: height / 2
            color: A.BleeckerTheme.palette.background
            border.color: callerButton.visualFocus ? A.BleeckerTheme.palette.ring : A.BleeckerTheme.palette.border
        }
        contentItem: Item {
            DesktopSidebarGlyph { anchors.centerIn: parent; width: 18; height: 18; color: A.BleeckerTheme.nativeTextPrimary }
        }
    }
    Shortcut {
        sequence: "Meta+Ctrl+S"
        context: Qt.WindowShortcut
        enabled: toolbar.enabled && toolbar.visible && toolbar.Window.window !== null
        onActivated: toolbar.callerToggleRequested()
    }
}
