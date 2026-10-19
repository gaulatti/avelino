import QtQuick
import QtQuick.Templates as T

T.Control {
    id: control
    required property var selection
    required property Component header
    required property Component content
    property Component footer: null
    property var tabs: []
    property var valueIdentity: null
    property Component sectionIcon: null
    signal selectionRequested(var requestedValue)
    readonly property Item toolbarItem: toolbar
    readonly property Item presentationItem: body
    readonly property Item headerItem: headerSlot.item
    readonly property Item contentSlotItem: contentSlot.item
    readonly property Item footerItem: footerSlot.item
    implicitWidth: Math.max(headerSlot.implicitWidth, contentSlot.implicitWidth, footerSlot.implicitWidth)
    implicitHeight: headerSlot.implicitHeight + 1 + contentSlot.implicitHeight + footerSlot.implicitHeight
    padding: 0
    background: null
    contentItem: null
    Accessible.ignored: true
    BleeckerLayout.minimumWidth: body.minimumWidth
    BleeckerLayout.idealWidth: implicitWidth

    // The source toolbar is outside its VStack. A Qt ApplicationWindow hosts
    // this retained item through header: shell.toolbarItem.
    DesktopSectionPicker {
        id: toolbar
        parent: null
        selection: control.selection
        tabs: control.tabs
        valueIdentity: control.valueIdentity
        icon: control.sectionIcon
        enabled: control.enabled
        onSelectionRequested: requestedValue => control.selectionRequested(requestedValue)
    }
    Item {
        id: body
        readonly property real minimumWidth: Math.max(headerSlot.minimumWidth, contentSlot.minimumWidth, footerSlot.minimumWidth)
        readonly property real minimumHeight: headerSlot.minimumHeight + contentSlot.minimumHeight + footerSlot.minimumHeight + 1
        readonly property int flexibleCount: (headerSlot.item && headerSlot.fillsHeight ? 1 : 0)
            + (contentSlot.item ? 1 : 0) + (footerSlot.item && footerSlot.fillsHeight ? 1 : 0)
        readonly property real extra: flexibleCount ? Math.max(0, height - minimumHeight) / flexibleCount : 0
        width: Math.max(control.availableWidth, minimumWidth)
        height: flexibleCount ? Math.max(control.availableHeight, minimumHeight) : minimumHeight
        x: (control.availableWidth - width) / 2
        y: (control.availableHeight - height) / 2
        ShellSlot {
            id: headerSlot
            objectName: "bleeckerMobileHeader"
            width: body.width
            height: minimumHeight + (item && fillsHeight ? body.extra : 0)
            sourceComponent: control.header
        }
        BleeckerSeparator {
            objectName: "bleeckerMobileHeaderSeparator"
            y: headerSlot.height
            width: body.width
        }
        ShellSlot {
            id: contentSlot
            objectName: "bleeckerMobileContent"
            y: headerSlot.height + 1
            width: body.width
            height: minimumHeight + (item ? body.extra : 0)
            sourceComponent: control.content
        }
        ShellSlot {
            id: footerSlot
            objectName: "bleeckerMobileFooter"
            y: contentSlot.y + contentSlot.height
            width: body.width
            height: minimumHeight + (item && fillsHeight ? body.extra : 0)
            sourceComponent: control.footer
        }
    }
}
