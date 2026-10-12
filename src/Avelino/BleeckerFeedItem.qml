import QtQuick

Item {
    id: control
    default property alias content: host.data
    required property string author
    required property string timestamp
    implicitWidth: 44 + Math.max(authorLabel.unwrappedWidth + timestampLabel.unwrappedWidth + 8, host.implicitWidth)
    implicitHeight: Math.max(32, headerHeight + 6 + host.implicitHeight) + 16
    readonly property real headerHeight: Math.max(authorLabel.height, timestampLabel.height)
    BleeckerAvatar { name: control.author; size: "sm"; y: 8 }
    Item {
        x: 44; y: 8; width: Math.max(0, control.width - 44)
        OwnedText {
            id: authorLabel
            objectName: "bleeckerFeedAuthor"
            text: control.author
            width: Math.min(unwrappedWidth, Math.max(0, parent.width - timestampLabel.width - 8)); wrapWidth: width
            y: (control.headerHeight - height) / 2
            font.pointSize: BleeckerFonts.pointSizeForPixels(13); font.weight: Font.DemiBold
            Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
        }
        OwnedText {
            id: timestampLabel
            objectName: "bleeckerFeedTimestamp"
            text: control.timestamp; x: authorLabel.width + 8; y: (control.headerHeight - height) / 2
            font.family: BleeckerTheme.secondaryFont; font.pointSize: BleeckerFonts.pointSizeForPixels(11)
            color: BleeckerTheme.palette.textSecondary
            Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
        }
        Item {
            id: host
            objectName: "bleeckerFeedContent"
            y: control.headerHeight + 6; width: parent.width; height: implicitHeight
            implicitWidth: childrenRect.width; implicitHeight: childrenRect.height
        }
    }
}
