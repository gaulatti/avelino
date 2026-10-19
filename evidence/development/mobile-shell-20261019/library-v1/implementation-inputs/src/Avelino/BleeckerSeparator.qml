import QtQuick

Rectangle {
    property bool vertical: false
    implicitWidth: vertical ? 1 : 0
    implicitHeight: vertical ? 0 : 1
    color: BleeckerTheme.palette.border
    Accessible.ignored: true
}
