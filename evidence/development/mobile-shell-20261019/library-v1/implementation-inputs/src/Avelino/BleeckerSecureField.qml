import QtQuick
import QtQuick.Templates as T

T.TextField {
    id: control
    readonly property bool revealed: reveal.checked
    implicitWidth: 240
    implicitHeight: Math.max(40, contentHeight + topPadding + bottomPadding)
    leftPadding: 14; rightPadding: 14 + 8 + reveal.width
    topPadding: 0; bottomPadding: 0
    font.family: BleeckerTheme.primaryFont
    font.pointSize: BleeckerFonts.pointSizeForPixels(14)
    font.weight: Font.Normal
    color: enabled ? BleeckerTheme.nativeEditorText : BleeckerTheme.nativeEditorDisabledText
    placeholderTextColor: BleeckerTheme.nativeEditorPlaceholder
    selectionColor: BleeckerTheme.palette.sea
    selectedTextColor: BleeckerTheme.palette.primaryForeground
    echoMode: revealed ? TextInput.Normal : TextInput.Password
    passwordCharacter: "\u2022"
    passwordMaskDelay: 0
    verticalAlignment: TextInput.AlignVCenter
    focusPolicy: Qt.StrongFocus
    Accessible.name: placeholderText
    Accessible.description: revealed ? "Contents visible" : "Contents hidden"
    OwnedText {
        objectName: "bleeckerSecurePlaceholder"
        x: control.leftPadding
        y: (control.height - height) / 2
        width: Math.max(0,control.width-control.leftPadding-control.rightPadding)
        text: control.placeholderText; font: control.font; color: control.placeholderTextColor
        elideWidth: width
        visible: !control.length && !control.preeditText
        Accessible.ignored: true
    }
    T.Button {
        id: reveal
        objectName: "bleeckerSecureReveal"
        x: control.width - 14 - width; y: (control.height-height)/2
        width: 22; height: 20
        padding: 0; checkable: true
        focusPolicy: Qt.StrongFocus
        opacity: enabled ? 1 : 0.5
        Accessible.name: checked ? "Hide contents" : "Show contents"
        Accessible.role: Accessible.Button
        contentItem: SecureEyeGlyph { slashed: reveal.checked }
        background: Rectangle {
            anchors.fill: parent; anchors.margins: -3
            radius: 3; color: "transparent"
            border.width: reveal.visualFocus ? 2 : 0
            border.color: BleeckerTheme.palette.sea
        }
    }
    background: BleeckerSurface { radius: BleeckerTokens.radii.ui }
}
