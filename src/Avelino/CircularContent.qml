import QtQuick
import QtQuick.Shapes

Item {
    id:control
    default property alias content:contents.data
    property real radius:BleeckerTokens.radii.ui
    readonly property bool roundedClipping:outline.rendererType===Shape.CurveRenderer
    clip:true;containmentMask:outline
    Item {id:contents;anchors.fill:parent;clip:true}
    ShaderEffectSource {
        id:texture;sourceItem:contents;sourceRect:Qt.rect(0,0,control.width,control.height)
        hideSource:control.roundedClipping;visible:false
    }
    Shape {
        id:outline;anchors.fill:parent;preferredRendererType:Shape.CurveRenderer
        containsMode:Shape.FillContains;antialiasing:true
        ShapePath {
            fillColor:"transparent";strokeColor:"transparent";strokeWidth:-1
            fillItem:control.roundedClipping ? texture:null
            PathSvg {
                path:{
                    const w=control.width,h=control.height,r=Math.min(control.radius,w/2,h/2)
                    if(w<=0 || h<=0)return ""
                    return `M ${r} 0 H ${w-r} A ${r} ${r} 0 0 1 ${w} ${r} V ${h-r} A ${r} ${r} 0 0 1 ${w-r} ${h} H ${r} A ${r} ${r} 0 0 1 0 ${h-r} V ${r} A ${r} ${r} 0 0 1 ${r} 0 Z`
                }
            }
        }
    }
}
