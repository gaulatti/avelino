import QtQuick
import QtQuick.Shapes
import "continuouscorners.js" as Corners

Shape {
    id: surface
    property color color: "transparent"
    property color borderColor: "transparent"
    property real borderWidth: 1
    property real radius: 7
    readonly property string outerPath: Corners.svg(width, height, radius, 0)
    readonly property string borderPath: Corners.svg(width, height, radius, borderWidth / 2)
    antialiasing: true
    preferredRendererType: Shape.CurveRenderer
    ShapePath {
        fillColor: surface.color
        strokeColor: "transparent"
        strokeWidth: -1
        PathSvg { path: surface.outerPath }
    }
    ShapePath {
        fillColor: "transparent"
        strokeColor: surface.borderColor
        strokeWidth: surface.borderWidth
        PathSvg { path: surface.borderPath }
    }
}
