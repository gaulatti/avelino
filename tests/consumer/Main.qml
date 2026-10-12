import QtQuick
import Avelino
Window {
    property int invocations: 0
    width: 400; height: 240; visible: true
    color: BleeckerTheme.palette.background
    Column {
        x: 24; y: 24; spacing: 16
        BleeckerButton { objectName: "button"; text: "Installed package"; onClicked: invocations++ }
        BleeckerTextField { objectName: "field"; placeholderText: "Edit here" }
    }
}
