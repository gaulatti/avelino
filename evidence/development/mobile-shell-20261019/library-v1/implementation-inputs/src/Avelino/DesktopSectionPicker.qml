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
    function segmentAt(index: int): Item { return segments.itemAt(index) }
    function validateIcon(): void {
        if (count && !icon) throw new Error("Desktop section tabs require an explicit icon Component")
    }
    Component.onCompleted: { complete = true; validateIcon() }
    onIconChanged: if (complete) validateIcon()
    onCountChanged: if (complete) validateIcon()
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
                x: index * 39
                width: 39
                height: 36
                focusPolicy: tabSelected || (index === 0 && !control.segmentsSelected()) ? Qt.StrongFocus : Qt.ClickFocus
                Accessible.role: Accessible.RadioButton
                Accessible.name: tabLabel
                Accessible.checked: tabSelected
                // The desktop Picker does not consume BleeckerAppTab's badge,
                // per-tab disabled flag, or alternate accessibility label.
                onClicked: control.selectionRequested(tabValue)
                background: Rectangle {
                    x: 4; y: 4; width: 31; height: 28
                    radius: height / 2
                    color: BleeckerTheme.nativeTextPrimary
                    visible: segment.tabSelected
                    Accessible.ignored: true
                }
                contentItem: Item {
                    Loader {
                        width: 16; height: 16
                        x: (parent.width - width) / 2; y: (parent.height - height) / 2
                        readonly property string systemImage: segment.tabSystemImage
                        readonly property var tabValue: segment.tabValue
                        readonly property bool selected: segment.tabSelected
                        readonly property real pixelSize: 16
                        readonly property color foregroundColor: segment.tabSelected
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
    function segmentsSelected(): bool {
        for (let i = 0; i < count; ++i) if (segmentAt(i).tabSelected) return true
        return false
    }
}
