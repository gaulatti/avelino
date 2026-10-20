import QtQuick

Canvas {
    required property string symbol
    property color color: BleeckerTheme.palette.textSecondary
    property real strokeWidth: symbol === "search" ? 1.4 : 2
    implicitWidth: symbol === "search" ? 16.5 : 10.5
    implicitHeight: implicitWidth
    Accessible.ignored: true
    onSymbolChanged: requestPaint()
    onColorChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onStrokeWidthChanged: requestPaint()
    onPaint: {
        const ctx=getContext("2d")
        ctx.reset(); ctx.scale(width/14,height/14)
        ctx.strokeStyle=color; ctx.lineCap="round"
        ctx.lineWidth=strokeWidth
        ctx.beginPath()
        if (symbol === "search") {
            ctx.arc(5.8,5.8,4.1,0,Math.PI*2)
            ctx.moveTo(8.7,8.7); ctx.lineTo(12.8,12.8)
        } else if (symbol === "clear") {
            ctx.moveTo(2.5,2.5); ctx.lineTo(11.5,11.5)
            ctx.moveTo(11.5,2.5); ctx.lineTo(2.5,11.5)
        } else throw new Error("Unknown input glyph: "+symbol)
        ctx.stroke()
    }
}
