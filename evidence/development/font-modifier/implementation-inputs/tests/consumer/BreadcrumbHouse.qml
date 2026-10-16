import QtQuick
import Avelino

Item {
    id:icon
    property color color:parent.foregroundColor
    PixelAlignment {id:metrics;target:icon}
    implicitWidth:metrics.devicePixelRatio<2 ? 16:17
    implicitHeight:metrics.devicePixelRatio<2 ? 15:14.5
    Accessible.ignored:true
    Canvas {
        id:canvas;anchors.fill:parent
        Connections {target:icon;function onColorChanged(){canvas.requestPaint()}}
        onPaint:{
            const c=getContext("2d");c.reset();c.strokeStyle=icon.color;c.lineWidth=1.1;c.lineJoin="round";c.lineCap="round"
            c.beginPath();c.moveTo(width*.07,height*.46);c.lineTo(width*.5,height*.08);c.lineTo(width*.93,height*.46)
            c.moveTo(width*.21,height*.38);c.lineTo(width*.21,height*.91);c.lineTo(width*.42,height*.91);c.lineTo(width*.42,height*.66)
            c.lineTo(width*.59,height*.66);c.lineTo(width*.59,height*.91);c.lineTo(width*.79,height*.91);c.lineTo(width*.79,height*.38);c.stroke()
        }
    }
}
