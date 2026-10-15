import QtQuick
import Avelino

Window {
    id: window
    property var chosen: "a"
    property int activations: 0
    readonly property var choices: [{value:"a",label:"Alpha"},{value:"b",label:"Disabled",disabled:true},{value:"c",label:"Gamma"}]
    width: 780; height: 540; visible: true
    title: "Avelino installed tabs"
    color: BleeckerTheme.palette.background
    Component.onCompleted: { BleeckerTheme.dark=consumerDark;BleeckerTheme.textScale=consumerTextScale;BleeckerTheme.reducedMotion=true }
    Column {
        x: 24; y: 24; spacing: 28
        BleeckerEyebrow { text: "Shared binding" }
        BleeckerTabs { objectName: "tabs"; options: window.choices; selection: window.chosen; onActivated: value => { window.chosen=value;window.activations++ } }
        BleeckerSegmentedControl { objectName: "segments"; options: window.choices; selection: window.chosen; onActivated: value => { window.chosen=value;window.activations++ } }
        BleeckerTabs { objectName: "disabledTabs"; options: window.choices; selection: "a"; enabled: false }
        BleeckerTextField { objectName: "tabsNext"; width: 300; placeholderText: "Continue here" }
    }
    Column {
        x: 410; y: 24; spacing: 28
        BleeckerEyebrow { text: "Layout and typed IDs" }
        BleeckerTabs { objectName: "narrowTabs"; width: 140; selection: "a"; options: [{value:"a",label:"Morning edition"},{value:"b",label:"Evening edition",disabled:true},{value:"c",label:"Weekend edition"}] }
        BleeckerTabs { objectName: "rtlTabs"; options: window.choices; selection: "c"; LayoutMirroring.enabled: true; LayoutMirroring.childrenInherit: true }
        BleeckerTabs { objectName: "numericTabs"; selection: 0; options: [{value:0,label:"Zero"},{value:2,label:"Two"}] }
    }
}
