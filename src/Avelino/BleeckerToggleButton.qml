import QtQuick
import QtQuick.Templates as T

T.Button {
    id: control
    property bool selected: false
    property string variant: "default"
    readonly property color outlineColor: {
        if (variant === "outline") return BleeckerTheme.palette.border
        if (variant === "default") return "transparent"
        throw new Error("Unknown Bleecker toggle variant: "+variant)
    }
    font.family: BleeckerTheme.primaryFont; font.pointSize: BleeckerFonts.pointSizeForPixels(14)
    padding: 0; leftPadding: 12; rightPadding: 12
    implicitWidth: implicitContentWidth+24; implicitHeight: Math.max(34,implicitContentHeight)
    focusPolicy: Qt.StrongFocus
    contentItem: Item {
        implicitWidth: label.unwrappedWidth; implicitHeight: label.height
        OwnedText {
            id: label
            objectName: "bleeckerToggleLabel"
            text: control.text; font: control.font; y: (parent.height-height)/2
            color: control.selected ? BleeckerTheme.palette.primaryForeground : BleeckerTheme.palette.textSecondary
        }
    }
    background: ContinuousSurface {
        radius: BleeckerTokens.radii.button
        color: control.selected ? BleeckerTheme.palette.primary : control.down ? BleeckerTheme.palette.muted : "transparent"
        borderColor: control.outlineColor
    }
    ContinuousSurface {
        anchors.fill: parent; radius: BleeckerTokens.radii.button; color: "transparent"
        borderColor: BleeckerTheme.alpha(BleeckerTheme.palette.ring,0.75)
        visible: control.visualFocus; Accessible.ignored: true
    }
}
