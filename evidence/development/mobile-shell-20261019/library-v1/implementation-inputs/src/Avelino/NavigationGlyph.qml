import QtQuick

Item {
    id: glyph
    required property string direction
    property real pixelSize: 13
    property color color: BleeckerTheme.palette.textPrimary
    implicitWidth: 16; implicitHeight: 16
    Accessible.ignored: true
    // The source icon frame does not crop a larger text-scaled symbol.
    Canvas {
        id: canvas
        anchors.centerIn: parent
        width: Math.max(glyph.width,glyph.pixelSize*1.2)
        height: Math.max(glyph.height,glyph.pixelSize*1.2)
        Accessible.ignored: true
        Connections {
            target: glyph
            function onColorChanged() {canvas.requestPaint()}
            function onPixelSizeChanged() {canvas.requestPaint()}
            function onDirectionChanged() {canvas.requestPaint()}
        }
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
        onPaint: {
            if (glyph.direction !== "left" && glyph.direction !== "right") throw new Error("Unknown navigation glyph: "+glyph.direction)
            const ctx=getContext("2d"),size=glyph.pixelSize
            ctx.reset();ctx.strokeStyle=glyph.color;ctx.lineWidth=size*0.0935
            ctx.lineCap="round";ctx.lineJoin="round"
            const sign=glyph.direction === "right" ? 1 : -1,center=width/2+sign*size*0.075
            ctx.beginPath()
            ctx.moveTo(center-sign*size*0.20,height/2-size*0.375)
            ctx.lineTo(center+sign*size*0.20,height/2)
            ctx.lineTo(center-sign*size*0.20,height/2+size*0.375)
            ctx.stroke()
        }
    }
}
