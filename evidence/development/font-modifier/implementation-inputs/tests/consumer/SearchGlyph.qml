import QtQuick
import Avelino

Canvas {
    implicitWidth: 14*BleeckerTheme.textScale
    implicitHeight: 14*BleeckerTheme.textScale
    property color color: BleeckerTheme.palette.sea
    Accessible.ignored: true
    onColorChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onPaint: {
        const ctx=getContext("2d")
        ctx.reset();ctx.scale(width/14,height/14)
        ctx.lineWidth=1.2;ctx.strokeStyle=color;ctx.lineCap="round"
        ctx.beginPath();ctx.arc(5.8,5.8,4.1,0,Math.PI*2);ctx.stroke()
        ctx.beginPath();ctx.moveTo(8.7,8.7);ctx.lineTo(12.8,12.8);ctx.stroke()
    }
}
