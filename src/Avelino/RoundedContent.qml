import QtQuick
import QtQuick.Shapes
import "continuouscorners.js" as Corners

Item {
    id: control
    default property alias content: contents.data
    property real radius: BleeckerTokens.radii.card
    readonly property int rendererType: outline.rendererType
    readonly property bool roundedClipping: outline.rendererType === Shape.CurveRenderer
    clip: true
    containmentMask: outline
    Item { id: contents; anchors.fill: parent; clip: true }
    ShaderEffectSource {
        id: texture
        sourceItem: contents
        sourceRect: Qt.rect(0,0,control.width,control.height)
        hideSource: control.roundedClipping
        visible: false
    }
    Shape {
        id: outline
        anchors.fill: parent
        preferredRendererType: Shape.CurveRenderer
        containsMode: Shape.FillContains
        antialiasing: true
        ShapePath {
            fillColor: "transparent"; strokeColor: "transparent"; strokeWidth: -1
            fillItem: control.roundedClipping ? texture : null
            PathSvg { path: Corners.svg(control.width,control.height,control.radius,0) }
        }
    }
}
