import QtQuick

Canvas {
    id:glyph
    property real pixelSize:13
    property bool bold:false
    property color color:BleeckerTheme.nativeEditorPlaceholder
    PixelAlignment {id:alignment;target:glyph}
    width:(alignment.devicePixelRatio>1 ? 15:16)*pixelSize/13
    height:12*pixelSize/13
    onWidthChanged:requestPaint()
    onHeightChanged:requestPaint()
    onColorChanged:requestPaint()
    onBoldChanged:requestPaint()
    onPaint:{
        const p=getContext("2d"),s=pixelSize/13
        p.reset();p.strokeStyle=color;p.lineWidth=(bold ? 1.7:1.3)*s;p.lineCap="round";p.lineJoin="round"
        p.beginPath();p.moveTo(1.5*s,height/2);p.lineTo(width-2*s,height/2)
        p.moveTo(width-6.5*s,1.5*s);p.lineTo(width-2*s,height/2);p.lineTo(width-6.5*s,height-1.5*s);p.stroke()
    }
    Accessible.ignored:false;Accessible.role:Accessible.Graphic;Accessible.name:"Right"
}
