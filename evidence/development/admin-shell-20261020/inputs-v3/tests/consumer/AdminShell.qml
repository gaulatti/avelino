import QtQuick
import QtQuick.Templates as T
import Avelino

T.ApplicationWindow {
    id: window
    readonly property bool gallery: typeof consumerDark === "undefined"
    property var definition: ({id:"standard", width:840, height:500, columnWidth:300, breakpoint:768,
        sidebar:"fixed", header:"fixed", content:"flex", sideWidth:180, sideHeight:90,
        headWidth:180, headHeight:36, contentWidth:200, contentHeight:100})
    property Item primaryFixture: null
    width: gallery ? 1180 : Math.ceil(definition.width)
    height: gallery ? 800 : Math.ceil(definition.height) + (header ? header.height : 0)
    visible: true
    title: "Avelino desktop administration shell"
    header: primaryFixture ? primaryFixture.toolbarItem : null
    background: Rectangle { color: BleeckerTheme.palette.background }
    Component { id: factory; AdminShellCase {} }
    function configure(value, policy): void {
        if (primaryFixture) { const old = primaryFixture; primaryFixture = null; old.destroy() }
        definition = Object.assign({}, value.definition !== undefined ? value.definition : value)
        if (value.dark !== undefined) BleeckerTheme.dark = value.dark
        primaryFixture = factory.createObject(bodyHost, {definition:definition, initial:value.initial === undefined ? true : value.initial,
            owner:policy === undefined ? "echo" : policy})
        if (!primaryFixture) throw new Error("Admin caller creation failed")
    }
    function applyStep(step): void {
        primaryFixture.applyStep(step)
        if (step.startsWith("resize-")) definition = Object.assign({}, definition, {width:Number(step.slice(7))})
    }
    function update(value): void { configure({definition:Object.assign({}, definition, value), initial:primaryFixture.navigation}) }
    Component.onCompleted: {
        BleeckerTheme.dark = gallery ? captureDark : consumerDark
        BleeckerTheme.textScale = gallery ? captureTextScale : consumerTextScale
        configure({definition:definition, initial:true})
    }
    Item {
        id: bodyHost
        x: gallery ? 24 : 0; y: gallery ? 140 : 0
        width: Math.ceil(window.definition.width); height: Math.ceil(window.definition.height)
    }
    ProposalRow {
        x:24; y:24; spacing:8; visible:window.gallery
        Repeater {
            model:["empty", "zero", "fixed", "flex"]
            BleeckerButton { required property string modelData; text:modelData; size:"xs"; onClicked:window.update({content:modelData}) }
        }
        BleeckerButton { text:"Navigation"; size:"xs"; onClicked:window.primaryFixture.navigation = !window.primaryFixture.navigation }
        BleeckerButton { text:"Narrow"; size:"xs"; onClicked:window.update({width:window.definition.width === 360 ? 840 : 360}) }
        BleeckerButton { text:"Short"; size:"xs"; onClicked:window.update({height:window.definition.height === 24 ? 500 : 24}) }
    }
    ProposalRow {
        x:24; y:80; spacing:8; visible:window.gallery
        Repeater {
            model:["echo", "ignore", "delay"]
            BleeckerButton { required property string modelData; text:modelData; size:"xs"; onClicked:window.configure({definition:window.definition, initial:true}, modelData) }
        }
        BleeckerButton { text:"Apply pending"; size:"xs"; onClicked:window.primaryFixture.flush() }
        BleeckerButton { text:"Theme"; size:"xs"; onClicked:BleeckerTheme.dark = !BleeckerTheme.dark }
    }
    Text {
        x:24; y:680; width:1100; visible:window.gallery
        text:window.primaryFixture ? "Caller: " + window.primaryFixture.navigation + "  Displayed: " + window.primaryFixture.shell.displayedNavigation
            + "  Requests: " + JSON.stringify(window.primaryFixture.requests) + "  Pending: " + JSON.stringify(window.primaryFixture.pending) : ""
        color:BleeckerTheme.palette.textPrimary
        font.family:BleeckerTheme.secondaryFont; font.pixelSize:16
        wrapMode:Text.WordWrap
    }
}
