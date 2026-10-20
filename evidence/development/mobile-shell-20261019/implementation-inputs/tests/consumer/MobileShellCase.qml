import QtQuick
import Avelino

Item {
    id: fixture
    required property var definition
    property var selection: "news"
    property var tabs: definition.tabs !== undefined ? definition.tabs
        : [{value:"news",label:"News",systemImage:"newspaper"}]
    signal selectionRequested(var requestedValue)
    readonly property Item shell: shellControl
    readonly property Item toolbarItem: shellControl.toolbarItem
    width: definition.width
    height: definition.height
    readonly property Component headerFactory: Component {
        Rectangle { objectName:"mobileHeader"; width:180; height:fixture.definition.header; color:"#ff0000"; visible:!fixture.definition.hiddenHeader }
    }
    readonly property Component footerFactory: Component {
        Rectangle { objectName:"mobileFooter"; width:120; height:fixture.definition.footer; color:"#00ff00" }
    }
    readonly property Component flexibleFactory: Component {
        Rectangle { objectName:"mobileContent"; implicitWidth:10; implicitHeight:10; color:"#0000ff"; BleeckerLayout.minimumWidth:0; BleeckerLayout.fillsWidth:true; BleeckerLayout.fillsHeight:true }
    }
    readonly property Component fixedFactory: Component {
        Rectangle { objectName:"mobileContent"; width:200; height:100; color:"#0000ff" }
    }
    readonly property Component zeroFactory: Component {
        Rectangle { objectName:"mobileContent"; width:0; height:0; color:"#0000ff" }
    }
    Rectangle { anchors.fill:parent; color:BleeckerTheme.palette.background; Accessible.ignored:true }
    Item {
        id: fit
        width: Math.max(fixture.width, shellControl.BleeckerLayout.minimumWidth)
        height: Math.max(fixture.height, shellControl.presentationItem.minimumHeight)
        x: (fixture.width-width)/2
        y: (fixture.height-height)/2
        BleeckerMobileAppShell {
            id: shellControl
            anchors.fill:parent
            selection:fixture.selection
            tabs:fixture.tabs
            header:fixture.definition.header===null ? null:fixture.headerFactory
            footer:fixture.definition.footer===null ? null:fixture.footerFactory
            content:fixture.definition.content==="empty" ? null
                :fixture.definition.content==="fixed" ? fixture.fixedFactory
                :fixture.definition.content==="zero" ? fixture.zeroFactory:fixture.flexibleFactory
            sectionIcon:Component { MobileShellGlyph {} }
            onSelectionRequested:requestedValue=>fixture.selectionRequested(requestedValue)
        }
    }
    function box(item):var {
        const p=item.mapToItem(fixture,0,0)
        return {x:p.x,y:p.y,width:item.width,height:item.height}
    }
    function snapshot():var {
        const frames={component:box(shellControl.presentationItem),fit:box(fit)}
        if(shellControl.headerItem && !definition.hiddenHeader)frames.header=box(shellControl.headerItem)
        if(shellControl.footerItem)frames.footer=box(shellControl.footerItem)
        if(shellControl.contentSlotItem)frames.content=box(shellControl.contentSlotItem)
        return {frames:frames,selection:selection,toolbarVisible:toolbarItem.visible,
            toolbarCount:toolbarItem.count,toolbarHeight:toolbarItem.height}
    }
}
