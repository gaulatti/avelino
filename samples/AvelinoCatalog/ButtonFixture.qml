import QtQuick
import Avelino
Window {
    width: 240; height: 96; visible: true
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark = captureDark; BleeckerTheme.reducedMotion = true }
    BleeckerButton {
        anchors.centerIn: parent
        text: "Publish"
        variant: captureVariant
        size: captureSize
        enabled: !captureDisabled
    }
}
