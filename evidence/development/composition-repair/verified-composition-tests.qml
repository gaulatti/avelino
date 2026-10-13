import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

Item {
    id: root
    width: 1100; height: 850
    property int invocations: 0
    Rectangle { anchors.fill: parent; color: "white" }
    PixelAlignment { id: displayAlignment; target: root }
    Component { id: action; BleeckerButton { text: "Review"; size: "xs"; onClicked: root.invocations++ } }
    Component { id: sectionFactory; BleeckerDashboardSection { title: "Newsroom"; actions: action; Rectangle { objectName: "sectionSlot"; width: 180; height: 40; color: "red" } } }
    Component { id: gridFactory; BleeckerDashboardGrid { width: 536; tile: Rectangle { implicitHeight: tileData.height; color: tileData.color } } }
    Component { id: actionGridFactory; BleeckerDashboardGrid { width: 536; tile: BleeckerButton { text: tileData.title; onClicked: root.invocations++ } } }
    Component { id: feedFactory; BleeckerFeedItem { author: "Jane Doe"; timestamp: "12 Oct"; Rectangle { objectName: "feedSlot"; width: 180; height: 40; color: "red" } } }
    Component { id: footerFactory; BleeckerFooter { width: 300; T.Label { objectName: "footerLabel"; text: "Bleecker"; color: palette.windowText } } }
    Component {
        id: shellFactory
        BleeckerAppShell {
            width: 800; height: 400
            sidebar: Rectangle { implicitHeight: 80; color: "red" }
            header: Rectangle { implicitHeight: 30; color: "green" }
            content: Rectangle { implicitHeight: 60; color: "blue" }
        }
    }
    Component { id: progressFactory; BleeckerProgressStack { width: 100; height: 12 } }
    Component { id: clippingHostFactory; Item { width: 100; height: 12; clip: true } }
    TestCase {
        name: "CompositionContracts"
        when: windowShown
        function init() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1; BleeckerTheme.reducedMotion = true; root.invocations = 0 }
        function cleanup() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1 }
        function test_section_optional_subtitle_wrapping_actions() {
            const item = createTemporaryObject(sectionFactory,root,{width:300})
            verify(item)
            const header = findChild(item,"bleeckerDashboardHeader"), slot = findChild(item,"bleeckerDashboardContent")
            const title = findChild(item,"bleeckerSectionTitle"), subtitle = findChild(item,"bleeckerSectionSubtitle")
            const actionSlot = findChild(item,"bleeckerSectionActions")
            compare(subtitle.visible,false); compare(slot.y,header.height+16)
            mouseClick(actionSlot.item); compare(root.invocations,1)
            item.subtitle = "Ready for review"; tryCompare(subtitle,"visible",true)
            tryCompare(subtitle,"y",title.height+3)
            item.subtitle = ""; item.hasSubtitle = true; compare(subtitle.height,14)
            item.title = "A long newsroom heading that wraps at the offered width"
            item.width = 200; verify(title.height > 22)
            findChild(item,"sectionSlot").height = 70; tryCompare(item,"height",header.height+16+70)
        }
        function test_grid_breakpoints_order_variable_rows_and_mutation() {
            const item = createTemporaryObject(gridFactory,root,{tiles:[{height:30,color:"red"},{height:50,color:"green"},{height:40,color:"blue"}]})
            tryCompare(item,"columns",2)
            const a=findChild(item,"bleeckerDashboardTile0"), b=findChild(item,"bleeckerDashboardTile1"), c=findChild(item,"bleeckerDashboardTile2")
            tryCompare(a,"width",260); tryCompare(b,"x",276); tryCompare(c,"y",66)
            compare(a.y,10); compare(b.y,0); compare(item.height,106)
            item.width=535; tryCompare(item,"columns",1); tryCompare(c,"y",112); compare(item.height,152)
            item.width=812; tryCompare(item,"columns",3); tryCompare(c,"x",552); tryCompare(item,"height",50)
            item.minimumColumnWidth=200; item.width=519; tryCompare(item,"columns",2)
            tryCompare(a,"width",251.5); tryCompare(b,"x",267.5)
            item.tiles=[{height:60,color:"yellow"}]; tryCompare(item,"height",60)
            item.tiles=[]; tryCompare(item,"height",0)
        }
        function test_feed_slot_and_adjacent_timestamp() {
            const item=createTemporaryObject(feedFactory,root,{width:400})
            const author=findChild(item,"bleeckerFeedAuthor"), timestamp=findChild(item,"bleeckerFeedTimestamp"), slot=findChild(item,"bleeckerFeedContent")
            compare(timestamp.x,author.width+8); verify(timestamp.x+timestamp.width<300)
            compare(item.bodyWidth,224); compare(item.bodyX,88); compare(item.height,78)
            compare(slot.y,item.headerHeight+6); compare(item.height,item.headerHeight+6+40+16)
            item.author="A substantially longer author name wraps in a narrow feed"; item.width=220
            compare(item.bodyWidth,224); compare(item.bodyX,-2); compare(author.height,48); compare(item.height,110)
            verify(author.height>20); compare(item.height,item.headerHeight+6+40+16)
            findChild(item,"feedSlot").height=80; tryCompare(item,"height",item.headerHeight+6+80+16)
        }
        function test_grid_preserves_focused_tile_through_reflow() {
            const item=createTemporaryObject(actionGridFactory,root,{tiles:[{title:"First"},{title:"Second"},{title:"Third"}]})
            const tile=findChild(item,"bleeckerDashboardTile2"), button=tile.item
            button.forceActiveFocus(); verify(button.activeFocus)
            item.width=300; tryCompare(item,"columns",1); tryVerify(() => tile.y > 50)
            compare(tile.item,button); verify(button.activeFocus)
            keyClick(Qt.Key_Space); compare(root.invocations,1)
            item.width=812; tryCompare(item,"columns",3); tryCompare(tile,"x",552)
            compare(tile.item,button); verify(button.activeFocus)
            keyClick(Qt.Key_Space); compare(root.invocations,2)
        }
        function test_footer_inherits_font_and_palette() {
            const item=createTemporaryObject(footerFactory,root)
            const slot=findChild(item,"bleeckerFooterContent"), label=findChild(item,"footerLabel")
            compare(slot.y,21); compare(slot.width,300); compare(item.height,label.height+41)
            compare(label.font.family,BleeckerTheme.secondaryFont); compare(label.color.toString(),BleeckerTheme.palette.textSecondary.toString())
            BleeckerTheme.dark=true; compare(label.color.toString(),BleeckerTheme.palette.textSecondary.toString())
        }
        function test_shell_allocations_and_resize() {
            const item=createTemporaryObject(shellFactory,root)
            const sidebar=findChild(item,"bleeckerAppSidebar"), header=findChild(item,"bleeckerAppHeader"), content=findChild(item,"bleeckerAppContent")
            compare(sidebar.x,16); compare(sidebar.y,16); compare(sidebar.width,240); compare(header.width,479)
            compare(sidebar.parent.height,112); compare(sidebar.parent.y,144)
            compare(content.y,89); compare(content.height,287); compare(content.width,479)
            item.sidebarWidth=180; item.width=700; item.height=500
            tryCompare(sidebar,"width",180); tryCompare(header,"width",439); tryCompare(content,"height",387)
            header.item.implicitHeight=90; tryCompare(item,"headerHeight",90); compare(content.y,115); compare(content.height,361)
        }
        function test_stack_renders_gaps_negative_and_overflow() {
            const item=createTemporaryObject(progressFactory,root,{segments:[{id:"a",value:0.25,color:"red"},{id:"b",value:0.25,color:"blue"}]})
            verify(waitForRendering(item)); wait(40)
            // QuickTest's software item grab crops to logical dimensions even
            // when its pixels retain the window DPR. Capture the larger root.
            const image=grabImage(root), dpr=displayAlignment.devicePixelRatio, mid=Math.floor(item.height*dpr/2)
            compare(findChild(item,"bleeckerProgressStackTrack").width,52)
            compare(image.red(Math.floor(10*dpr),mid),255); compare(image.blue(Math.floor(35*dpr),mid),255)
            const muted=item.trackColor
            compare(image.red(Math.floor(26*dpr),mid),Math.round(muted.r*255))
            compare(image.red(Math.floor(75*dpr),mid),255); compare(image.blue(Math.floor(75*dpr),mid),255)
            item.segments=[{id:"negative",value:-1,color:"red"},{id:"overflow",value:2,color:"blue"}]
            verify(waitForRendering(item)); wait(40)
            compare(grabImage(root).blue(Math.floor(50*dpr),mid),255)
            compare(findChild(item,"bleeckerProgressStackTrack").width,202)
            compare(grabImage(root).red(Math.floor(150*dpr),mid),0)
            compare(grabImage(root).blue(Math.floor(150*dpr),mid),255)
            const clippingHost=createTemporaryObject(clippingHostFactory,root)
            item.parent=clippingHost
            verify(waitForRendering(item)); wait(40)
            compare(grabImage(root).red(Math.floor(50*dpr),mid),0)
            compare(grabImage(root).red(Math.floor(150*dpr),mid),255)
            compare(grabImage(root).blue(Math.floor(150*dpr),mid),255)
            item.segments=[]; verify(waitForRendering(item)); wait(40)
            compare(findChild(item,"bleeckerProgressStackTrack").width,0)
            compare(grabImage(root).red(Math.floor(50*dpr),mid),255)
            compare(grabImage(root).blue(Math.floor(50*dpr),mid),255)
        }
    }
}
