import QtQuick
import QtQuick.Templates as T
import Avelino as A

T.Control {
    id: control
    required property Component sidebar
    required property Component header
    required property Component content
    required property bool navigationPresented
    property real sidebarWidth: 300
    property real breakpoint: 768
    signal navigationPresentedRequested(bool presented)
    readonly property bool displayedNavigation: _displayedNavigation
    readonly property Item toolbarItem: toolbar
    readonly property Item splitItem: split
    padding: 0
    background: null
    contentItem: null
    implicitWidth: sidebarWidth + Math.max(headerSlot.implicitWidth, contentSlot.implicitWidth)
    implicitHeight: Math.max(sidebarSlot.minimumHeight + 32, headerSlot.minimumHeight + 1 + contentSlot.minimumHeight)
    A.BleeckerLayout.minimumWidth: body.minimumWidth
    A.BleeckerLayout.idealWidth: implicitWidth
    Accessible.ignored: true
    A.PixelAlignment { id: alignment; target: control }
    QtObject {
        readonly property Item navigationToolbar: DesktopNavigationToolbar {
            id: toolbar
            parent: null
            navigationPresented: control.navigationPresented
            displayedNavigation: control.displayedNavigation
            enabled: control.enabled
            onCallerToggleRequested: control.requestNavigationToggle()
            onNativeToggleRequested: control.setDisplayedNavigation(!control.displayedNavigation, true)
        }
    }
    property bool _complete: false
    property bool _displayedNavigation: navigationPresented
    property bool _hasShown: navigationPresented
    property real _preferredColumnWidth: -1
    readonly property real minimumColumnWidth: Math.max(Math.min(220, sidebarWidth), sidebarSlot.minimumWidth + 32)
    readonly property real columnWidth: _preferredColumnWidth >= 0
        ? (_displayedNavigation && sidebarSlot.item ? Math.max(minimumColumnWidth, _preferredColumnWidth) : _preferredColumnWidth)
        : sidebarSlot.item ? (_hasShown ? Math.max(sidebarWidth, sidebarSlot.minimumWidth + 32) : sidebarWidth) : 144
    function synchronizeNavigation(): void {
        setDisplayedNavigation(navigationPresented, true)
    }
    function setDisplayedNavigation(value: bool, notify: bool): void {
        const changed = _displayedNavigation !== value
        _displayedNavigation = value
        if (value) _hasShown = true
        leftPane.T.SplitView.preferredWidth = value ? columnWidth : 0
        if (notify && changed) navigationPresentedRequested(value)
    }
    function setDividerPosition(position: real): void {
        if (!Number.isFinite(position)) throw new Error("Divider position must be finite")
        if (!_displayedNavigation) {
            if (position < _preferredColumnWidth / 2) return
            setDisplayedNavigation(true, true)
        }
        if (position < minimumColumnWidth / 2) {
            setDisplayedNavigation(false, true)
        } else {
            _preferredColumnWidth = Math.min(Math.max(sidebarWidth, 420), Math.max(minimumColumnWidth, position))
            setDisplayedNavigation(true, true)
        }
    }
    function requestNavigationToggle(): void { navigationPresentedRequested(!navigationPresented) }
    onNavigationPresentedChanged: if (_complete) synchronizeNavigation()
    Component.onCompleted: Qt.callLater(function() {
        _hasShown = navigationPresented
        _preferredColumnWidth = sidebarSlot.item ? sidebarWidth : 144
        _displayedNavigation = navigationPresented
        _complete = true
        leftPane.T.SplitView.preferredWidth = _displayedNavigation ? columnWidth : 0
        if (!navigationPresented) navigationPresentedRequested(false)
    })
    readonly property Item presentationItem: body
    readonly property Item sidebarItem: sidebarSlot.item
    readonly property Item headerItem: headerSlot.item
    readonly property Item contentSlotItem: contentSlot.item
    Item {
        id: body
        readonly property real detailMinimumWidth: Math.max(headerSlot.minimumWidth, contentSlot.minimumWidth)
        readonly property real detailMinimumHeight: headerSlot.minimumHeight + 1 + contentSlot.minimumHeight
        readonly property real minimumWidth: detailMinimumWidth + (control._displayedNavigation ? control.columnWidth : 0)
        readonly property real minimumHeight: Math.max(detailMinimumHeight,
            control._displayedNavigation && sidebarSlot.item ? sidebarSlot.minimumHeight + 32 : 0)
        width: Math.max(control.availableWidth, minimumWidth)
        height: Math.max(control.availableHeight, minimumHeight)
        x: (control.availableWidth - width) / 2
        y: (control.availableHeight - height) / 2
        T.SplitView {
            id: split
            anchors.fill: parent
            objectName: "bleeckerAdminSplit"
            onResizingChanged: if (!resizing && control._complete) control.setDividerPosition(leftPane.T.SplitView.preferredWidth)
            handle: Item {
                implicitWidth: 0
                containmentMask: Item { x: -8; width: 16; height: split.height }
                Rectangle {
                    objectName: "bleeckerAdminDivider"
                    x: -width
                    width: 1 / alignment.devicePixelRatio
                    height: split.height
                    visible: control.displayedNavigation
                    color: A.BleeckerTheme.nativeSeparator
                    Accessible.ignored: true
                }
            }
            Item {
                id: leftPane
                T.SplitView.preferredWidth: control._displayedNavigation ? control.columnWidth : 0
                Item {
                    width: control.columnWidth
                    height: Math.max(body.height, sidebarSlot.minimumHeight + 32)
                    visible: control._displayedNavigation
                    Rectangle {
                        objectName: "bleeckerAdminSidebarBackground"
                        x: (parent.width - width) / 2
                        width: sidebarSlot.item ? sidebarSlot.item.width + 32 : 0
                        height: parent.height
                        visible: sidebarSlot.item !== null
                        color: A.BleeckerTheme.palette.card
                    }
                    A.ShellSlot {
                        id: sidebarSlot
                        objectName: "bleeckerAdminSidebar"
                        x: 16; y: 16
                        width: control.columnWidth - 32
                        height: fillsHeight ? Math.max(0, parent.height - 32) : minimumHeight
                        sourceComponent: control.sidebar
                    }
                }
            }
            Item {
                T.SplitView.fillWidth: true
                Item {
                    id: detail
                    readonly property int flexibleCount: (headerSlot.item && headerSlot.fillsHeight ? 1 : 0) + (contentSlot.item ? 1 : 0)
                    readonly property real extra: flexibleCount ? Math.max(0, height - body.detailMinimumHeight) / flexibleCount : 0
                    width: parent.width
                    height: flexibleCount ? parent.height : body.detailMinimumHeight
                    y: (parent.height - height) / 2
                    Rectangle { anchors.fill: parent; color: A.BleeckerTheme.palette.background }
                    A.ShellSlot {
                        id: headerSlot
                        objectName: "bleeckerAdminHeader"
                        width: parent.width
                        height: minimumHeight + (item && fillsHeight ? detail.extra : 0)
                        sourceComponent: control.header
                    }
                    A.BleeckerSeparator { y: headerSlot.height; width: parent.width }
                    A.ShellSlot {
                        id: contentSlot
                        objectName: "bleeckerAdminContent"
                        y: headerSlot.height + 1
                        width: parent.width
                        height: minimumHeight + (item ? detail.extra : 0)
                        sourceComponent: control.content
                    }
                }
            }
        }
    }
}
