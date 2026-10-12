import QtQuick
import QtQuick.Templates as T

T.Control {
    id: control
    default property alias content: host.data
    font.family: BleeckerTheme.secondaryFont
    font.pointSize: BleeckerFonts.pointSizeForPixels(12)
    palette.windowText: BleeckerTheme.palette.textSecondary
    implicitWidth: host.implicitWidth
    implicitHeight: host.implicitHeight + 41
    contentItem: Item {
        BleeckerSeparator { width: parent.width }
        Item {
            id: host
            objectName: "bleeckerFooterContent"
            y: 21; width: parent.width; height: implicitHeight
            implicitWidth: childrenRect.width; implicitHeight: childrenRect.height
        }
    }
}
