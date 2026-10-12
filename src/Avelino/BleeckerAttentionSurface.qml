import QtQuick
import QtQuick.Shapes
import "attentioncolors.js" as Colors

Item {
    id: control
    default property alias content: host.data
    required property real hue
    required property real intensity
    readonly property real urgency: Colors.urgency(intensity)
    readonly property color accent: {
        const rgb = Colors.components(hue,intensity)
        return Qt.rgba(rgb[0],rgb[1],rgb[2],1)
    }
    readonly property color labelAccent: {
        const rgb = Colors.labelComponents(hue,intensity,BleeckerTheme.dark)
        return Qt.rgba(rgb[0],rgb[1],rgb[2],1)
    }
    readonly property real accentOpacity: BleeckerTheme.dark ? 0.12 + urgency * 0.037 : 0.06 + urgency * 0.018
    readonly property bool roundedContentClipping: body.roundedClipping
    implicitWidth: host.implicitWidth + BleeckerTokens.spacing.component * 2
    implicitHeight: host.implicitHeight + BleeckerTokens.spacing.component * 2
    ContinuousSurface {
        anchors.fill: parent; radius: BleeckerTokens.radii.card
        color: BleeckerTheme.palette.card; borderWidth: 0
    }
    ContinuousSurface {
        anchors.fill: parent; radius: BleeckerTokens.radii.card
        fillGradient: LinearGradient {
            x1: 0; y1: control.height; x2: control.width; y2: 0
            GradientStop { position: 0; color: BleeckerTheme.alpha(control.accent,control.accentOpacity) }
            GradientStop { position: 1; color: "transparent" }
        }
        borderColor: BleeckerTheme.alpha(control.accent,BleeckerTheme.dark ? 0.24 : 0.18)
    }
    RoundedContent {
        id: body
        anchors.fill: parent
        Item {
            id: host
            objectName: "bleeckerAttentionContent"
            x: BleeckerTokens.spacing.component; y: x
            width: Math.max(0,control.width - x * 2); height: Math.max(0,control.height - y * 2)
            implicitWidth: childrenRect.width; implicitHeight: childrenRect.height
        }
    }
}
