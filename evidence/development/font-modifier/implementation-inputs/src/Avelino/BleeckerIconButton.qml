import QtQuick

FocusScope {
    id: control
    required property Component icon
    required property string accessibilityLabel
    property string size: "md"
    property string variant: "default"
    readonly property real iconEdge: {
        if (size === "sm") return 12
        if (size === "md") return 16
        if (size === "lg") return 20
        throw new Error("Unknown icon-button size: "+size)
    }
    readonly property string buttonSize: size === "sm" ? "xs" : size === "lg" ? "md" : "sm"
    readonly property string buttonVariant: {
        if (variant === "default") return "secondary"
        if (variant === "subtle" || variant === "ghost") return variant
        throw new Error("Unknown icon-button variant: "+variant)
    }
    readonly property Item inputItem: button.inputItem
    readonly property bool down: button.down
    readonly property bool visualFocus: button.inputItem.visualFocus
    readonly property color foregroundColor: button.foregroundColor
    readonly property real glyphPixelSize: metrics.resolvedPixelSize
    property alias font: button.font
    property alias focusPolicy: button.focusPolicy
    signal clicked()
    implicitWidth: button.implicitWidth; implicitHeight: button.implicitHeight
    Accessible.ignored: true
    ButtonLabel { id: metrics; text: ""; font: button.font; visible: false; Accessible.ignored: true }
    BleeckerButton {
        id: button
        objectName: "bleeckerIconButtonStyle"
        anchors.fill: parent; focus: true
        size: control.buttonSize; variant: control.buttonVariant
        accessibleName: control.accessibilityLabel
        onClicked: control.clicked()
        contentItem: Item {
            implicitWidth: control.iconEdge; implicitHeight: control.iconEdge
            Loader {
                objectName: "bleeckerIconButtonSlot"
                anchors.centerIn: parent; width: control.iconEdge; height: width
                sourceComponent: control.icon
            }
        }
    }
    ContinuousSurface {
        objectName: "bleeckerIconButtonFocus"
        anchors.fill: parent; radius: BleeckerTokens.radii.button; color: "transparent"
        borderColor: BleeckerTheme.alpha(BleeckerTheme.palette.ring,0.75)
        visible: control.visualFocus; Accessible.ignored: true
    }
}
