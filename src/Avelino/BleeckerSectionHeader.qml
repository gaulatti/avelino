import QtQuick

Item {
    id: control
    required property string title
    property string subtitle: ""
    property bool hasSubtitle: subtitle !== ""
    property Component actions
    implicitWidth: Math.max(titleLabel.unwrappedWidth, hasSubtitle ? subtitleLabel.unwrappedWidth : 0) + actionSlot.implicitWidth + (actionSlot.item ? 16 : 0)
    implicitHeight: Math.max(labels.height, actionSlot.implicitHeight)
    Column {
        id: labels
        width: Math.max(0, control.width - actionSlot.width - (actionSlot.item ? 16 : 0))
        y: (control.height - height) / 2
        spacing: 3
        OwnedText {
            id: titleLabel
            objectName: "bleeckerSectionTitle"
            text: control.title; width: labels.width; wrapWidth: width
            font.pointSize: BleeckerFonts.pointSizeForPixels(17); font.weight: Font.DemiBold
            Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
        }
        OwnedText {
            id: subtitleLabel
            objectName: "bleeckerSectionSubtitle"
            text: control.subtitle; visible: control.hasSubtitle
            width: labels.width; wrapWidth: width
            font.family: BleeckerTheme.secondaryFont; font.pointSize: BleeckerFonts.pointSizeForPixels(12)
            color: BleeckerTheme.palette.textSecondary
            Accessible.ignored: !visible; Accessible.role: Accessible.StaticText; Accessible.name: text
        }
    }
    Loader {
        id: actionSlot
        objectName: "bleeckerSectionActions"
        sourceComponent: control.actions
        x: control.width - width; y: (control.height - height) / 2
    }
}
