import QtQuick

Item {
    id:icon
    property string symbol:"chart.line.uptrend.xyaxis"
    property color color:parent.foregroundColor
    property real pixelSize:parent.pixelSize
    implicitWidth:pixelSize*1.2;implicitHeight:pixelSize*1.15
    Accessible.ignored:true
    Canvas {
        id:canvas;anchors.fill:parent
        Connections {target:icon;function onColorChanged(){canvas.requestPaint()} function onSymbolChanged(){canvas.requestPaint()}}
        onPaint:{
            const c=getContext("2d");c.reset();c.strokeStyle=icon.color;c.lineWidth=Math.max(1,icon.pixelSize*.085);c.lineCap="round";c.lineJoin="round";c.beginPath()
            if(icon.symbol==="chart.line.uptrend.xyaxis") {c.moveTo(width*.1,height*.1);c.lineTo(width*.1,height*.9);c.lineTo(width*.9,height*.9);c.moveTo(width*.2,height*.65);c.lineTo(width*.4,height*.42);c.lineTo(width*.6,height*.6);c.lineTo(width*.9,height*.15);c.lineTo(width*.64,height*.2);c.moveTo(width*.9,height*.15);c.lineTo(width*.87,height*.4)}
            else if(icon.symbol==="minus"){c.moveTo(width*.15,height*.5);c.lineTo(width*.85,height*.5)}
            else if(icon.symbol==="house"){c.moveTo(width*.05,height*.45);c.lineTo(width*.5,height*.08);c.lineTo(width*.95,height*.45);c.moveTo(width*.2,height*.35);c.lineTo(width*.2,height*.9);c.lineTo(width*.4,height*.9);c.lineTo(width*.4,height*.64);c.lineTo(width*.6,height*.64);c.lineTo(width*.6,height*.9);c.lineTo(width*.8,height*.9);c.lineTo(width*.8,height*.35)}
            else if(icon.symbol==="arrow.left.arrow.right"){c.moveTo(width*.9,height*.3);c.lineTo(width*.1,height*.3);c.lineTo(width*.3,height*.1);c.moveTo(width*.1,height*.3);c.lineTo(width*.3,height*.5);c.moveTo(width*.1,height*.7);c.lineTo(width*.9,height*.7);c.lineTo(width*.7,height*.5);c.moveTo(width*.9,height*.7);c.lineTo(width*.7,height*.9)}
            else throw new Error("Unsupported metric fixture symbol: "+icon.symbol)
            c.stroke()
        }
    }
}
