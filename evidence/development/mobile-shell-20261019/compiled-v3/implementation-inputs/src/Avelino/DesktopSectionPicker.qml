import QtQuick
import QtQuick.Templates as T

Item {
    id: control
    required property var selection
    property var tabs: []
    property var valueIdentity: null
    property Component icon: null
    signal selectionRequested(var requestedValue)
    readonly property int count: segments.count
    readonly property Item presentationItem: presentation
    property bool complete: false
    property int displayedIndex: -1
    function segmentAt(index: int): Item { return segments.itemAt(index) }
    function validateIcon(): void {
        if (count && !icon) throw new Error("Desktop section tabs require an explicit icon Component")
    }
    function synchronizeSelection(): void {
        displayedIndex = -1
        for (let i = 0; i < count; ++i) if (segmentAt(i).tabSelected) { displayedIndex = i; break }
    }
    function activate(index: int): void {
        if (!enabled || index < 0 || index >= count) return
        displayedIndex = index
        selectionRequested(segmentAt(index).tabValue)
    }
    Component.onCompleted: { complete = true; validateIcon(); Qt.callLater(synchronizeSelection) }
    onIconChanged: if (complete) validateIcon()
    onCountChanged: if (complete) { validateIcon(); Qt.callLater(synchronizeSelection) }
    onSelectionChanged: if (complete) Qt.callLater(synchronizeSelection)
    onTabsChanged: if (complete) Qt.callLater(synchronizeSelection)
    onEnabledChanged: if (complete) Qt.callLater(synchronizeSelection)
    visible: count > 0
    implicitWidth: presentation.width
    implicitHeight: count ? 52 : 0
    Accessible.role: Accessible.Grouping
    Accessible.name: qsTr("Application section")
    AppTabOptions { id: options; tabs: control.tabs; selection: control.selection; valueIdentity: control.valueIdentity }
    Item {
        id: presentation
        width: control.count * 39
        height: 36
        x: (control.width - width) / 2
        y: (control.height - height) / 2
        Rectangle {
            anchors.fill: parent
            radius: height / 2
            color: BleeckerTheme.palette.background
            border.color: BleeckerTheme.palette.border
            Accessible.ignored: true
        }
        Repeater {
            id: segments
            model: options
            T.Button {
                id: segment
                required property int index
                required property var tabValue
                required property string tabLabel
                required property string tabSystemImage
                required property bool tabSelected
                readonly property bool selected: control.displayedIndex === index
                x: index * 39
                width: 39
                height: 36
                focusPolicy: selected || (index === 0 && control.displayedIndex < 0) ? Qt.StrongFocus : Qt.ClickFocus
                Accessible.role: Accessible.RadioButton
                Accessible.name: tabLabel
                Accessible.checked: selected
                // The desktop Picker does not consume BleeckerAppTab's badge,
                // per-tab disabled flag, or alternate accessibility label.
                onClicked: control.activate(index)
                background: Rectangle {
                    x: 4; y: 4; width: 31; height: 28
                    radius: height / 2
                    color: BleeckerTheme.nativeTextPrimary
                    visible: segment.selected
                    Accessible.ignored: true
                }
                contentItem: Item {
                    Loader {
                        width: 16; height: 16
                        x: (parent.width - width) / 2; y: (parent.height - height) / 2
                        readonly property string systemImage: segment.tabSystemImage
                        readonly property var tabValue: segment.tabValue
                        readonly property bool selected: segment.selected
                        readonly property real pixelSize: 16
                        readonly property color foregroundColor: segment.selected
                            ? BleeckerTheme.palette.background : BleeckerTheme.nativeTextPrimary
                        sourceComponent: control.icon
                        Accessible.ignored: true
                    }
                }
                Rectangle {
                    anchors.fill: parent
                    radius: height / 2
                    color: "transparent"
                    border.color: BleeckerTheme.palette.ring
                    visible: segment.visualFocus
                    Accessible.ignored: true
                }
            }
        }
    }
}
