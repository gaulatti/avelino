import QtQuick
import QtQuick.Templates as T

T.Control {
    id: control
    property string text: ""
    property bool selected: false
    property bool removable: false
    readonly property bool roundedContentClipping: body.roundedClipping
    signal clicked()
    signal removeRequested()
    font.family: BleeckerTheme.primaryFont
    font.pointSize: BleeckerFonts.pointSizeForPixels(12)
    font.weight: Font.Medium
    padding: 0; focusPolicy: Qt.NoFocus
    implicitWidth: body.implicitWidth
    implicitHeight: body.implicitHeight
    Accessible.role: Accessible.Grouping; Accessible.name: text
    contentItem: CapsuleContent {
        id: body
        implicitWidth: label.unwrappedWidth+20+(control.removable ? remove.implicitWidth+6 : 0)
        implicitHeight: Math.max(28,label.naturalHeight,control.removable ? remove.implicitHeight : 0)
        T.Button {
            id: primary
            objectName: "bleeckerFilterAction"
            x: 10; y: (parent.height-height)/2
            width: Math.max(0,parent.width-20-(control.removable ? remove.width+6 : 0))
            height: label.naturalHeight; padding: 0
            text: control.text; font: control.font
            opacity: enabled ? 1 : 0.5
            focusPolicy: Qt.StrongFocus
            Accessible.role: Accessible.Button; Accessible.name: text
            onClicked: control.clicked()
            contentItem: OwnedText {
                id: label
                objectName: "bleeckerFilterLabel"
                text: primary.text; font: primary.font; wrapWidth: width
                color: control.selected ? BleeckerTheme.palette.primaryForeground : BleeckerTheme.palette.textPrimary
            }
            background: Rectangle {
                anchors.fill: parent; anchors.margins: -2
                color: "transparent"; radius: 3
                border.width: primary.visualFocus ? 2 : 0; border.color: BleeckerTheme.palette.sea
            }
        }
        T.Button {
            id: remove
            objectName: "bleeckerFilterRemove"
            visible: control.removable
            implicitWidth: 10; implicitHeight: 10
            width: implicitWidth; height: implicitHeight; padding: 0
            x: parent.width-10-width; y: (parent.height-height)/2
            opacity: enabled ? 1 : 0.5
            focusPolicy: Qt.StrongFocus
            Accessible.role: Accessible.Button
            Accessible.name: control.text === "" ? "Remove filter" : "Remove "+control.text
            onClicked: control.removeRequested()
            contentItem: InputGlyph {
                symbol: "clear"; strokeWidth: 1.3
                color: control.selected ? BleeckerTheme.palette.primaryForeground : BleeckerTheme.palette.textPrimary
            }
            background: Rectangle {
                anchors.fill: parent; anchors.margins: -2
                color: "transparent"; radius: 3
                border.width: remove.visualFocus ? 2 : 0; border.color: BleeckerTheme.palette.sea
            }
        }
    }
    background: Rectangle {
        objectName: "bleeckerFilterBackground"
        radius: Math.min(width,height)/2; antialiasing: true
        color: control.selected ? BleeckerTheme.palette.primary : BleeckerTheme.palette.muted
        border.width: control.selected ? 0 : 1; border.color: BleeckerTheme.palette.border
    }
}
