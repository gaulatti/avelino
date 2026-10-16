import QtQuick

Canvas {
    required property bool slashed
    property color color: BleeckerTheme.palette.textSecondary
    implicitWidth: 22; implicitHeight: 20
    Accessible.ignored: true
    onSlashedChanged: requestPaint()
    onColorChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onPaint: {
        const ctx = getContext("2d")
        ctx.reset(); ctx.scale(width/22,height/20)
        ctx.strokeStyle=color; ctx.lineWidth=1.25
        ctx.lineCap="round"; ctx.lineJoin="round"
        ctx.beginPath(); ctx.moveTo(2,10)
        ctx.bezierCurveTo(6,3,16,3,20,10)
        ctx.bezierCurveTo(16,17,6,17,2,10); ctx.closePath(); ctx.stroke()
        ctx.beginPath(); ctx.arc(11,10,3,0,Math.PI*2); ctx.stroke()
        if (slashed) {
            ctx.beginPath(); ctx.moveTo(3,3); ctx.lineTo(19,17); ctx.stroke()
        }
    }
}
