import QtQuick
import QtQuick.Templates as T

T.Control {
    id: control
    default property alias content: host.data
    required property string title
    required property string date
    property bool last: false
    font.family: BleeckerTheme.secondaryFont
    font.pointSize: BleeckerFonts.pointSizeForPixels(13)
    palette.windowText: BleeckerTheme.palette.textSecondary
    implicitWidth: 21 + Math.max(titleLabel.unwrappedWidth + dateLabel.implicitWidth + 8,host.implicitWidth)
    implicitHeight: headerHeight + 4 + host.implicitHeight + (last ? 0 : 18)
    readonly property real headerHeight: Math.max(titleLabel.height,dateLabel.height)
    contentItem: Item {
        Rectangle {
            objectName: "bleeckerTimelineDot"
            x: 0; y: 0; width: 9; height: 9; radius: 4.5; color: BleeckerTheme.palette.sea
            Accessible.ignored: true
        }
        Rectangle {
            objectName: "bleeckerTimelineConnector"
            x: 4; y: 9; width: 1; height: Math.max(0,parent.height-9)
            visible: !control.last; color: BleeckerTheme.palette.border; Accessible.ignored: true
        }
        OwnedText {
            id: titleLabel
            objectName: "bleeckerTimelineTitle"
            x: 21; y: (control.headerHeight-height)/2
            text: control.title
            width: Math.max(0,control.availableWidth-21-dateLabel.implicitWidth-8)
            wrapWidth: width
            font.pointSize: BleeckerFonts.pointSizeForPixels(14); font.weight: Font.DemiBold
            Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
        }
        OwnedText {
            id: dateLabel
            objectName: "bleeckerTimelineDate"
            x: Math.max(21,parent.width-width); y: (control.headerHeight-height)/2
            text: control.date; font.family: BleeckerTheme.secondaryFont
            font.pointSize: BleeckerFonts.pointSizeForPixels(11); color: BleeckerTheme.palette.textSecondary
            Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
        }
        Item {
            id: host
            objectName: "bleeckerTimelineContent"
            x: 21; y: control.headerHeight+4
            width: Math.max(0,parent.width-21); height: implicitHeight
            implicitWidth: childrenRect.width; implicitHeight: childrenRect.height
        }
    }
}
