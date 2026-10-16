import QtQuick

Item {
    id:glyph
    property real pixelSize:14.4
    property color color:BleeckerTheme.palette.sea
    implicitWidth:pixelSize;implicitHeight:pixelSize
    Accessible.ignored:true
    Canvas {
        id:canvas;anchors.fill:parent
        onWidthChanged:requestPaint()
        onHeightChanged:requestPaint()
        Connections {target:glyph;function onColorChanged(){canvas.requestPaint()}}
        // Original clock artwork. Native SF symbol equivalence is unapproved.
        onPaint:{
            const ctx=getContext("2d");ctx.reset();ctx.strokeStyle=glyph.color
            ctx.lineWidth=1.35;ctx.lineCap="round";ctx.lineJoin="round"
            ctx.beginPath();ctx.arc(width/2,height/2,Math.min(width,height)*0.40,0,Math.PI*2);ctx.stroke()
            ctx.beginPath();ctx.moveTo(width/2,height*0.26);ctx.lineTo(width/2,height/2)
            ctx.lineTo(width*0.69,height*0.61);ctx.stroke()
        }
    }
}
