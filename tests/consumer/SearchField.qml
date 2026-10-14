import QtQuick
import Avelino

Window {
    property string query: ""
    property int edits: 0
    property int accepts: 0
    width: 700; height: 420; visible: true
    title: "Avelino installed search field"
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark=consumerDark; BleeckerTheme.textScale=consumerTextScale; BleeckerTheme.reducedMotion=true }
    Column {
        x: 24; y: 24; width: 300; spacing: 24
        BleeckerEyebrow { text: "Search and clear" }
        BleeckerSearchField {
            objectName: "searchField"; width: parent.width; placeholderText: "Search editions"
            text: query
            onTextEdited: { query=text; edits++ }
            onAccepted: accepts++
        }
        BleeckerSearchField { objectName: "disabledSearch"; width: parent.width; placeholderText: "Disabled"; text: "Morning edition"; enabled: false }
        BleeckerTextField { objectName: "searchNextField"; width: parent.width; placeholderText: "Continue here" }
    }
    Column {
        x: 360; y: 24; width: 316; spacing: 24
        BleeckerEyebrow { text: "Constrained and error" }
        BleeckerSearchField { objectName: "narrowSearch"; width: 160; text: "A longer fictional search query for the native fixture"; placeholderText: "Search editions" }
        BleeckerSearchField { width: parent.width; error: true; text: "Morning edition"; placeholderText: "Search editions" }
    }
}
