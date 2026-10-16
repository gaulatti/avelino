import QtQuick
import QtQuick.Templates as T

T.TextField {
    id: control
    property string size: "md"
    property bool error: false
    property Component leading
    property Component trailing
    property int placeholderElide:Text.ElideRight
    readonly property var p: BleeckerTheme.palette
    readonly property real horizontalPadding: size === "sm" ? 12 : size === "lg" ? 16 : 14
    implicitWidth: 240
    implicitHeight: Math.max(contentHeight + topPadding + bottomPadding,
                             leadingSlot.item ? leadingSlot.height : 0, trailingSlot.item ? trailingSlot.height : 0,
                             (size === "sm" ? 36 : size === "lg" ? 44 : 40) * BleeckerTheme.textScale)
    leftPadding: horizontalPadding + (leadingSlot.item ? leadingSlot.width + 10 : 0)
    rightPadding: horizontalPadding + (trailingSlot.item ? trailingSlot.width + 10 : 0)
    topPadding: 0
    bottomPadding: 0
    font.family: BleeckerTheme.primaryFont
    font.weight: Font.Normal
    font.pixelSize: (size === "sm" ? 12 : 14) * BleeckerTheme.textScale
    color: p.textPrimary
    placeholderTextColor: p.textSecondary
    selectionColor: p.sea
    selectedTextColor: p.primaryForeground
    verticalAlignment: TextInput.AlignVCenter
    opacity: enabled ? 1 : 0.6
    focusPolicy: Qt.StrongFocus
    Accessible.name: placeholderText
    Loader {
        id: leadingSlot
        objectName: "bleeckerTextFieldLeading"
        sourceComponent: control.leading
        x: control.horizontalPadding; y: (control.height-height)/2
    }
    Loader {
        id: trailingSlot
        objectName: "bleeckerTextFieldTrailing"
        sourceComponent: control.trailing
        x: control.width-control.horizontalPadding-width; y: (control.height-height)/2
    }
    Text {
        objectName: "bleeckerTextFieldPlaceholder"
        x: control.leftPadding; y: control.topPadding
        width: Math.max(0,control.width-control.leftPadding-control.rightPadding)
        height: Math.max(0,control.height-control.topPadding-control.bottomPadding)
        text: control.placeholderText; font: control.font; color: control.placeholderTextColor
        horizontalAlignment: control.horizontalAlignment; verticalAlignment: control.verticalAlignment
        elide: control.placeholderElide; renderType: control.renderType
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
