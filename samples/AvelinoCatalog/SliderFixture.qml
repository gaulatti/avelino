import QtQuick
import Avelino

Window {
    id: window
    property real amount: 0.35
    width: 700; height: 440; visible: true
    title: "Avelino — sliders"
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark=captureDark;BleeckerTheme.textScale=captureTextScale;BleeckerTheme.reducedMotion=true }
    Column {
        x: 24; y: 24; width: 300; spacing: 28
        BleeckerEyebrow { text: "Continuous and bound" }
        BleeckerSlider { width: parent.width; value: window.amount; onMoved: window.amount=value; Accessible.name: "Amount" }
        BleeckerSlider { width: parent.width; value: 0; Accessible.name: "Minimum" }
        BleeckerSlider { width: parent.width; value: 1; Accessible.name: "Maximum" }
        BleeckerSlider { width: parent.width; value: 0.35; enabled: false; Accessible.name: "Disabled amount" }
        BleeckerSlider { width: 140; value: 0.35; Accessible.name: "Narrow amount" }
    }
    Column {
        x: 360; y: 24; width: 316; spacing: 28
        BleeckerEyebrow { text: "Stepped ranges" }
        BleeckerSlider { width: parent.width; stepSize: 0.25; value: 0.5; Accessible.name: "Quarter steps" }
        BleeckerSlider { width: parent.width; from: -5; to: 5; stepSize: 0.5; value: -1.5; Accessible.name: "Signed amount" }
        BleeckerSlider { width: parent.width; from: 10; to: 22; stepSize: 3; value: 16; Accessible.name: "Shifted amount" }
        BleeckerSlider { width: parent.width; stepSize: 0.3; value: 0.3; Accessible.name: "Partial final interval" }
        BleeckerSlider { width: parent.width; stepSize: 0.000001; value: 0.35; Accessible.name: "Dense steps" }
    }
}
