import QtQuick
import QtQuick.Layouts
import QtTest
import Avelino

Item {
    width: 1000; height: 500
    Component { id: separatorFactory; BleeckerSeparator {} }
    Component { id: progressFactory; BleeckerProgress { width: 200 } }
    Component {
        id: rtlProgressFactory
        BleeckerProgress { width: 200; LayoutMirroring.enabled: true; LayoutMirroring.childrenInherit: true }
    }
    Component { id: skeletonFactory; BleeckerSkeleton { width: 180; height: 20 } }
    Component { id: backgroundFactory; BleeckerBauhausBackground {} }
    Component {
        id: groupFactory
        BleeckerButtonGroup {
            Rectangle { objectName: "short"; implicitWidth: 30; implicitHeight: 20 }
            Rectangle { objectName: "tall"; implicitWidth: 70; implicitHeight: 40 }
        }
    }
    Component { id: leadingSlot; Rectangle { implicitWidth: 30; implicitHeight: 12; color: "red" } }
    Component { id: centerSlot; Rectangle { implicitWidth: 40; implicitHeight: 24; color: "green" } }
    Component { id: trailingSlot; Rectangle { implicitWidth: 70; implicitHeight: 36; color: "blue" } }
    Component { id: tallSlot; Rectangle { implicitWidth: 40; implicitHeight: 80; color: "green" } }
    Component {
        id: headerFactory
        BleeckerHeader { width: 500; leading: leadingSlot; center: centerSlot; trailing: trailingSlot }
    }
    Component {
        id: panelFactory
        BleeckerPanelLayout {
            width: 900; height: 100
            leading: leadingSlot; content: centerSlot; trailing: trailingSlot
        }
    }
    TestCase {
        name: "SurfaceAndLayoutContracts"
        when: windowShown
        function init() { BleeckerTheme.dark = false; BleeckerTheme.reducedMotion = true }
        function cleanup() { BleeckerTheme.dark = false; BleeckerTheme.reducedMotion = true }
        function test_separator_data() {
            return [{tag:"horizontal-light",vertical:false,dark:false},
                    {tag:"horizontal-dark",vertical:false,dark:true},
                    {tag:"vertical-light",vertical:true,dark:false},
                    {tag:"vertical-dark",vertical:true,dark:true}]
        }
        function test_separator(data) {
            BleeckerTheme.dark = data.dark
            const item = createTemporaryObject(separatorFactory, parent, {vertical:data.vertical})
            compare(data.vertical ? item.width : item.height, 1)
            const channel = data.dark ? 1 : 0
            verify(Qt.colorEqual(item.color, Qt.rgba(channel,channel,channel,0.08)))
            verify(item.Accessible.ignored)
        }
        function test_progress_data() {
            const rows = []
            for (const dark of [false,true])
                for (const size of ["sm","md","lg"])
                    for (const variant of ["default","success","warning","destructive"])
                        rows.push({tag:dark+"-"+size+"-"+variant,dark:dark,size:size,variant:variant})
            return rows
        }
        function test_progress(data) {
            BleeckerTheme.dark = data.dark
            const item = createTemporaryObject(progressFactory, parent, {size:data.size,variant:data.variant,accessibleName:"Download"})
            const fill = findChild(item, "bleeckerProgressFill")
            const nativeControl = findChild(item, "bleeckerProgressControl")
            compare(item.height, {sm:4,md:7,lg:10}[data.size])
            compare(nativeControl.Accessible.name, "Download")
            const paletteKey = {"default":"primary",success:"live",warning:"desert",destructive:"destructive"}[data.variant]
            compare(fill.color.toString(), BleeckerTheme.palette[paletteKey].toString())
            compare(nativeControl.background.color.toString(), BleeckerTheme.palette.muted.toString())
            for (const value of [-1,0,0.25,1,2]) {
                item.value = value
                tryCompare(fill, "width", 200 * Math.max(0,Math.min(1,value)))
                compare(nativeControl.value, Math.max(0,Math.min(1,value)))
            }
            item.value = 0.25; item.width = 320
            tryCompare(fill, "width", 80)
            compare(fill.radius, item.height / 2)
        }
        function test_progress_rtl() {
            const item = createTemporaryObject(rtlProgressFactory, parent, {value:0.25})
            const fill = findChild(item, "bleeckerProgressFill")
            tryCompare(fill, "width", 50)
            tryCompare(fill, "x", 150)
        }
        function test_progress_transition() {
            const item = createTemporaryObject(progressFactory, parent, {value:0})
            const fill = findChild(item, "bleeckerProgressFill")
            BleeckerTheme.reducedMotion = false
            item.value = 1
            wait(50)
            verify(fill.width > 0 && fill.width < 200)
            tryCompare(fill, "width", 200)
            BleeckerTheme.reducedMotion = true
            item.value = 0.25
            tryCompare(fill, "width", 50)
        }
        function test_skeleton_motion_and_visibility() {
            const item = createTemporaryObject(skeletonFactory, parent, {radius:18})
            compare(item.radius, 18); compare(item.opacity, 0.9)
            compare(item.color.toString(), BleeckerTheme.palette.muted.toString())
            verify(item.Accessible.ignored); verify(!item.animating)
            BleeckerTheme.reducedMotion = false
            tryCompare(item, "animating", true)
            wait(50)
            verify(item.opacity < 0.9 && item.opacity >= 0.45)
            item.visible = false
            tryCompare(item, "animating", false)
            compare(item.opacity, 0.9)
            BleeckerTheme.reducedMotion = true; item.visible = true
            verify(!item.animating); compare(item.opacity, 0.9)
            BleeckerTheme.dark = true
            compare(item.color.toString(), BleeckerTheme.palette.muted.toString())
        }
        function test_bauhaus_geometry_data() {
            return [{tag:"wide-light",width:400,height:200,dark:false},
                    {tag:"wide-dark",width:400,height:200,dark:true},
                    {tag:"tall-light",width:100,height:400,dark:false},
                    {tag:"tall-dark",width:100,height:400,dark:true}]
        }
        function test_bauhaus_geometry(data) {
            BleeckerTheme.dark = data.dark
            const item = createTemporaryObject(backgroundFactory, parent, {width:data.width,height:data.height})
            const circle = findChild(item, "bleeckerBauhausCircle")
            const band = findChild(item, "bleeckerBauhausBand")
            compare(circle.x, data.width * 0.72); compare(circle.y, -data.height * 0.18)
            compare(circle.width, data.height * 0.62); compare(circle.height, circle.width)
            compare(circle.radius, circle.width / 2); compare(circle.opacity, 0.16)
            compare(band.x, -data.width * 0.08); compare(band.y, data.height * 0.72)
            compare(band.width, data.width * 0.52); compare(band.height, data.height * 0.18)
            compare(band.opacity, 0.16)
            compare(circle.color.toString(), BleeckerTheme.palette.desert.toString())
            compare(band.color.toString(), BleeckerTheme.palette.sea.toString())
            verify(item.clip && item.Accessible.ignored)
            item.width *= 2
            compare(circle.x, data.width * 1.44); compare(band.width, data.width * 1.04)
        }
        function test_group_spacing_and_alignment() {
            const item = createTemporaryObject(groupFactory, parent)
            const shorter = findChild(item, "short"), tall = findChild(item, "tall")
            tryCompare(item, "implicitWidth", 108)
            compare(item.implicitHeight, 40)
            compare(shorter.y, 10); compare(tall.y, 0); compare(tall.x, 38)
            item.spacing = 12
            tryCompare(tall, "x", 42)
            tall.visible = false
            tryCompare(item, "implicitWidth", 30)
        }
        function test_header_slots_and_height() {
            const item = createTemporaryObject(headerFactory, parent)
            const leading = findChild(item, "bleeckerHeaderLeading")
            const center = findChild(item, "bleeckerHeaderCenter")
            const trailing = findChild(item, "bleeckerHeaderTrailing")
            tryCompare(item, "height", 56)
            tryCompare(center, "x", 210)
            compare(leading.x, 0); compare(trailing.x, 430)
            compare(leading.y, 22); compare(center.y, 16); compare(trailing.y, 10)
            item.center = tallSlot
            tryCompare(item, "height", 80)
            compare(center.height, 80); compare(center.y, 0)
        }
        function test_panel_slots_and_resize() {
            const item = createTemporaryObject(panelFactory, parent)
            const leading = findChild(item, "bleeckerPanelLeading")
            const center = findChild(item, "bleeckerPanelContent")
            const trailing = findChild(item, "bleeckerPanelTrailing")
            tryCompare(center, "x", 241)
            compare(leading.width, 240); compare(center.width, 358)
            compare(trailing.x, 600); compare(trailing.width, 300)
            compare(center.item.width, center.width); compare(center.item.height, 100)
            item.leadingWidth = 100; item.trailingWidth = 120; item.width = 700
            tryCompare(center, "x", 101)
            compare(center.width, 478); compare(trailing.x, 580)
        }
    }
}
