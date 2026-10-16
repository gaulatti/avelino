import QtQuick
import Avelino

Window {
    id: window
    property bool chosen: false
    property int changes: 0
    width: 680; height: 360; visible: true
    title: "Avelino installed checkbox"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark = consumerDark
        BleeckerTheme.textScale = consumerTextScale
    }
    Column {
        x: 24; y: 24; spacing: 20
        BleeckerEyebrow { text: "Checkbox states" }
        BleeckerCheckbox {
            objectName: "checkbox"; text: "Keep edition"; checked: window.chosen
            onToggled: { window.chosen = checked; window.changes++ }
        }
        BleeckerCheckbox { objectName: "disabledCheckbox"; text: "Disabled selection"; checked: true; enabled: false }
        BleeckerCheckbox { objectName: "nextCheckbox"; text: "Small selection"; size: "sm" }
        BleeckerCheckbox { text: "Large selection"; size: "lg"; checked: true }
        BleeckerCheckbox { objectName: "wrappedCheckbox"; width: 160; text: "Keep selected editions available for review"; checked: true }
    }
    BleeckerTextField { objectName: "checkboxNextField"; x: 360; y: 72; width: 260; placeholderText: "Keyboard focus continues" }
}
