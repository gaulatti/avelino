import QtQuick
import Avelino

Item {
    id:icon
    property string symbol:"house"
    property color color:parent.foregroundColor
    implicitWidth:20
    implicitHeight:symbol==="minus" ? (metrics.devicePixelRatio<2 ? 4:5):symbol==="arrow.left.arrow.right" ? (metrics.devicePixelRatio<2 ? 20:21):(metrics.devicePixelRatio<2 ? 18:19)
    PixelAlignment {id:metrics;target:icon}
    Accessible.ignored:true
    Canvas {
        id:canvas;anchors.fill:parent
        Connections {target:icon;function onColorChanged(){canvas.requestPaint()} function onSymbolChanged(){canvas.requestPaint()}}
        onPaint:{
            const c=getContext("2d");c.reset();c.strokeStyle=icon.color;c.lineWidth=1.35;c.lineCap="round";c.lineJoin="round"
            c.beginPath()
            if(icon.symbol==="minus"){c.moveTo(width*.15,height/2);c.lineTo(width*.85,height/2)}
            else if(icon.symbol==="arrow.left.arrow.right"){
                c.moveTo(width*.9,height*.3);c.lineTo(width*.1,height*.3);c.lineTo(width*.3,height*.1);c.moveTo(width*.1,height*.3);c.lineTo(width*.3,height*.5)
                c.moveTo(width*.1,height*.7);c.lineTo(width*.9,height*.7);c.lineTo(width*.7,height*.5);c.moveTo(width*.9,height*.7);c.lineTo(width*.7,height*.9)
            }else if(icon.symbol==="house"){
                c.moveTo(width*.04,height*.45);c.lineTo(width*.5,height*.06);c.lineTo(width*.96,height*.45)
                c.moveTo(width*.19,height*.36);c.lineTo(width*.19,height*.94);c.lineTo(width*.41,height*.94);c.lineTo(width*.41,height*.65);c.lineTo(width*.6,height*.65);c.lineTo(width*.6,height*.94);c.lineTo(width*.81,height*.94);c.lineTo(width*.81,height*.36)
            }else throw new Error("Unsupported sidebar fixture symbol: "+icon.symbol)
            c.stroke()
        }
    }
}
