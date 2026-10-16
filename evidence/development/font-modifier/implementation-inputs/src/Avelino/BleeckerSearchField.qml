import QtQuick
import QtQuick.Templates as T

BleeckerTextField {
    id: control
    leading: InputGlyph { symbol: "search" }
    trailing: length > 0 ? clearAction : null
    Component {
        id: clearAction
        T.Button {
            objectName: "bleeckerSearchClear"
            implicitWidth: 18.5; implicitHeight: 18.5; padding: 4
            focusPolicy: Qt.StrongFocus
            enabled: !control.readOnly
            opacity: enabled ? 1 : 0.5
            Accessible.role: Accessible.Button
            Accessible.name: "Clear search"
            onClicked: {
                control.clear()
                control.textEdited()
                control.forceActiveFocus(Qt.OtherFocusReason)
            }
            contentItem: InputGlyph { symbol: "clear" }
            background: Rectangle {
                radius: 4; color: control.p.muted
                border.width: parent.visualFocus ? 2 : 0
                border.color: control.p.sea
            }
        }
    }
}
