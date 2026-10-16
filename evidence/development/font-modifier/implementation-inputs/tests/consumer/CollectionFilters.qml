import QtQuick
import Avelino

Window {
    id: window
    property string query: ""
    property bool selected: false
    property bool hasChip: true
    property bool tallContent: false
    property int edits: 0
    property int accepts: 0
    property int activations: 0
    property int removals: 0
    width: 740; height: 480; visible: true
    title: "Avelino installed collection filters"
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark=consumerDark; BleeckerTheme.textScale=consumerTextScale; BleeckerTheme.reducedMotion=true }
    Column {
        x: 24; y: 24; width: 692; spacing: 24
        BleeckerEyebrow { text: "Query and independent filter actions" }
        BleeckerCollectionFilters {
            objectName: "collection"; width: parent.width; query: window.query
            content: window.tallContent ? tall : window.hasChip ? chip : null
            onQueryEdited: { window.query=query; window.edits++ }
            onAccepted: window.accepts++
        }
        BleeckerCollectionFilters {
            objectName: "disabledCollection"; width: parent.width; query: "Disabled query"; enabled: false
            content: BleeckerFilterChip { text: "Disabled"; removable: true }
        }
        BleeckerFilterChip { objectName: "narrowChip"; width: 140; text: "A longer filter label wraps in its allocation"; removable: true }
        BleeckerTextField { objectName: "collectionNext"; width: 300; placeholderText: "Continue here" }
    }
    Component {
        id: chip
        BleeckerFilterChip {
            text: "Edition"; selected: window.selected; removable: true
            onClicked: { window.activations++; window.selected=!window.selected }
            onRemoveRequested: { window.removals++; window.hasChip=false }
        }
    }
    Component { id: tall; Rectangle { implicitWidth: 100; implicitHeight: 84; color: BleeckerTheme.palette.sea } }
}
