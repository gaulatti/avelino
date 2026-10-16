import QtQuick

Item {
    id:glyph
    property string type:"info"
    property color color:BleeckerTheme.palette.sea
    // Actual source default context; larger/dynamic symbol slots stay caller-owned.
    PixelAlignment {id:metrics;target:glyph}
    implicitWidth:type==="error" ? (metrics.devicePixelRatio<2 ? 16:16.5):15
    implicitHeight:type==="error" && metrics.devicePixelRatio>=2 ? 14.5:15
    Accessible.ignored:true
    Canvas {
        id:canvas;anchors.fill:parent
        onWidthChanged:requestPaint()
        onHeightChanged:requestPaint()
        Connections {target:glyph;function onTypeChanged(){canvas.requestPaint()} function onColorChanged(){canvas.requestPaint()}}
        onPaint:{
            BleeckerValueTools.alertTypeIndex(glyph.type)
            const ctx=getContext("2d");ctx.reset();ctx.fillStyle=glyph.color;ctx.strokeStyle=glyph.color
            ctx.lineJoin="round";ctx.lineCap="round"
            if(glyph.type==="error"){
                ctx.beginPath();ctx.moveTo(width/2,0.5);ctx.lineTo(width-0.5,height-1);ctx.lineTo(0.5,height-1);ctx.closePath();ctx.fill()
            }else{ctx.beginPath();ctx.arc(width/2,height/2,Math.min(width,height)/2-0.4,0,2*Math.PI);ctx.fill()}
            ctx.globalCompositeOperation="destination-out";ctx.fillStyle="black";ctx.strokeStyle="black";ctx.lineWidth=1.6
            if(glyph.type==="success"){
                ctx.beginPath();ctx.moveTo(width*0.27,height*0.51);ctx.lineTo(width*0.44,height*0.68);ctx.lineTo(width*0.74,height*0.32);ctx.stroke()
            }else if(glyph.type==="info"){
                ctx.beginPath();ctx.arc(width/2,height*0.29,0.85,0,2*Math.PI);ctx.fill()
                ctx.fillRect(width*0.45,height*0.44,width*0.12,height*0.31);ctx.fillRect(width*0.35,height*0.70,width*0.31,height*0.09)
            }else{
                ctx.beginPath();ctx.moveTo(width/2,height*0.28);ctx.lineTo(width/2,height*0.57);ctx.stroke()
                ctx.beginPath();ctx.arc(width/2,height*0.74,0.85,0,2*Math.PI);ctx.fill()
            }
        }
    }
}
