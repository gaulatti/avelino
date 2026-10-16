import QtQuick
import Avelino

Window {
    id: window
    property string chosen: "a"
    readonly property var choices: [{value:"a",label:"Alpha"},{value:"b",label:"Disabled",disabled:true},{value:"c",label:"Gamma"}]
    width: 780; height: 540; visible: true
    title: "Avelino — tabs and segmented selection"
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark=captureDark;BleeckerTheme.textScale=captureTextScale;BleeckerTheme.reducedMotion=true }
    Column {
        x: 24; y: 24; spacing: 24
        BleeckerEyebrow { text: "Caller-owned selection" }
        BleeckerTabs { options: window.choices; selection: window.chosen; onActivated: value => window.chosen=value }
        BleeckerSegmentedControl { options: window.choices; selection: window.chosen; onActivated: value => window.chosen=value }
        BleeckerTabs { options: window.choices; selection: "b" }
        BleeckerTabs { options: window.choices; selection: "a"; enabled: false }
        BleeckerTabs { options: window.choices; selection: "missing" }
    }
    Column {
        x: 410; y: 24; spacing: 24
        BleeckerEyebrow { text: "Constrained, empty and RTL" }
        BleeckerTabs { width: 140; selection: "a"; options: [{value:"a",label:"Morning edition"},{value:"b",label:"Evening edition",disabled:true},{value:"c",label:"Weekend edition"}] }
        BleeckerTabs { options: window.choices; selection: "c"; LayoutMirroring.enabled: true; LayoutMirroring.childrenInherit: true }
        BleeckerTabs { selection: "a"; options: [] }
    }
}
