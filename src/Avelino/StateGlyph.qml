import QtQuick

Item {
    id:glyph
    property string symbol:"tray"
    property color color:BleeckerTheme.palette.sea
    PixelAlignment {id:metrics;target:glyph}
    // Original artwork; these standard/scaled frames are measured source
    // layout candidates. Fractional-DPR symbol presentation remains pending.
    implicitWidth:symbol==="tray" ? (metrics.devicePixelRatio<2 ? 39 : 39.5) : 35
    implicitHeight:symbol==="tray" ? (metrics.devicePixelRatio<2 ? 28 : 28.5) : (metrics.devicePixelRatio<2 ? 30 : 31)
    Accessible.ignored:true
    Canvas {
        id:canvas;anchors.fill:parent
        onWidthChanged:requestPaint()
        onHeightChanged:requestPaint()
        Connections {target:glyph;function onColorChanged(){canvas.requestPaint()} function onSymbolChanged(){canvas.requestPaint()}}
        onPaint:{
            if(glyph.symbol!=="tray" && glyph.symbol!=="error")throw new Error("Unknown presentation glyph: "+glyph.symbol)
            const ctx=getContext("2d");ctx.reset();ctx.strokeStyle=glyph.color;ctx.fillStyle=glyph.color
            ctx.lineWidth=1.8;ctx.lineCap="round";ctx.lineJoin="round"
            if(glyph.symbol==="tray"){
                ctx.beginPath();ctx.moveTo(width*0.12,height*0.60);ctx.lineTo(width*0.24,height*0.20);ctx.lineTo(width*0.76,height*0.20)
                ctx.lineTo(width*0.88,height*0.60);ctx.lineTo(width*0.88,height*0.84);ctx.lineTo(width*0.12,height*0.84);ctx.closePath();ctx.stroke()
                ctx.beginPath();ctx.moveTo(width*0.12,height*0.60);ctx.lineTo(width*0.34,height*0.60);ctx.lineTo(width*0.40,height*0.72)
                ctx.lineTo(width*0.60,height*0.72);ctx.lineTo(width*0.66,height*0.60);ctx.lineTo(width*0.88,height*0.60);ctx.stroke()
            }else{
                ctx.beginPath();ctx.moveTo(width/2,height*0.10);ctx.lineTo(width*0.92,height*0.86);ctx.lineTo(width*0.08,height*0.86);ctx.closePath();ctx.stroke()
                ctx.beginPath();ctx.moveTo(width/2,height*0.36);ctx.lineTo(width/2,height*0.58);ctx.stroke()
                ctx.beginPath();ctx.arc(width/2,height*0.72,1.2,0,Math.PI*2);ctx.fill()
            }
        }
    }
}
