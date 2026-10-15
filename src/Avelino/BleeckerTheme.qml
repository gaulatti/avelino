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
    // Resolved source Color.primary; native editors use the same text color.
    readonly property color nativeTextPrimary: Qt.rgba(dark ? 1 : 0, dark ? 1 : 0, dark ? 1 : 0, 216/255)
    // Resolved native editor colors from the pinned secure-field fixture.
    readonly property color nativeEditorText: nativeTextPrimary
    readonly property color nativeEditorPlaceholder: Qt.rgba(dark ? 1 : 0, dark ? 1 : 0, dark ? 1 : 0, (dark ? 140 : 127)/255)
    readonly property color nativeEditorDisabledText: Qt.rgba(dark ? 1 : 0, dark ? 1 : 0, dark ? 1 : 0, 63/255)
    readonly property color nativeSpinnerForeground: dark ? "#ffffff" : "#000000"
    readonly property int nativeSpinnerDuration: 800
    // Opaque Color.red samples from the pinned macOS source at both schemes.
    readonly property color nativeRed: dark ? "#ff4245" : "#ff383c"
    // Owned Linux presentation of the pinned source slider's system surfaces.
    readonly property color nativeSliderFill: dark ? "#60a5f5" : "#2b5580"
    readonly property color nativeSliderTrack: dark ? "#252f37" : "#e6e6e6"
    readonly property color nativeSliderHandle: dark ? "#dbddde" : "#ffffff"
    readonly property color nativeSliderTick: dark ? "#485157" : "#bdbdbd"
    readonly property color nativeSliderDisabledFill: dark ? "#303a40" : "#dadada"
    function alpha(value: color, opacity: real): color {
        return Qt.rgba(value.r, value.g, value.b, value.a * opacity)
    }
}
