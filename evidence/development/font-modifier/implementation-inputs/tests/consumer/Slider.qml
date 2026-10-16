import QtQuick
import Avelino

Window {
    id: window
    property real amount: 0.35
    property int edits: 0
    width: 740; height: 480; visible: true
    title: "Avelino installed sliders"
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark=consumerDark;BleeckerTheme.textScale=consumerTextScale;BleeckerTheme.reducedMotion=true }
    Column {
        x: 24; y: 24; width: 320; spacing: 36
        BleeckerEyebrow { text: "Bound range and input" }
        BleeckerSlider { objectName: "slider"; width: parent.width; value: window.amount; onMoved: { window.amount=value;window.edits++ } Accessible.name: "Amount" }
        BleeckerSlider { objectName: "disabledSlider"; width: parent.width; value: 0.35; enabled: false; Accessible.name: "Disabled amount" }
        BleeckerSlider { objectName: "narrowSlider"; width: 140; value: 0.35; Accessible.name: "Narrow amount" }
        BleeckerTextField { objectName: "sliderNext"; width: parent.width; placeholderText: "Continue here" }
    }
    Column {
        x: 380; y: 24; width: 336; spacing: 36
        BleeckerEyebrow { text: "Steps and endpoint math" }
        BleeckerSlider { objectName: "steppedSlider"; width: parent.width; from: 10; to: 22; stepSize: 3; value: 16; Accessible.name: "Stepped amount" }
        BleeckerSlider { objectName: "oddSlider"; width: parent.width; stepSize: 0.3; value: 0.3; Accessible.name: "Partial final interval" }
        BleeckerSlider { objectName: "decimalSlider"; width: parent.width; to: 0.3; stepSize: 0.1; value: 0.1; Accessible.name: "Decimal intervals" }
        BleeckerSlider { objectName: "denseSlider"; width: parent.width; stepSize: 0.000001; value: 0.35; Accessible.name: "Dense steps" }
    }
}
