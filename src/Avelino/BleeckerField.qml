import QtQuick

Item {
    id: control
    default property alias content: host.data
    required property string label
    property string description: ""
    property string error: ""
    property bool optional: false
    property bool hasDescription: description !== ""
    property bool hasError: error !== ""
    implicitWidth: Math.max(heading.implicitWidth,host.implicitWidth,hasDescription ? descriptionLabel.unwrappedWidth : 0,hasError ? errorLabel.unwrappedWidth : 0)
    implicitHeight: column.implicitHeight
    Column {
        id: column
        width: control.width; spacing: 10
        Item {
            id: heading
            width: parent.width
            implicitWidth: labelText.unwrappedWidth + (control.optional ? optionalText.implicitWidth+16 : 0)
            implicitHeight: Math.max(labelText.height,control.optional ? optionalText.y+optionalText.height : 0)
            OwnedText {
                id: labelText
                objectName: "bleeckerFieldLabel"
                text: control.label; width: Math.max(0,parent.width-(control.optional ? optionalText.width+16 : 0)); wrapWidth: width
                font.pointSize: BleeckerFonts.pointSizeForPixels(13*BleeckerTheme.textScale); font.weight: Font.Medium
                Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
            }
            OwnedText {
                id: optionalText
                objectName: "bleeckerFieldOptional"
                text: qsTr("Optional"); visible: control.optional
                x: parent.width-width; y: labelText.baselineOffset-baselineOffset
                font.family: BleeckerTheme.secondaryFont
                font.pointSize: BleeckerFonts.pointSizeForPixels(11*BleeckerTheme.textScale)
                color: BleeckerTheme.palette.textSecondary
                Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
            }
        }
        Item {
            id: host
            objectName: "bleeckerFieldContent"
            width: parent.width; height: implicitHeight
            implicitWidth: childrenRect.width; implicitHeight: childrenRect.height
        }
        OwnedText {
            id: descriptionLabel
            objectName: "bleeckerFieldDescription"
            visible: control.hasDescription; text: control.description; width: parent.width; wrapWidth: width
            font.family: BleeckerTheme.secondaryFont; font.pointSize: BleeckerFonts.pointSizeForPixels(12*BleeckerTheme.textScale)
            color: BleeckerTheme.palette.textSecondary
            Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
        }
        OwnedText {
            id: errorLabel
            objectName: "bleeckerFieldError"
            visible: control.hasError; text: control.error; width: parent.width; wrapWidth: width
            font.family: BleeckerTheme.secondaryFont; font.pointSize: BleeckerFonts.pointSizeForPixels(12*BleeckerTheme.textScale)
            color: BleeckerTheme.palette.destructive
            Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
        }
    }
}
