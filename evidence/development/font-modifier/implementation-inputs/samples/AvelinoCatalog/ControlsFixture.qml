import QtQuick
import Avelino

Window {
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    width: 760; height: 620; visible: true
    title: "Avelino — form controls"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark = captureDark
        BleeckerTheme.textScale = captureTextScale
        BleeckerTheme.reducedMotion = true
    }
    Column {
        x: 24; y: 24; width: 336; spacing: 24
        BleeckerEyebrow { text: "Field composition" }
        BleeckerField {
            width: parent.width; label: "Title"; optional: true; description: "Visible helper text"
            BleeckerTextField { width: parent.width; placeholderText: "Title" }
        }
        BleeckerField {
            width: parent.width; label: "Required title"; error: "Enter a title"
            BleeckerTextField { width: parent.width; error: true; placeholderText: "Required" }
        }
        BleeckerTextArea { width: parent.width; minimumHeight: 140; text: "Multiline editing\nSecond line"; accessibleName: "Notes" }
    }
    Column {
        x: 400; y: 24; width: 336; spacing: 24
        BleeckerEyebrow { text: "Selection" }
        BleeckerSwitch { text: "Off" }
        BleeckerSwitch { text: "On"; checked: true }
        BleeckerSwitch { text: "Disabled"; enabled: false }
        Row {
            spacing: 12
            BleeckerToggleButton { text: "Default" }
            BleeckerToggleButton { text: "Selected"; selected: true }
            BleeckerToggleButton { text: "Outline"; variant: "outline" }
        }
        BleeckerSegmentedControl {
            options: [{value:"a",label:"One"},{value:"b",label:"Two"},{value:"c",label:"Three",disabled:true}]
            selection: "b"
        }
    }
}
