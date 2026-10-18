import QtQuick

Canvas {
    id:glyph
    property bool directory:false
    property color ink:directory ? "#59abe8":BleeckerTheme.dark ? "#dddddd":"#f5f5f5"
    implicitWidth:16;implicitHeight:16
    Accessible.ignored:true
    onInkChanged:requestPaint()
    onDirectoryChanged:requestPaint()
    onWidthChanged:requestPaint()
    onHeightChanged:requestPaint()
    onPaint:{
        const p=getContext("2d");p.reset();p.scale(width/16,height/16);p.fillStyle=ink;p.lineWidth=0.75
        p.strokeStyle=directory ? "#3887bd":BleeckerTheme.dark ? "#999999":"#aaaaaa"
        p.beginPath()
        if(directory){p.moveTo(1,4);p.lineTo(6,4);p.lineTo(8,6);p.lineTo(15,6);p.lineTo(15,14);p.lineTo(1,14)}
        else {p.moveTo(4,1);p.lineTo(10,1);p.lineTo(14,5);p.lineTo(14,15);p.lineTo(4,15)}
        p.closePath();p.fill();p.stroke()
    }
}
