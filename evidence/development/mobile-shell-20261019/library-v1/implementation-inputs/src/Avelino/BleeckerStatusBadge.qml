import QtQuick

Item {
    id: control
    required property string text
    property string variant: "default"
    readonly property color foregroundColor: {
        switch (variant) {
        case "default": return BleeckerTheme.palette.textPrimary
        case "live": return BleeckerTheme.palette.live
        case "offline": return BleeckerTheme.palette.textSecondary
        case "warning": return BleeckerTheme.palette.desert
        case "info": return BleeckerTheme.palette.sea
        default: throw new Error("Unknown Bleecker status variant: " + variant)
        }
    }
    implicitWidth: label.implicitWidth + 30
    implicitHeight: Math.max(24,label.height)
    Accessible.role: Accessible.StaticText; Accessible.name: text
    Rectangle { objectName: "bleeckerStatusBackground"; anchors.fill: parent; radius: height / 2; color: BleeckerTheme.alpha(control.foregroundColor,0.1) }
    Rectangle { objectName: "bleeckerStatusDot"; x: 9; y: (parent.height - 6) / 2; width: 6; height: 6; radius: 3; color: control.foregroundColor; Accessible.ignored: true }
    OwnedText {
        id: label
        objectName: "bleeckerStatusLabel"
        x: 21; y: (parent.height - height) / 2
        text: control.text; color: control.foregroundColor
        font.pointSize: BleeckerFonts.pointSizeForPixels(11 * BleeckerTheme.textScale)
        font.weight: Font.DemiBold
    }
}
