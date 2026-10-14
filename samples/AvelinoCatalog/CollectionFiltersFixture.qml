import QtQuick
import Avelino

Window {
    id: window
    property string query: "Morning edition"
    property bool selected: false
    property bool hasChip: true
    width: 740; height: 520; visible: true
    title: "Avelino — collection filters"
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark=captureDark; BleeckerTheme.textScale=captureTextScale; BleeckerTheme.reducedMotion=true }
    Column {
        x: 24; y: 24; width: 692; spacing: 28
        BleeckerEyebrow { text: "Query and caller-owned filters" }
        BleeckerCollectionFilters {
            width: parent.width; query: window.query
            onQueryEdited: window.query=query
            content: window.hasChip ? chip : null
        }
        Row {
            spacing: 12
            BleeckerFilterChip { text: "Unselected" }
            BleeckerFilterChip { text: "Selected"; selected: true }
            BleeckerFilterChip { text: "Disabled"; removable: true; enabled: false }
        }
        BleeckerFilterChip { width: 140; text: "A longer filter label wraps in its allocation"; removable: true }
        BleeckerCollectionFilters { width: 320; content: BleeckerFilterChip { text: "Edition"; removable: true } }
        BleeckerCollectionFilters { width: parent.width; content: Rectangle { implicitWidth: 100; implicitHeight: 84; color: BleeckerTheme.palette.sea } }
    }
    Component {
        id: chip
        BleeckerFilterChip { text: "Edition"; selected: window.selected; removable: true; onClicked: window.selected=!window.selected; onRemoveRequested: window.hasChip=false }
    }
}
