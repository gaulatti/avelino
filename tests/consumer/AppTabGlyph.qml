import QtQuick
import Avelino
import "apptabfixturemetrics.js" as Metrics

Item {
    id:glyph
    property string symbol:parent.systemImage
    property bool selected:parent.selected
    property color color:parent.foregroundColor
    readonly property var measured:Metrics.metric(symbol,selected,alignment.devicePixelRatio,appTabFixtureMetrics)
    readonly property bool dimensionsAvailable:measured!==undefined &&typeof measured.width==="number" &&typeof measured.height==="number"
    implicitWidth:measured.width;implicitHeight:measured.height
    PixelAlignment {id:alignment;target:glyph}
    Accessible.ignored:true
    Canvas {
        id:canvas;anchors.fill:parent
        onWidthChanged:requestPaint()
        onHeightChanged:requestPaint()
        Connections {target:glyph;function onColorChanged(){canvas.requestPaint()}function onSymbolChanged(){canvas.requestPaint()}function onSelectedChanged(){canvas.requestPaint()}}
        // Original fixture artwork, with measured view boxes. It is not an
        // accepted SF-symbol substitute; strict native raster stays unresolved.
        onPaint:{
            const c=getContext("2d");c.reset()
            if(width===0 ||height===0)return
            c.strokeStyle=glyph.color;c.lineWidth=glyph.selected ? 1.8:1.35;c.lineCap="round";c.lineJoin="round"
            c.translate((width-18)/2,(height-18)/2);c.beginPath()
            if(glyph.symbol==="house"){
                c.moveTo(0.5,8);c.lineTo(9,1);c.lineTo(17.5,8)
                c.moveTo(3,6);c.lineTo(3,17);c.lineTo(7,17);c.lineTo(7,11);c.lineTo(11,11);c.lineTo(11,17);c.lineTo(15,17);c.lineTo(15,6)
            }else if(glyph.symbol==="tray"){
                c.moveTo(1,9);c.lineTo(4,4);c.lineTo(14,4);c.lineTo(17,9);c.lineTo(17,15);c.lineTo(1,15);c.closePath()
                c.moveTo(1,9);c.lineTo(6,9);c.lineTo(7,11);c.lineTo(11,11);c.lineTo(12,9);c.lineTo(17,9)
            }else if(glyph.symbol==="gearshape"){
                for(let i=0;i<32;i++){
                    const a=i*Math.PI/16,r=i%4===0 ||i%4===3 ? 8:6.5,x=9+Math.cos(a)*r,y=9+Math.sin(a)*r
                    if(i===0)c.moveTo(x,y);else c.lineTo(x,y)
                }
                c.closePath();c.moveTo(12,9);c.arc(9,9,3,0,Math.PI*2)
            }else if(glyph.symbol==="minus"){
                c.moveTo(1,9);c.lineTo(17,9)
            }else if(glyph.symbol==="arrow.left.arrow.right"){
                c.moveTo(17,5);c.lineTo(1,5);c.lineTo(5,1);c.moveTo(1,5);c.lineTo(5,9)
                c.moveTo(1,13);c.lineTo(17,13);c.lineTo(13,9);c.moveTo(17,13);c.lineTo(13,17)
            }else if(glyph.symbol==="square"){
                c.rect(1,1,16,16)
            }else throw new Error("Unsupported app-tab fixture artwork: "+glyph.symbol)
            c.stroke()
        }
    }
}
