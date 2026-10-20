import QtQuick

Item {
    id: control
    property alias query: search.text
    property Component content
    readonly property var searchField: search
    readonly property var contentItem: slot.item
    signal queryEdited()
    signal accepted()
    implicitWidth: search.implicitWidth+(slot.item ? slot.width+10 : 0)
    implicitHeight: Math.max(40,search.implicitHeight,slot.item ? slot.implicitHeight : 0)
    Accessible.role: Accessible.Grouping; Accessible.name: "Collection filters"
    BleeckerSearchField {
        id: search
        objectName: "bleeckerCollectionSearch"
        placeholderText: "Search"
        width: Math.max(0,control.width-(slot.item ? slot.width+10 : 0))
        height: implicitHeight; y: (control.height-height)/2
        onTextEdited: control.queryEdited()
        onAccepted: control.accepted()
    }
    Item {
        // Keep positioning outside the Loader: its size synchronization also
        // observes geometry changes during content replacement.
        width: slot.width; height: slot.height
        x: control.width-width; y: (control.height-height)/2
        Loader {
            id: slot
            objectName: "bleeckerCollectionContent"
            sourceComponent: control.content
        }
    }
}
