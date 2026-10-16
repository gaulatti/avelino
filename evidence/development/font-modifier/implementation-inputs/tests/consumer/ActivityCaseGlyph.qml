import QtQuick

Item {
    id:glyph
    required property string symbol
    property real pixelSize:14.4
    property color color:"black"
    implicitWidth:symbol==="arrow.left.arrow.right" ? pixelSize*1.2:pixelSize
    implicitHeight:pixelSize
    Accessible.ignored:true
    Canvas {
        id:canvas;anchors.fill:parent
        onWidthChanged:requestPaint()
        onHeightChanged:requestPaint()
        Connections {target:glyph;function onColorChanged(){canvas.requestPaint()} function onSymbolChanged(){canvas.requestPaint()}}
        // Original fixture artwork. Native symbol raster remains unaccepted.
        onPaint:{
            const ctx=getContext("2d");ctx.reset();ctx.strokeStyle=glyph.color;ctx.lineWidth=glyph.symbol==="clock" ? 1.35:1.3;ctx.lineCap="round";ctx.lineJoin="round"
            if(glyph.symbol==="clock"){
                ctx.beginPath();ctx.arc(width/2,height/2,Math.min(width,height)*0.40,0,Math.PI*2);ctx.stroke()
                ctx.beginPath();ctx.moveTo(width/2,height*0.26);ctx.lineTo(width/2,height/2);ctx.lineTo(width*0.69,height*0.61);ctx.stroke()
            }else if(glyph.symbol==="house"){
                ctx.beginPath();ctx.moveTo(width*0.1,height*0.45);ctx.lineTo(width*0.5,height*0.12);ctx.lineTo(width*0.9,height*0.45)
                ctx.moveTo(width*0.22,height*0.37);ctx.lineTo(width*0.22,height*0.88);ctx.lineTo(width*0.78,height*0.88);ctx.lineTo(width*0.78,height*0.37);ctx.stroke()
            }else if(glyph.symbol==="arrow.left.arrow.right"){
                for(const direction of [-1,1]){
                    const y=direction<0 ? height*0.32:height*0.68,tip=direction<0 ? width*0.12:width*0.88,end=direction<0 ? width*0.88:width*0.12
                    ctx.beginPath();ctx.moveTo(end,y);ctx.lineTo(tip,y);ctx.moveTo(tip-direction*width*0.2,y-height*0.18);ctx.lineTo(tip,y);ctx.lineTo(tip-direction*width*0.2,y+height*0.18);ctx.stroke()
                }
            }else throw new Error("Unsupported Activity fixture symbol: "+glyph.symbol)
        }
    }
}
