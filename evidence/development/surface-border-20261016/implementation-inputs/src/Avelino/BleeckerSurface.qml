import QtQuick

Item {
    id: control
    default property alias content: host.data
    property real radius: BleeckerTokens.radii.card
    readonly property bool roundedContentClipping: body.roundedClipping
    implicitWidth: host.childrenRect.width; implicitHeight: host.childrenRect.height
    SurfaceShadow {
        objectName: "bleeckerSurfaceShadow"
        surfaceWidth: control.width; surfaceHeight: control.height; radius: control.radius
        blurRadius: 14; offsetY: 5
        shadowColor: BleeckerTheme.alpha(BleeckerTheme.palette.deepSea,BleeckerTheme.dark ? 0 : 0.055)
        fillColor: BleeckerTheme.palette.card
    }
    RoundedContent {
        id: body
        anchors.fill: parent; radius: control.radius
        Item {
            id:background;objectName:"bleeckerSurfaceBackground"
            anchors.fill:parent
            readonly property real radius:control.radius
            readonly property color color:BleeckerTheme.palette.card
            Accessible.ignored:true
            Rectangle {anchors.fill:parent;color:background.color}
        }
        Item { id: host; objectName: "bleeckerSurfaceContent"; anchors.fill: parent }
    }
    ContinuousSurface {
        objectName: "bleeckerSurfaceBorder"
        anchors.fill: parent; radius: control.radius
        borderColor: BleeckerTheme.palette.border
        Accessible.ignored: true
    }
}
