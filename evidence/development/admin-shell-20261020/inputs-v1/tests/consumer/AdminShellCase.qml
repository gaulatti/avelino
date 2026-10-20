import QtQuick
import Avelino

Item {
    id: fixture
    required property var definition
    required property bool initial
    property string owner: "echo"
    property bool navigation: initial
    property var requests: []
    property var pending: null
    property Component sidebarOverride: null
    property Component headerOverride: null
    property Component contentOverride: null
    readonly property Item shell: shellControl
    readonly property Item toolbarItem: shellControl.toolbarItem
    width: Math.ceil(definition.width)
    height: Math.ceil(definition.height)
    clip: true
    function request(value: bool): void {
        requests = requests.concat([value])
        if (owner === "echo") navigation = value
        else if (owner === "delay") pending = value
    }
    function flush(): void { if (pending !== null) { const value = pending; pending = null; navigation = value } }
    function applyStep(step: string): void {
        if (step === "initial") return
        if (step === "external-false" || step === "external-hide") navigation = false
        else if (step === "external-true" || step === "external-show") navigation = true
        else if (step.endsWith("-flush")) flush()
        else if (step.startsWith("divider-")) shellControl.setDividerPosition(Number(step.slice(8)))
        else if (step.startsWith("resize-")) width = Number(step.slice(7))
        else throw new Error("Unknown native admin step: " + step)
    }
    readonly property Component sideFactory: Component {
        Rectangle { width: fixture.definition.sidebar === "zero" ? 0 : fixture.definition.sideWidth; height: fixture.definition.sidebar === "zero" ? 0 : fixture.definition.sideHeight; color: "#00ff00" }
    }
    readonly property Component headFactory: Component {
        Rectangle { width: fixture.definition.header === "zero" ? 0 : fixture.definition.headWidth; height: fixture.definition.header === "zero" ? 0 : fixture.definition.headHeight; color: "#ff0000" }
    }
    readonly property Component contentFactory: Component {
        Rectangle { width: fixture.definition.content === "zero" ? 0 : fixture.definition.contentWidth; height: fixture.definition.content === "zero" ? 0 : fixture.definition.contentHeight; color: "#0000ff" }
    }
    readonly property Component flexSideFactory: Component {
        Rectangle { implicitWidth: 10; implicitHeight: 10; BleeckerLayout.minimumWidth: 0; BleeckerLayout.fillsWidth: true; BleeckerLayout.fillsHeight: true; color: "#00ff00" }
    }
    readonly property Component flexHeadFactory: Component {
        Rectangle { implicitWidth: 10; implicitHeight: 10; BleeckerLayout.minimumWidth: 0; BleeckerLayout.fillsWidth: true; BleeckerLayout.fillsHeight: true; color: "#ff0000" }
    }
    readonly property Component flexContentFactory: Component {
        Rectangle { implicitWidth: 10; implicitHeight: 10; BleeckerLayout.minimumWidth: 0; BleeckerLayout.fillsWidth: true; BleeckerLayout.fillsHeight: true; color: "#0000ff" }
    }
    // Caller colours are diagnostics until native Color inputs and window
    // compositing have been compared. Geometry does not accept their pixels.
    Rectangle { anchors.fill: parent; color: "white"; Accessible.ignored: true }
    BleeckerAdminShell {
        id: shellControl
        anchors.fill: parent
        navigationPresented: fixture.navigation
        sidebarWidth: fixture.definition.columnWidth
        breakpoint: fixture.definition.breakpoint
        sidebar: fixture.sidebarOverride ? fixture.sidebarOverride : fixture.definition.sidebar === "empty" ? null
            : fixture.definition.sidebar === "flex" ? fixture.flexSideFactory : fixture.sideFactory
        header: fixture.headerOverride ? fixture.headerOverride : fixture.definition.header === "empty" ? null
            : fixture.definition.header === "flex" ? fixture.flexHeadFactory : fixture.headFactory
        content: fixture.contentOverride ? fixture.contentOverride : fixture.definition.content === "empty" ? null
            : fixture.definition.content === "flex" ? fixture.flexContentFactory : fixture.contentFactory
        onNavigationPresentedRequested: value => fixture.request(value)
    }
    function box(item): var { const p = item.mapToItem(fixture, 0, 0); return {x:p.x, y:p.y, width:item.width, height:item.height} }
    function snapshot(): var {
        const frames = {root:box(shellControl.presentationItem)}
        if (shellControl.sidebarItem) frames.sidebar = box(shellControl.sidebarItem)
        if (shellControl.headerItem) frames.header = box(shellControl.headerItem)
        if (shellControl.contentSlotItem) frames.content = box(shellControl.contentSlotItem)
        return {frames:frames, navigation:navigation, requests:requests, pending:pending,
            displayedNavigation:shellControl.displayedNavigation, columnWidth:shellControl.columnWidth}
    }
}
