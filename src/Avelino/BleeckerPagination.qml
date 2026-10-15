import QtQuick
import QtQuick.Templates as T

T.Control {
    id: control
    required property int page
    required property int pageCount
    signal pageRequested(int page)
    readonly property real naturalWidth: previous.implicitWidth+next.implicitWidth+16+label.unwrappedWidth
    readonly property size contentSize: Qt.size(row.width,row.height)
    implicitWidth: naturalWidth; implicitHeight: row.implicitHeight
    padding: 0
    contentItem: Item {
        Row {
            id: row
            objectName: "bleeckerPaginationContent"
            anchors.centerIn: parent; anchors.alignWhenCentered: false
            spacing: 8
            BleeckerIconButton {
                id: previous
                objectName: "bleeckerPreviousPage"
                y: (row.height-height)/2
                accessibilityLabel: "Previous page"
                enabled: control.page>1
                onClicked: control.pageRequested(Math.max(1,control.page-1))
                icon: NavigationGlyph { direction: "left"; color: previous.foregroundColor; pixelSize: previous.glyphPixelSize }
            }
            OwnedText {
                id: label
                objectName: "bleeckerPaginationLabel"
                y: (row.height-height)/2
                text: qsTr("Page %1 of %2").arg(Number(control.page).toLocaleString(control.locale,"f",0)).arg(Number(Math.max(1,control.pageCount)).toLocaleString(control.locale,"f",0))
                font.family: BleeckerTheme.primaryFont
                font.pointSize: BleeckerFonts.pointSizeForPixels(12)
                wrapWidth: Math.max(0,control.availableWidth-previous.width-next.width-16)
                color: BleeckerTheme.nativeTextPrimary
                Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
            }
            BleeckerIconButton {
                id: next
                objectName: "bleeckerNextPage"
                y: (row.height-height)/2
                accessibilityLabel: "Next page"
                enabled: control.page<control.pageCount
                onClicked: control.pageRequested(Math.min(control.pageCount,control.page+1))
                icon: NavigationGlyph { direction: "right"; color: next.foregroundColor; pixelSize: next.glyphPixelSize }
            }
        }
    }
}
