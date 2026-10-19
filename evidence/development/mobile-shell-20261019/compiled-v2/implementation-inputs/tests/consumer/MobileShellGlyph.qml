import QtQuick

Canvas {
    id: glyph
    implicitWidth:16; implicitHeight:16
    property string symbol:parent.systemImage
    property color ink:parent.foregroundColor
    onSymbolChanged:requestPaint()
    onInkChanged:requestPaint()
    onWidthChanged:requestPaint()
    onHeightChanged:requestPaint()
    Accessible.ignored:true
    // Original caller artwork for the operator fixture. Native SF-symbol
    // shapes and toolbar raster acceptance remain pending.
    onPaint: {
        const c=getContext("2d");c.reset()
        c.strokeStyle=ink;c.lineWidth=1.4;c.lineJoin="round";c.beginPath()
        if(symbol==="newspaper") {
            c.rect(1,2,14,12);c.moveTo(4,5);c.lineTo(12,5)
            c.moveTo(4,8);c.lineTo(12,8);c.moveTo(4,11);c.lineTo(9,11)
        } else if(symbol==="bookmark") {
            c.moveTo(4,1);c.lineTo(12,1);c.lineTo(12,15);c.lineTo(8,12);c.lineTo(4,15);c.closePath()
        } else throw new Error("Unknown mobile shell fixture symbol: "+symbol)
        c.stroke()
    }
}
