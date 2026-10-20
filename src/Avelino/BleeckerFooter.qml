import QtQuick
import QtQuick.Templates as T

T.Control {
    id: control
    default property alias content: host.data
    font.family: BleeckerTheme.secondaryFont
    font.pointSize: BleeckerFonts.pointSizeForPixels(12)
    palette.windowText: BleeckerTheme.palette.textSecondary
    BleeckerLayout.minimumWidth: Math.max(0, host.minimumWidth - 40)
    BleeckerLayout.idealWidth: Math.max(0, host.naturalWidth - 40)
    BleeckerLayout.fillsWidth: true
    implicitWidth: BleeckerLayout.idealWidth
    implicitHeight: host.implicitHeight + 1
    contentItem: Item {
        BleeckerSeparator { width: parent.width }
        ProposalColumn {
            id: host
            objectName: "bleeckerFooterContent"
            y: 1; width: parent.width; height: implicitHeight
            padding: 20
            // The shared column pads both axes. Cancel its horizontal padding
            // in the proposal and natural width; retain each child's vertical padding.
            maximumWidth: width + 40
        }
    }
}
