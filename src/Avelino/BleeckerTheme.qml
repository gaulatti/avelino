pragma Singleton
pragma FunctionSignatureBehavior: Enforced
import QtQuick
QtObject {
    property bool dark: false
    property real textScale: 1.0
    property bool reducedMotion: false
    readonly property var palette: dark ? BleeckerTokens.colors.dark : BleeckerTokens.colors.light
    readonly property string primaryFont: BleeckerFonts.primary
    readonly property string secondaryFont: BleeckerFonts.secondary
    function alpha(value: color, opacity: real): color {
        return Qt.rgba(value.r, value.g, value.b, value.a * opacity)
    }
}
