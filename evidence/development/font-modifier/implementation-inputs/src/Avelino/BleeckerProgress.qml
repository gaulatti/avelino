import QtQuick
import QtQuick.Templates as T

Item {
    id: control
    property real value: 0
    property string size: "md"
    property string variant: "default"
    property string accessibleName: ""
    readonly property color fillColor: {
        switch (variant) {
        case "default": return BleeckerTheme.palette.primary
        case "success": return BleeckerTheme.palette.live
        case "warning": return BleeckerTheme.palette.desert
        case "destructive": return BleeckerTheme.palette.destructive
        default: throw new Error("Unknown Bleecker progress variant: " + variant)
        }
    }
    implicitHeight: {
        switch (size) {
        case "sm": return 4
        case "md": return 7
        case "lg": return 10
        default: throw new Error("Unknown Bleecker progress size: " + size)
        }
    }
    T.ProgressBar {
        id: nativeProgress
        objectName: "bleeckerProgressControl"
        anchors.fill: parent
        from: 0; to: 1; value: control.value
        Accessible.name: control.accessibleName
        background: Rectangle {
            radius: height / 2
            color: BleeckerTheme.palette.muted
        }
        contentItem: Item {
            property real presentedPosition: nativeProgress.position
            Behavior on presentedPosition {
                NumberAnimation {
                    duration: BleeckerTheme.reducedMotion ? 0 : BleeckerTokens.durations.standard
                    easing.type: Easing.BezierSpline
                    easing.bezierCurve: [0, 0, 0.58, 1, 1, 1]
                }
            }
            Rectangle {
                objectName: "bleeckerProgressFill"
                x: nativeProgress.mirrored ? parent.width - width : 0
                width: parent.width * parent.presentedPosition
                height: parent.height
                radius: height / 2
                color: control.fillColor
            }
        }
    }
}
