import QtQuick
import Avelino

Window {
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    width: 700; height: 460; visible: true
    title: "Avelino — search fields"
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark=captureDark; BleeckerTheme.textScale=captureTextScale; BleeckerTheme.reducedMotion=true }
    Column {
        x: 24; y: 24; width: 300; spacing: 24
        BleeckerEyebrow { text: "Search and clear" }
        BleeckerSearchField { width: parent.width; placeholderText: "Search editions" }
        BleeckerSearchField { width: parent.width; placeholderText: "Search editions"; text: "Morning edition" }
        BleeckerSearchField { width: parent.width; placeholderText: "Disabled"; text: "Morning edition"; enabled: false }
        BleeckerSearchField { width: 160; placeholderText: "Search editions"; text: "A longer fictional search query for the native fixture" }
    }
    Column {
        x: 360; y: 24; width: 316; spacing: 24
        BleeckerEyebrow { text: "Shared field variants" }
        BleeckerSearchField { width: parent.width; size: "sm"; placeholderText: "Small search"; text: "Morning edition" }
        BleeckerSearchField { width: parent.width; size: "lg"; placeholderText: "Large search"; text: "Morning edition" }
        BleeckerSearchField { width: parent.width; error: true; placeholderText: "Search editions"; text: "Morning edition" }
    }
}
