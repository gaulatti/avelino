import QtQuick
import Avelino

Window {
    id: root
    property var chosen: "morning"
    property var longChosen: 0
    property int activations: 0
    width: 760; height: 560; visible: true
    title: "Avelino installed selector"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark=consumerDark
        BleeckerTheme.textScale=consumerTextScale
        BleeckerTheme.reducedMotion=true
    }
    BleeckerEyebrow { x: 24; y: 24; text: "Selector popup candidate" }
    BleeckerSelect {
        objectName: "select"
        x: 24; y: 440; width: 300
        options: [{value:"morning",label:"Morning edition"},{value:"skip",label:"Disabled edition",disabled:true},{value:"evening",label:"Evening edition"}]
        selection: root.chosen
        onActivated: value => { root.chosen=value; root.activations++ }
    }
    BleeckerTextField { objectName: "nextField"; x: 400; y: 40; width: 300; placeholderText: "Next field" }
    BleeckerSelect {
        objectName: "longSelect"
        x: 400; y: 440; width: 300
        selection: root.longChosen
        options: { const rows=[]; for (let i=0;i<40;i++) rows.push({value:i,label:"Edition "+i,disabled:i===39}); return rows }
        onActivated: value => root.longChosen=value
    }
    BleeckerSelect { x: 400; y: 120; width: 300; selection: "missing"; options: []; enabled: false }
}
