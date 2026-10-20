import QtQuick

Item {
    id:glyph
    property bool selected:false
    property real pixelSize:13
    property bool bold:false
    property color color:BleeckerTheme.nativeTextPrimary
    // Original circle drawing; this size/weight fit remains an unapproved candidate.
    readonly property real edge:Math.round(pixelSize*(bold ? 1.2:1.15))
    readonly property real contentInset:edge/15
    implicitWidth:edge;implicitHeight:edge
    Accessible.ignored:true
    Canvas {
        id:canvas;anchors.fill:parent
        Connections {
            target:glyph
            function onSelectedChanged(){canvas.requestPaint()}
            function onColorChanged(){canvas.requestPaint()}
            function onBoldChanged(){canvas.requestPaint()}
        }
        onWidthChanged:requestPaint()
        onHeightChanged:requestPaint()
        onPaint:{
            const ctx=getContext("2d"),unit=glyph.edge/15,stroke=(glyph.bold ? 1.45:1.15)*unit
            ctx.reset();if(unit<=0)return
            ctx.strokeStyle=glyph.color;ctx.fillStyle=glyph.color;ctx.lineWidth=stroke
            ctx.beginPath();ctx.arc(width/2,height/2,(glyph.edge-2*glyph.contentInset-stroke)/2,0,Math.PI*2);ctx.stroke()
            if(glyph.selected){ctx.beginPath();ctx.arc(width/2,height/2,4.05*unit,0,Math.PI*2);ctx.fill()}
        }
    }
}
