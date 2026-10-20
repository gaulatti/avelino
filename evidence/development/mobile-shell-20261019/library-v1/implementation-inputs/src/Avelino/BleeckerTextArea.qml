import QtQuick
import QtQuick.Templates as T

FocusScope {
    id: control
    property alias text: editor.text
    property alias font: editor.font
    property alias readOnly: editor.readOnly
    property alias selectedText: editor.selectedText
    property alias selectionStart: editor.selectionStart
    property alias selectionEnd: editor.selectionEnd
    property string accessibleName: ""
    property real minimumHeight: 96
    implicitWidth: 240; implicitHeight: minimumHeight
    activeFocusOnTab: true
    ContinuousSurface {
        anchors.fill: parent; radius: BleeckerTokens.radii.ui
        color: BleeckerTheme.palette.card; borderColor: BleeckerTheme.palette.border
    }
    Flickable {
        id: viewport
        objectName: "bleeckerTextAreaViewport"
        x: 10; y: 10; width: Math.max(0,parent.width-20); height: Math.max(0,parent.height-20)
        clip: true; boundsBehavior: Flickable.StopAtBounds
        T.TextArea.flickable: T.TextArea {
            id: editor
            objectName: "bleeckerTextAreaInput"
            focus: true; padding: 0
            implicitHeight: contentHeight+topPadding+bottomPadding
            font.family: BleeckerTheme.primaryFont
            font.pointSize: BleeckerFonts.pointSizeForPixels(14*BleeckerTheme.textScale)
            color: BleeckerTheme.palette.textPrimary
            selectionColor: BleeckerTheme.palette.sea; selectedTextColor: BleeckerTheme.palette.primaryForeground
            wrapMode: TextEdit.Wrap
            background: null
            Accessible.name: control.accessibleName
        }
        T.ScrollBar.vertical: T.ScrollBar {
            objectName: "bleeckerTextAreaScrollBar"
            width: 6; minimumSize: 0.08
            opacity: active || hovered ? 1 : 0
            contentItem: Rectangle { radius: 3; color: BleeckerTheme.alpha(BleeckerTheme.palette.textSecondary,0.5) }
            background: null
        }
    }
}
