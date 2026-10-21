import QtQuick
import Prototype.Atomic 1.0
Rectangle {
    width: 420; height: 100; color: "white"
    Flickable {
        id: viewport; objectName: "viewport"
        x: 4; y: 4; width: 340; height: 36
        clip: true; interactive: false
        contentWidth: editor.width; contentHeight: height
        function ensureCursor() {
            const rectangle = editor.cursorRectangle
            if (rectangle.x < contentX) contentX = rectangle.x
            else if (rectangle.x + rectangle.width > contentX + width)
                contentX = rectangle.x + rectangle.width - width
            contentX = Math.max(0, Math.min(contentX, contentWidth - width))
        }
        AtomicEditor {
            id: editor; objectName: "editor"
            width: Math.max(viewport.width, contentWidth + 2); height: viewport.height
            onCursorRectangleChanged: viewport.ensureCursor()
            onContentWidthChanged: viewport.ensureCursor()
            Accessible.role: Accessible.EditableText
            Accessible.name: "Search"
            Accessible.description: "Atomic token document prototype"
        }
    }
}
