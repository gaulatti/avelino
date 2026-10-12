import QtQuick
import Avelino
Window {
    property int invocations: 0
    width: 400; height: 240; visible: true
    title: "Avelino installed consumer"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark = consumerDark
        BleeckerTheme.textScale = consumerTextScale
        BleeckerTheme.reducedMotion = true
    }
    Column {
        x: 24.23; y: 24.17; spacing: 16
        BleeckerButton { objectName: "button"; text: "Installed package"; onClicked: invocations++ }
        BleeckerButton { objectName: "fractionalButton"; text: "Fractional size"; size: "sm" }
        BleeckerTextField { objectName: "field"; placeholderText: "Edit here" }
    }
}
