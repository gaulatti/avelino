import QtQuick
import QtQuick.Templates as T

T.CheckBox {
    id: control
    property string size: "md"
    readonly property real indicatorEdge: {
        if (size === "sm") return 14
        if (size === "md") return 18
        if (size === "lg") return 22
        throw new Error("Unknown checkbox size: " + size)
    }
    readonly property real labelSize: size === "sm" ? 11 : size === "lg" ? 16 : 14
    padding: 0
    spacing: size === "sm" ? 6 : 10
    font.family: BleeckerTheme.primaryFont
    font.pointSize: BleeckerFonts.pointSizeForPixels(labelSize * BleeckerTheme.textScale)
    font.weight: Font.Normal
    implicitWidth: indicatorEdge + spacing + Math.ceil(label.unwrappedWidth * metrics.devicePixelRatio) / metrics.devicePixelRatio
    implicitHeight: Math.max(indicatorEdge, implicitContentHeight)
    focusPolicy: Qt.StrongFocus
    opacity: enabled ? 1 : 0.5
    Accessible.role: Accessible.CheckBox
    Accessible.name: text
    Accessible.description: checked ? "Selected" : "Not selected"
    PixelAlignment { id: metrics; target: control }
    indicator: Rectangle {
        objectName: "bleeckerCheckboxIndicator"
        x: control.mirrored ? control.width - width : 0
        y: (control.height - height) / 2
        width: control.indicatorEdge; height: width; radius: 4
        color: control.checked ? BleeckerTheme.palette.primary : BleeckerTheme.palette.card
        border.width: 1
        border.color: control.checked ? BleeckerTheme.palette.primary : BleeckerTheme.palette.border
        Accessible.ignored: true
        CheckboxGlyph {
            objectName: "bleeckerCheckboxGlyph"
            anchors.centerIn: parent
            visible: control.checked
            color: BleeckerTheme.palette.primaryForeground
        }
    }
    contentItem: Item {
        implicitHeight: label.height
        OwnedText {
            id: label
            objectName: "bleeckerCheckboxLabel"
            x: control.mirrored ? 0 : control.indicatorEdge + control.spacing
            y: (parent.height - height) / 2
            width: Math.max(0, parent.width - control.indicatorEdge - control.spacing)
            height: text === "" ? 0 : Math.ceil(naturalHeight * metrics.devicePixelRatio) / metrics.devicePixelRatio
            wrapWidth: width
            text: control.text; font: control.font
        }
    }
    Rectangle {
        objectName: "bleeckerCheckboxFocus"
        anchors.fill: parent; radius: 4; color: "transparent"
        border.color: BleeckerTheme.alpha(BleeckerTheme.palette.ring, 0.75)
        border.width: 1; visible: control.visualFocus
        Accessible.ignored: true
    }
}
