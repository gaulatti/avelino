import QtQuick

Item {
    id:glyph
    property bool increment:false
    property real pixelSize:13
    property color color:BleeckerTheme.nativeEditorPlaceholder
    // Original geometric candidate. These normalized boxes use the measured
    // default source layout; SF artwork and arbitrary inherited fonts are open.
    implicitWidth:13.5*pixelSize/13
    implicitHeight:(increment ? 12.5:3.5)*pixelSize/13
    Accessible.ignored:true
    Canvas {
        id:canvas;anchors.fill:parent
        Connections {
            target:glyph
            function onColorChanged(){canvas.requestPaint()}
            function onIncrementChanged(){canvas.requestPaint()}
            function onPixelSizeChanged(){canvas.requestPaint()}
        }
        onWidthChanged:requestPaint()
        onHeightChanged:requestPaint()
        onPaint:{
            const ctx=getContext("2d"),unit=glyph.pixelSize/13
            ctx.reset();ctx.strokeStyle=glyph.color
            ctx.lineWidth=1.1*unit;ctx.lineCap="round"
            ctx.beginPath();ctx.moveTo(2*unit,height/2);ctx.lineTo(width-2*unit,height/2);ctx.stroke()
            if(glyph.increment){ctx.beginPath();ctx.moveTo(width/2,1.5*unit);ctx.lineTo(width/2,height-1.5*unit);ctx.stroke()}
        }
    }
}
