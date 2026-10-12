import QtQuick
Item {
    id: spinner
    property string size: "md"
    property color color: BleeckerTheme.palette.sea
    implicitWidth: size === "sm" ? 16 : size === "lg" ? 32 : 20
    implicitHeight: implicitWidth
    Accessible.role: Accessible.ProgressBar
    Accessible.name: qsTr("Loading")
    Canvas {
        id: canvas
        anchors.fill: parent
        onPaint: {
            const ctx = getContext("2d")
            ctx.reset()
            ctx.strokeStyle = spinner.color
            ctx.lineWidth = 2
            ctx.beginPath()
            ctx.arc(width/2, height/2, width/2 - 2, -Math.PI/2, Math.PI)
            ctx.stroke()
        }
        Connections { target: spinner; function onColorChanged() { canvas.requestPaint() } }
        RotationAnimator on rotation { from: 0; to: 360; duration: 900; loops: Animation.Infinite; running: spinner.visible && !BleeckerTheme.reducedMotion }
    }
}
