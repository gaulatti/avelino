import QtQuick

Canvas {
    property color color: BleeckerTheme.palette.primaryForeground
    implicitWidth: 10; implicitHeight: 10
    Accessible.ignored: true
    onColorChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onPaint: {
        const ctx = getContext("2d")
        ctx.reset(); ctx.strokeStyle = color; ctx.lineWidth = 1.8
        ctx.lineCap = "round"; ctx.lineJoin = "round"
        ctx.beginPath()
        ctx.moveTo(width * 0.1, height * 0.5)
        ctx.lineTo(width * 0.4, height * 0.8)
        ctx.lineTo(width * 0.9, height * 0.2)
        ctx.stroke()
    }
}
