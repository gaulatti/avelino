import QtQuick
import Avelino

Window {
    id: root
    readonly property real fixtureTextScale: BleeckerTheme.textScale
    property var chosen: 20
    width: 760; height: 560; visible: true
    title: "Avelino — selector popup candidate"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {
        BleeckerTheme.dark=captureDark
        BleeckerTheme.textScale=captureTextScale
        BleeckerTheme.reducedMotion=true
        Qt.callLater(() => select.popup.open())
    }
    BleeckerEyebrow { x: 24; y: 24; text: "Owned selector and open popup" }
    BleeckerSelect {
        id: select
        objectName: "selectorCandidate"
        x: 24; y: 440; width: 300
        selection: root.chosen
        options: { const rows=[]; for (let i=0;i<40;i++) rows.push({value:i,label:"Edition "+i,disabled:i===22}); return rows }
        onActivated: value => root.chosen=value
    }
    Column {
        x: 400; y: 40; width: 300; spacing: 24
        BleeckerSelect { width: parent.width; selection: "missing"; options: [] }
        BleeckerSelect { width: parent.width; selection: "a"; options: [{value:"a",label:"Disabled selector"}]; enabled: false }
        BleeckerSelect { width: 180; selection: "a"; options: [{value:"a",label:"A longer choice requires elision"}] }
    }
}
