import QtQuick

Item {
    id: control
    default property alias content: host.data
    property string paddingSize: "md"
    property string variant: "surface"
    readonly property real padding: {
        switch (paddingSize) {
        case "none": return 0
        case "sm": return 16
        case "md": return 24
        case "lg": return 32
        default: throw new Error("Unknown Bleecker card padding: " + paddingSize)
        }
    }
    readonly property color fillColor: {
        switch (variant) {
        case "surface": case "outlined": case "elevated": return BleeckerTheme.palette.card
        case "subtle": return BleeckerTheme.alpha(BleeckerTheme.palette.lightSand,0.5)
        case "transparent": return "transparent"
        default: throw new Error("Unknown Bleecker card variant: " + variant)
        }
    }
    readonly property color borderColor: variant === "transparent" ? "transparent" : BleeckerTheme.palette.border
    readonly property color shadowColor: BleeckerTheme.alpha(BleeckerTheme.palette.deepSea,
        !BleeckerTheme.dark && (variant === "surface" || variant === "elevated") ? 0.06 : 0)
    readonly property real shadowRadius: variant === "elevated" ? 20 : 10
    readonly property real shadowOffsetY: variant === "elevated" ? 8 : 3
    readonly property bool roundedContentClipping: body.roundedClipping
    implicitWidth: host.implicitWidth + padding * 2
    implicitHeight: host.implicitHeight + padding * 2
    SurfaceShadow {
        objectName: "bleeckerCardShadow"
        surfaceWidth: control.width; surfaceHeight: control.height
        blurRadius: control.shadowRadius; offsetY: control.shadowOffsetY
        shadowColor: control.shadowColor; fillColor: control.fillColor
    }
    ContinuousSurface {
        objectName: "bleeckerCardSurface"
        anchors.fill: parent; radius: BleeckerTokens.radii.card
        color: control.fillColor; borderColor: control.borderColor
    }
    RoundedContent {
        id: body
        objectName: "bleeckerCardClip"
        anchors.fill: parent
        Item {
            id: host
            objectName: "bleeckerCardContent"
            x: control.padding; y: control.padding
            width: Math.max(0,control.width - control.padding * 2)
            height: Math.max(0,control.height - control.padding * 2)
            implicitWidth: childrenRect.width
            implicitHeight: childrenRect.height
        }
    }
}
