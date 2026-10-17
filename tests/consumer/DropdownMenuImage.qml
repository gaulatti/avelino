import QtQuick
import Avelino

Image {
    property string systemImage:""
    readonly property bool supported:systemImage==="folder"||systemImage==="ellipsis"
    source:supported ? Qt.resolvedUrl("menu-symbols/"+systemImage+"-"+(BleeckerTheme.dark ? "dark":"light")+".svg"):""
    width:systemImage==="folder" ? 18:14
    height:systemImage==="folder" ? 14:5
    fillMode:Image.PreserveAspectFit
}
