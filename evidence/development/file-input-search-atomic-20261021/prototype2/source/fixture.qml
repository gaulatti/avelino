import QtQuick
import Prototype.Atomic 1.0
Rectangle {
    width: 420
    height: 100
    color: "white"
    AtomicEditor {
        objectName: "editor"
        x: 4; y: 4
        width: 340; height: 36
        clip: true
        Accessible.role: Accessible.EditableText
        Accessible.name: "Search"
        Accessible.description: "Atomic token document prototype"
    }
}
