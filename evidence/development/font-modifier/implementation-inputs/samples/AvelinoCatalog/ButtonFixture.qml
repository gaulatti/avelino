import QtQuick
import Avelino
Window {
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    width: 240; height: 96; visible: true
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark = captureDark; BleeckerTheme.reducedMotion = true; BleeckerTheme.textScale = captureTextScale }
    BleeckerButton {
        objectName: "fixtureButton"
        anchors.centerIn: parent
        anchors.alignWhenCentered: false
        text: "Publish"
        variant: captureVariant
        size: captureSize
        enabled: !captureDisabled
    }
}
