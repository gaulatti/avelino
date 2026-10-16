import QtQuick

Item {
    id: control
    clip: true
    Accessible.ignored: true
    Rectangle { anchors.fill: parent; color: BleeckerTheme.palette.background }
    Rectangle {
        objectName: "bleeckerBauhausCircle"
        x: control.width * 0.72; y: -control.height * 0.18
        width: control.height * 0.62; height: width
        radius: width / 2; opacity: 0.16
        color: BleeckerTheme.palette.desert
    }
    Rectangle {
        objectName: "bleeckerBauhausBand"
        x: -control.width * 0.08; y: control.height * 0.72
        width: control.width * 0.52; height: control.height * 0.18
        opacity: 0.16; color: BleeckerTheme.palette.sea
    }
}
