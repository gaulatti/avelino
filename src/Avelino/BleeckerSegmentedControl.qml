import QtQuick
import QtQuick.Templates as T

T.Control {
    id: control
    required property var selection
    property var options: []
    padding: 4
    implicitWidth: row.implicitWidth+8; implicitHeight: row.implicitHeight+8
    background: ContinuousSurface {
        radius: 9; color: BleeckerTheme.alpha(BleeckerTheme.palette.muted,0.65)
        borderColor: BleeckerTheme.palette.border
    }
    contentItem: Row {
        id: row
        spacing: 2
        Repeater {
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
                focusPolicy: Qt.StrongFocus
                onClicked: control.selection = modelData.value
                contentItem: Item {
                    implicitWidth: label.unwrappedWidth; implicitHeight: label.height
                    OwnedText {
                        id: label
                        objectName: "bleeckerSegmentLabel"
                        text: segment.text; font: segment.font; y: (parent.height-height)/2
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
