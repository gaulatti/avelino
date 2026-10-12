import QtQuick

Rectangle {
    id: control
    radius: BleeckerTokens.radii.ui
    color: BleeckerTheme.palette.muted
    opacity: 0.9
    Accessible.ignored: true
    readonly property bool animating: pulse.running
    SequentialAnimation on opacity {
        id: pulse
        running: control.visible && !BleeckerTheme.reducedMotion
        loops: Animation.Infinite
        onRunningChanged: if (!running) control.opacity = 0.9
        NumberAnimation {
            to: 0.45; duration: 900
            easing.type: Easing.BezierSpline
            easing.bezierCurve: [0.42, 0, 0.58, 1, 1, 1]
        }
        NumberAnimation {
            to: 0.9; duration: 900
            easing.type: Easing.BezierSpline
            easing.bezierCurve: [0.42, 0, 0.58, 1, 1, 1]
        }
    }
}
