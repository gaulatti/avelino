import QtQuick
import QtQuick.Layouts
import QtQuick.Templates as T

T.Control {
    id: control
    required property var selection
    property var options: []
    signal activated(var value)
    padding: 4
    implicitWidth: row.naturalWidth+8; implicitHeight: row.implicitHeight+8
    background: ContinuousSurface {
        radius: 9; color: BleeckerTheme.alpha(BleeckerTheme.palette.muted,0.65)
        borderColor: BleeckerTheme.palette.border
    }
    // Layout cells allocate constrained widths; the visible Row preserves the
    // source's fractional intrinsic widths and exact 2-unit natural gaps.
    RowLayout {
        id: allocation
        opacity: 0; width: control.availableWidth; height: 0; spacing: 2
        Accessible.ignored: true
    }
    contentItem: Row {
        id: row
        spacing: 2
        property int measureRevision: 0
        readonly property real naturalWidth: {
            const revision=measureRevision
            let width=Math.max(0,buttons.count-1)*spacing
            for (let i=0;i<buttons.count;i++) width+=buttons.itemAt(i).implicitWidth
            return width
        }
        readonly property bool constrained: width < naturalWidth
        Repeater {
            id: buttons
            onItemAdded: row.measureRevision++
            onItemRemoved: row.measureRevision++
            model: control.options
            T.Button {
                id: segment
                required property var modelData
                required property int index
                objectName: "bleeckerSegment"+index
                text: modelData.label; enabled: !modelData.disabled
                readonly property bool selected: control.selection === modelData.value
                font.family: BleeckerTheme.primaryFont
                font.pointSize: BleeckerFonts.pointSizeForPixels(13*BleeckerTheme.textScale); font.weight: Font.Medium
                padding: 0; leftPadding: 12; rightPadding: 12
                implicitWidth: implicitContentWidth+24; implicitHeight: Math.max(32,implicitContentHeight)
                width: row.constrained ? cell.width : implicitWidth
                y: (row.height-height)/2
                Item {
                    id: cell
                    parent: allocation
                    Layout.minimumWidth: 24
                    Layout.preferredWidth: segment.implicitWidth
                    Layout.maximumWidth: segment.implicitWidth
                    Layout.fillWidth: true
                    Accessible.ignored: true
                }
                focusPolicy: Qt.StrongFocus
                Accessible.role: Accessible.Button
                Accessible.name: text
                Accessible.description: selected ? "Selected" : "Not selected"
                onClicked: BleeckerValueTools.select(control,modelData.value)
                contentItem: Item {
                    opacity: segment.enabled ? 1 : 0.5
                    implicitWidth: label.unwrappedWidth; implicitHeight: label.height
                    OwnedText {
                        id: label
                        objectName: "bleeckerSegmentLabel"
                        text: segment.text; font: segment.font; width: parent.width; wrapWidth: row.constrained ? width : -1; y: (parent.height-height)/2
                        color: segment.selected ? BleeckerTheme.palette.sea : BleeckerTheme.palette.textSecondary
                    }
                }
                background: ContinuousSurface {
                    radius: BleeckerTokens.radii.button; borderWidth: 0
                    color: segment.selected ? BleeckerTheme.palette.card : "transparent"
                }
                ContinuousSurface {
                    anchors.fill: parent; color: "transparent"; radius: BleeckerTokens.radii.button
                    borderColor: BleeckerTheme.alpha(BleeckerTheme.palette.ring,0.75)
                    visible: segment.visualFocus; Accessible.ignored: true
                }
            }
        }
    }
}
