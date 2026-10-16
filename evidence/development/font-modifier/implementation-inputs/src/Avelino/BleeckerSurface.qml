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
    ContinuousSurface {
        objectName: "bleeckerSurfaceBackground"
        anchors.fill: parent; radius: control.radius
        color: BleeckerTheme.palette.card; borderColor: BleeckerTheme.palette.border
    }
    RoundedContent {
        id: body
        anchors.fill: parent; radius: control.radius
        Item { id: host; objectName: "bleeckerSurfaceContent"; anchors.fill: parent }
    }
}
