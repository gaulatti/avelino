import QtQuick
import Avelino

Window {
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    width: 680; height: 360; visible: true
    title: "Avelino — checkbox states"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark = captureDark
        BleeckerTheme.textScale = captureTextScale
    }
    Column {
        x: 24; y: 24; spacing: 20
        BleeckerEyebrow { text: "Checkbox states" }
        BleeckerCheckbox { text: "Keep edition" }
        BleeckerCheckbox { text: "Disabled selection"; checked: true; enabled: false }
        BleeckerCheckbox { text: "Small selection"; size: "sm" }
        BleeckerCheckbox { text: "Large selection"; size: "lg"; checked: true }
        BleeckerCheckbox { width: 160; text: "Keep selected editions available for review"; checked: true }
    }
}
