import QtQuick
import QtQuick.Shapes
import "continuouscorners.js" as Corners

Item {
    id: control
    default property alias content: contents.data
    property real radius: BleeckerTokens.radii.card
    property bool clipsInput: true
    readonly property int rendererType: outline.rendererType
    readonly property bool softwareClipping: GraphicsInfo.api === GraphicsInfo.Software
    readonly property bool roundedClipping: softwareClipping || outline.rendererType === Shape.CurveRenderer
    clip: clipsInput
    containmentMask: clipsInput ? outline : null
    Item { id: contents; anchors.fill: parent; clip: true }
    ShaderEffectSource {
        id: texture
        sourceItem: contents
        sourceRect: Qt.rect(0,0,control.width,control.height)
        hideSource: control.roundedClipping
        visible: false
        textureMirroring: control.softwareClipping ? ShaderEffectSource.NoMirroring : ShaderEffectSource.MirrorVertically
    }
    SoftwareContentMask {
        anchors.fill: parent; visible: control.softwareClipping; source: texture; outline: clipPath
    }
    Shape {
        id: outline
        anchors.fill: parent
        preferredRendererType: Shape.CurveRenderer
        containsMode: Shape.FillContains
        antialiasing: true
        ShapePath {
            id: clipPath
            fillColor: "transparent"; strokeColor: "transparent"; strokeWidth: -1
            fillItem: outline.rendererType === Shape.CurveRenderer ? texture : null
            PathSvg { path: Corners.svg(control.width,control.height,control.radius,0) }
        }
    }
}
