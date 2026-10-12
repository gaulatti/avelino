import QtQuick
import QtQuick.Templates as T

T.Switch {
    id: control
    padding: 0; spacing: 12
    font.family: BleeckerTheme.primaryFont
    font.pointSize: BleeckerFonts.pointSizeForPixels(14*BleeckerTheme.textScale); font.weight: Font.Medium
    implicitWidth: implicitContentWidth; implicitHeight: Math.max(20,implicitContentHeight)
    focusPolicy: Qt.StrongFocus
    indicator: Rectangle {
        objectName: "bleeckerSwitchTrack"
        x: control.mirrored ? control.width-width : 0; y: (control.height-height)/2
        width: 36; height: 20; radius: 10
        color: control.checked ? BleeckerTheme.palette.sea : BleeckerTheme.palette.muted
        border.width: 1; border.color: control.checked ? "transparent" : BleeckerTheme.palette.border
        Item {
            objectName: "bleeckerSwitchThumb"
            x: (control.checked !== control.mirrored) ? 18 : 2; y: 2
            width: 16; height: 16
            SurfaceShadow {
                surfaceWidth: 16; surfaceHeight: 16; circular: true
                blurRadius: 1; offsetY: 1; fillColor: "white"
                shadowColor: BleeckerTheme.alpha(BleeckerTheme.palette.deepSea,0.18)
            }
            Behavior on x { NumberAnimation { duration: BleeckerTheme.reducedMotion ? 0 : BleeckerTokens.durations.standard; easing.type: Easing.BezierSpline; easing.bezierCurve: [0,0,0.58,1,1,1] } }
        }
        Behavior on color { ColorAnimation { duration: BleeckerTheme.reducedMotion ? 0 : BleeckerTokens.durations.standard; easing.type: Easing.BezierSpline; easing.bezierCurve: [0,0,0.58,1,1,1] } }
    }
    contentItem: Item {
        implicitWidth: 36+(control.text === "" ? 0 : 12+label.unwrappedWidth)
        implicitHeight: label.height
        OwnedText {
            id: label
            objectName: "bleeckerSwitchLabel"
            x: control.mirrored ? 0 : 48; y: (parent.height-height)/2
            width: Math.max(0,parent.width-48); wrapWidth: width
            text: control.text; font: control.font
        }
    }
    ContinuousSurface {
        anchors.fill: parent; color: "transparent"; radius: 4
        borderColor: BleeckerTheme.alpha(BleeckerTheme.palette.ring,0.75)
        visible: control.visualFocus; Accessible.ignored: true
    }
}
