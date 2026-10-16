import QtQuick
import Avelino

Window {
    property string entry: ""
    property int edits: 0
    readonly property real expectedFontPointSize: BleeckerFonts.pointSizeForPixels(14)
    width: 700; height: 400; visible: true
    title: "Avelino installed secure field"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark=consumerDark; BleeckerTheme.textScale=consumerTextScale
        BleeckerTheme.reducedMotion=true
    }
    Column {
        x: 24; y: 24; width: 300; spacing: 24
        BleeckerEyebrow { text: "Secure editing" }
        BleeckerSecureField {
            objectName: "secureField"; width: parent.width; placeholderText: "Passphrase"
            text: entry
            onTextEdited: { entry=text; edits++ }
        }
        BleeckerSecureField {
            objectName: "disabledSecureField"
            width: parent.width; placeholderText: "Disabled"; text: "Disabled entry"; enabled: false
        }
        BleeckerTextField { objectName: "secureNextField"; width: parent.width; placeholderText: "Continue here" }
    }
    Column {
        x: 360; y: 24; width: 316; spacing: 24
        BleeckerEyebrow { text: "Constrained editing" }
        BleeckerSecureField {
            objectName: "narrowSecureField"
            width: 160; placeholderText: "Passphrase"; text: "A longer fictional entry for the native fixture"
        }
    }
}
