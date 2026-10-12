import QtQuick
import QtQuick.Templates as T
import QtQuick.Effects

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
    background: Rectangle {
        radius: BleeckerTokens.radii.ui
        color: control.enabled ? control.p.card : BleeckerTheme.alpha(control.p.muted, 0.65)
        border.color: control.error ? control.p.destructive : control.activeFocus ? BleeckerTheme.alpha(control.p.sea, 0.75) : control.p.border
        border.width: 1
        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: BleeckerTheme.alpha(control.activeFocus ? control.p.sea : control.p.deepSea, control.activeFocus ? 0.1 : 0.025)
            shadowBlur: control.activeFocus ? 0.2 : 0.05
            shadowVerticalOffset: 1
        }
        Behavior on border.color { ColorAnimation { duration: BleeckerTheme.reducedMotion ? 0 : BleeckerTokens.durations.control; easing.type: Easing.OutCubic } }
    }
}
