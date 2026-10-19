import QtQuick

Canvas {
    required property string symbol
    property color color: BleeckerTheme.palette.textSecondary
    implicitWidth: symbol === "chevronDown" ? 11 : 14
    implicitHeight: 14
    Accessible.ignored: true
    onColorChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onSymbolChanged: requestPaint()
    onPaint: {
        const ctx=getContext("2d")
        ctx.reset(); ctx.strokeStyle=color; ctx.lineWidth=1.5
        ctx.lineCap="round"; ctx.lineJoin="round"
        ctx.beginPath()
        if (symbol === "chevronDown") {
            ctx.moveTo(width*0.15,height*0.4); ctx.lineTo(width*0.5,height*0.65); ctx.lineTo(width*0.85,height*0.4)
        } else if (symbol === "checkmark") {
            ctx.moveTo(width*0.15,height*0.5); ctx.lineTo(width*0.4,height*0.75); ctx.lineTo(width*0.85,height*0.25)
        } else throw new Error("Unknown selection glyph: "+symbol)
        ctx.stroke()
    }
}
