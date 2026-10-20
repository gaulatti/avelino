import QtQuick
import QtQuick.Shapes

Item {
    id: glyph
    property color color
    Accessible.ignored: true
    // Owned sidebar presentation. Exact native symbol raster remains a
    // separate acceptance gate, alongside the surrounding window chrome.
    Shape {
        width: 18; height: 18
        scale: Math.min(glyph.width / width, glyph.height / height)
        transformOrigin: Item.TopLeft
        preferredRendererType: Shape.CurveRenderer
        ShapePath {
            strokeColor: glyph.color
            strokeWidth: 1.5
            fillColor: "transparent"
            capStyle: ShapePath.RoundCap
            joinStyle: ShapePath.RoundJoin
            PathMove { x: 3.5; y: 2.75 }
            PathLine { x: 14.5; y: 2.75 }
            PathQuad { x: 16; y: 4.25; controlX: 16; controlY: 2.75 }
            PathLine { x: 16; y: 13.75 }
            PathQuad { x: 14.5; y: 15.25; controlX: 16; controlY: 15.25 }
            PathLine { x: 3.5; y: 15.25 }
            PathQuad { x: 2; y: 13.75; controlX: 2; controlY: 15.25 }
            PathLine { x: 2; y: 4.25 }
            PathQuad { x: 3.5; y: 2.75; controlX: 2; controlY: 2.75 }
            PathMove { x: 6.5; y: 3 }
            PathLine { x: 6.5; y: 15 }
            PathMove { x: 4; y: 6 }
            PathLine { x: 4.5; y: 6 }
            PathMove { x: 4; y: 8.5 }
            PathLine { x: 4.5; y: 8.5 }
            PathMove { x: 4; y: 11 }
            PathLine { x: 4.5; y: 11 }
        }
    }
}
