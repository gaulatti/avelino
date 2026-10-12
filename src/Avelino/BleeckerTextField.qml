import QtQuick
import QtQuick.Templates as T

T.TextField {
    id: control
    property string size: "md"
    property bool error: false
    readonly property var p: BleeckerTheme.palette
    implicitWidth: 240
    implicitHeight: Math.max(contentHeight + topPadding + bottomPadding,
                             (size === "sm" ? 36 : size === "lg" ? 44 : 40) * BleeckerTheme.textScale)
    leftPadding: size === "sm" ? 12 : size === "lg" ? 16 : 14
    rightPadding: leftPadding
    topPadding: 0
    bottomPadding: 0
    font.family: BleeckerTheme.primaryFont
    font.pixelSize: (size === "sm" ? 12 : 14) * BleeckerTheme.textScale
    color: p.textPrimary
    placeholderTextColor: p.textSecondary
    selectionColor: p.sea
    selectedTextColor: p.primaryForeground
    verticalAlignment: TextInput.AlignVCenter
    opacity: enabled ? 1 : 0.6
    focusPolicy: Qt.StrongFocus
    Accessible.name: placeholderText
    Text {
        objectName: "bleeckerTextFieldPlaceholder"
        x: control.leftPadding; y: control.topPadding
        width: Math.max(0,control.width-control.leftPadding-control.rightPadding)
        height: Math.max(0,control.height-control.topPadding-control.bottomPadding)
        text: control.placeholderText; font: control.font; color: control.placeholderTextColor
        horizontalAlignment: control.horizontalAlignment; verticalAlignment: control.verticalAlignment
        elide: Text.ElideRight; renderType: control.renderType
        visible: !control.length && !control.preeditText && (!control.activeFocus || control.horizontalAlignment !== Qt.AlignHCenter)
        Accessible.ignored: true
    }
    background: Item {
        SurfaceShadow {
            objectName: "bleeckerTextFieldShadow"
            surfaceWidth: parent.width; surfaceHeight: parent.height; radius: BleeckerTokens.radii.ui
            fillColor: control.enabled ? control.p.card : BleeckerTheme.alpha(control.p.muted,0.65)
            shadowColor: BleeckerTheme.alpha(control.activeFocus ? control.p.sea : control.p.deepSea,control.activeFocus ? 0.10 : 0.025)
            blurRadius: control.activeFocus ? 4 : 1; offsetY: 1
        }
        ContinuousSurface {
            objectName: "bleeckerTextFieldSurface"
            anchors.fill: parent; radius: BleeckerTokens.radii.ui
            color: control.enabled ? control.p.card : BleeckerTheme.alpha(control.p.muted,0.65)
            borderColor: control.error ? control.p.destructive : control.activeFocus ? BleeckerTheme.alpha(control.p.sea,0.75) : control.p.border
            Behavior on borderColor { ColorAnimation { duration: BleeckerTheme.reducedMotion ? 0 : BleeckerTokens.durations.control; easing.type: Easing.OutCubic } }
        }
    }
}
