import QtQuick
import Avelino

Window {
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    width: 680; height: 440; visible: true
    title: "Avelino — secure fields"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark=captureDark; BleeckerTheme.textScale=captureTextScale
        BleeckerTheme.reducedMotion=true
    }
    Column {
        x: 24; y: 24; width: 300; spacing: 24
        BleeckerEyebrow { text: "Secure editing" }
        BleeckerSecureField { width: parent.width; placeholderText: "Passphrase" }
        BleeckerSecureField { width: parent.width; text: "Sample entry"; placeholderText: "Passphrase" }
        BleeckerSecureField { width: parent.width; enabled: false; text: "Disabled entry"; placeholderText: "Passphrase" }
        BleeckerSecureField { width: 160; text: "A longer fictional entry for the native fixture"; placeholderText: "Passphrase" }
    }
    Column {
        x: 360; y: 24; width: 296; spacing: 24
        BleeckerEyebrow { text: "Reveal and keyboard" }
        BleeckerSecureField {
            objectName: "galleryRevealedField"
            width: parent.width; text: "Visible sample"; placeholderText: "Passphrase"
        }
        BleeckerTextField { width: parent.width; placeholderText: "Continue here" }
    }
}
