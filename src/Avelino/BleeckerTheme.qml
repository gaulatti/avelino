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
    // Resolved native editor colors from the pinned secure-field fixture.
    readonly property color nativeEditorText: Qt.rgba(dark ? 1 : 0, dark ? 1 : 0, dark ? 1 : 0, 216/255)
    readonly property color nativeEditorPlaceholder: Qt.rgba(dark ? 1 : 0, dark ? 1 : 0, dark ? 1 : 0, (dark ? 140 : 127)/255)
    readonly property color nativeEditorDisabledText: Qt.rgba(dark ? 1 : 0, dark ? 1 : 0, dark ? 1 : 0, 63/255)
    function alpha(value: color, opacity: real): color {
        return Qt.rgba(value.r, value.g, value.b, value.a * opacity)
    }
}
