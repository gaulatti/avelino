import QtQuick

ListView {
    id: control
    property var rows: []
    required property Component rowContent
    model: rows
    spacing: 0
    implicitHeight: contentHeight
    interactive: false
    clip: true
    delegate: Item {
        id: rowDelegate
        required property int index
        required property var modelData
        readonly property bool last: index === control.count-1
        objectName: "bleeckerDataRow" + index
        width: control.width
        height: slot.implicitHeight + 20 + (last ? 0 : 1)
        Loader {
            id: slot
            objectName: "bleeckerDataSlot" + rowDelegate.index
            property var row: rowDelegate.modelData
            property int rowIndex: rowDelegate.index
            x: 0; y: 10; width: parent.width
            sourceComponent: control.rowContent
        }
        BleeckerSeparator {
            objectName: "bleeckerDataSeparator" + rowDelegate.index
            anchors.bottom: parent.bottom; width: parent.width; visible: !rowDelegate.last
        }
    }
}
