import QtQuick
import QtQuick.Templates as T

T.Button {
    id:button
    property bool accent:false
    property bool dark:BleeckerTheme.dark
    implicitWidth:Math.max(70,label.implicitWidth+24);implicitHeight:24
    padding:0;focusPolicy:Qt.StrongFocus;hoverEnabled:true
    font.family:Qt.application.font.family;font.pixelSize:13
    Accessible.name:text
    contentItem:Text {
        id:label;text:button.text;font:button.font;textFormat:Text.PlainText
        horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter
        color:button.accent ? "white":button.dark ? "white":"#222222"
        opacity:button.enabled ? 1:0.35;Accessible.ignored:true
    }
    background:Rectangle {
        radius:5
        color:button.accent ? button.enabled ? button.down ? "#075bb8":"#006fe8":button.dark ? "#444444":"#c2c2c2"
            :button.dark ? button.down ? "#666666":"#555555":button.down ? "#e4e4e4":"white"
        border.width:button.visualFocus ? 2:0.5
        border.color:button.visualFocus ? "#80baff":button.dark ? "#737373":"#bbbbbb"
    }
}
