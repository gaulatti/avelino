import QtQuick

Item {
    id:glyph
    property real pixelSize:13
    property color color:BleeckerTheme.palette.textPrimary
    implicitWidth:16;implicitHeight:16
    Accessible.ignored:true
    // Original cross candidate; native SF Symbol equivalence remains pending.
    Canvas {
        id:canvas;anchors.centerIn:parent
        width:Math.max(glyph.width,glyph.pixelSize*1.2);height:Math.max(glyph.height,glyph.pixelSize*1.2)
        Accessible.ignored:true
        Connections {
            target:glyph
            function onColorChanged(){canvas.requestPaint()}
            function onPixelSizeChanged(){canvas.requestPaint()}
        }
        onWidthChanged:requestPaint()
        onHeightChanged:requestPaint()
        onPaint:{
            const ctx=getContext("2d"),edge=glyph.pixelSize*0.34
            ctx.reset();ctx.strokeStyle=glyph.color;ctx.lineWidth=glyph.pixelSize*0.085;ctx.lineCap="round"
            ctx.beginPath();ctx.moveTo(width/2-edge,height/2-edge);ctx.lineTo(width/2+edge,height/2+edge)
            ctx.moveTo(width/2+edge,height/2-edge);ctx.lineTo(width/2-edge,height/2+edge);ctx.stroke()
        }
    }
}
