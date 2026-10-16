import QtQuick
import QtTest
import Avelino

Item {
    width: 900; height: 600
    Component { id: cardFactory; BleeckerCard { Rectangle { objectName: "slot"; width: 80; height: 30; color: "red" } } }
    Component { id: panelFactory; BleeckerPanel { title: "Panel"; Rectangle { objectName: "slot"; width: 80; height: 30; color: "red" } } }
    Component { id: attentionFactory; BleeckerAttentionSurface { hue: 210; intensity: 5; Rectangle { objectName: "slot"; width: 80; height: 30 } } }
    Component { id: statusFactory; BleeckerStatusBadge { text: "Ready" } }
    Component { id: notificationFactory; BleeckerNotificationBadge { count: 1 } }
    Component { id: eyebrowFactory; BleeckerEyebrow { text: "Mixed Case" } }
    TestCase {
        name: "CardAndBadgeContracts"
        when: windowShown
        function init() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1; BleeckerTheme.reducedMotion = true }
        function cleanup() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1 }
        function near(a,b) { verify(Math.abs(a-b) <= 1/65535, a + " != " + b) }
        function test_card_data() {
            const rows = []
            for (const dark of [false,true])
                for (const padding of ["none","sm","md","lg"])
                    for (const variant of ["surface","outlined","elevated","subtle","transparent"])
                        rows.push({tag:dark+"-"+padding+"-"+variant,dark:dark,padding:padding,variant:variant})
            return rows
        }
        function test_card(data) {
            BleeckerTheme.dark = data.dark
            const item = createTemporaryObject(cardFactory,parent,{paddingSize:data.padding,variant:data.variant})
            verify(item)
            const pad = {none:0,sm:16,md:24,lg:32}[data.padding]
            tryCompare(item,"width",80+pad*2); compare(item.height,30+pad*2)
            const host = findChild(item,"bleeckerCardContent"), slot = findChild(item,"slot")
            compare(slot.parent,host); compare(host.x,pad); compare(host.y,pad)
            compare(host.width,80); compare(host.height,30)
            const surface = findChild(item,"bleeckerCardSurface"), shadow = findChild(item,"bleeckerCardShadow")
            compare(surface.radius,12)
            compare(surface.borderColor.toString(),(data.variant === "transparent" ? Qt.rgba(0,0,0,0) : BleeckerTheme.palette.border).toString())
            const shadows = !data.dark && ["surface","elevated"].indexOf(data.variant) >= 0
            near(shadow.shadowColor.a,shadows ? 0.06 : 0)
            compare(shadow.visible,shadows)
            compare(shadow.blurRadius,data.variant === "elevated" ? 20 : 10)
            compare(shadow.offsetY,data.variant === "elevated" ? 8 : 3)
            slot.width = 100; tryCompare(item,"width",100+pad*2)
            item.width = 240; compare(host.width,240-pad*2)
        }
        function test_panel_optional_title_and_slots() {
            const item = createTemporaryObject(panelFactory,parent)
            verify(item)
            const title = findChild(item,"bleeckerPanelTitle"), host = findChild(item,"bleeckerPanelContent")
            const slot = findChild(item,"slot")
            compare(slot.parent,host)
            tryCompare(item,"height",48+title.height+16+30)
            compare(host.y,title.height+16); compare(title.logicalPixelSize,16)
            BleeckerTheme.textScale = 1.5; compare(title.logicalPixelSize,16)
            item.hasTitle = false; tryCompare(item,"height",78); compare(host.y,0)
            item.title = ""; item.hasTitle = true
            tryCompare(host,"y",title.height+16)
            verify(title.visible); compare(title.Accessible.name,"")
            slot.height = 60; tryCompare(item,"height",48+title.height+16+60)
        }
        function test_panel_intrinsic_slots_data() {
            const cases = []
            for (const padding of ["none","sm","md","lg"])
                for (const title of ["present","empty","omitted"])
                    cases.push({tag:padding+"-"+title,padding:padding,title:title})
            return cases
        }
        function test_panel_intrinsic_slots(data) {
            const item = createTemporaryObject(panelFactory,parent,{paddingSize:data.padding,
                title:data.title === "present" ? "Panel" : "",hasTitle:data.title !== "omitted"})
            verify(item)
            const padding = {none:0,sm:16,md:24,lg:32}[data.padding]
            const titleHeight = data.title === "present" ? 20 : data.title === "empty" ? 14 : 0
            tryCompare(item,"width",80+padding*2)
            tryCompare(item,"height",30+padding*2+(data.title === "omitted" ? 0 : titleHeight+16))
            const title = findChild(item,"bleeckerPanelTitle"), slot = findChild(item,"slot")
            compare(title.width,80)
            slot.width = 180; tryCompare(item,"width",180+padding*2)
            item.title = "A much longer title requiring a constrained width"; item.hasTitle = true
            item.width = 120+padding*2
            tryCompare(title,"width",120); verify(title.height > 20)
            item.hasTitle = false; tryCompare(item,"height",30+padding*2)
        }
        function test_attention_data() {
            return [
                {tag:"red-low",hue:0,intensity:0,rgb:[0.52,0.1768,0.1768]},
                {tag:"green-low",hue:120,intensity:0,rgb:[0.1768,0.52,0.1768]},
                {tag:"blue-low",hue:240,intensity:0,rgb:[0.1768,0.1768,0.52]},
                {tag:"sea-middle",hue:210,intensity:5,rgb:[0.5584,0.2992,0.35]},
                {tag:"urgent",hue:210,intensity:10,rgb:[0.94,0.25,0.18]},
                {tag:"wrapped-negative",hue:-120,intensity:-2,rgb:[0.1768,0.1768,0.52]},
                {tag:"wrapped-positive",hue:720,intensity:30,rgb:[0.94,0.25,0.18]},
                {tag:"nonfinite",hue:NaN,intensity:NaN,rgb:[0.1768,0.3484,0.52]}
            ]
        }
        function test_attention(data) {
            const item = createTemporaryObject(attentionFactory,parent,{hue:data.hue,intensity:data.intensity})
            verify(item); tryCompare(item,"width",112); compare(item.height,62)
            const host = findChild(item,"bleeckerAttentionContent")
            compare(findChild(item,"slot").parent,host); compare(host.x,16); compare(host.y,16)
            for (const dark of [false,true]) {
                BleeckerTheme.dark = dark
                const c = item.accent, l = item.labelAccent, rgb = data.rgb
                near(c.r,rgb[0]); near(c.g,rgb[1]); near(c.b,rgb[2])
                const mix = dark ? 0.45 : 0.12, target = dark ? 1 : 0
                near(l.r,rgb[0]*(1-mix)+target*mix)
                near(l.g,rgb[1]*(1-mix)+target*mix)
                near(l.b,rgb[2]*(1-mix)+target*mix)
                near(item.accentOpacity,(dark ? 0.12 : 0.06)+item.urgency*(dark ? 0.037 : 0.018))
            }
        }
        function test_status_data() {
            const rows = []
            for (const dark of [false,true]) for (const variant of ["default","live","offline","warning","info"])
                rows.push({tag:dark+"-"+variant,dark:dark,variant:variant})
            return rows
        }
        function test_status(data) {
            BleeckerTheme.dark = data.dark
            const item = createTemporaryObject(statusFactory,parent,{variant:data.variant})
            const label = findChild(item,"bleeckerStatusLabel"), dot = findChild(item,"bleeckerStatusDot")
            const key = {default:"textPrimary",live:"live",offline:"textSecondary",warning:"desert",info:"sea"}[data.variant]
            compare(item.foregroundColor.toString(),BleeckerTheme.palette[key].toString())
            compare(item.width,label.implicitWidth+30); compare(item.height,24)
            compare(label.x,21); compare(dot.x,9); compare(dot.width,6); compare(dot.height,6)
            near(findChild(item,"bleeckerStatusBackground").color.a,0.1)
            compare(label.logicalPixelSize,11); BleeckerTheme.textScale = 1.5; compare(label.logicalPixelSize,16.5)
            compare(item.Accessible.name,"Ready"); compare(item.Accessible.role,Accessible.StaticText)
            item.text = "Longer state"; compare(label.text,item.text); compare(item.Accessible.name,item.text)
        }
        function test_notification_data() {
            return [-1,0,1,99,100,1000].map(n => ({tag:String(n),count:n}))
        }
        function test_notification(data) {
            const item = createTemporaryObject(notificationFactory,parent,{count:data.count})
            const label = findChild(item,"bleeckerNotificationLabel"), bg = findChild(item,"bleeckerNotificationBackground")
            compare(item.text,data.count > 99 ? "99+" : data.count.toLocaleString(Qt.locale(),"f",0))
            compare(item.width,label.implicitWidth+12); compare(item.height,18); compare(label.x,6)
            compare(label.color.toString(),"#ffffff"); compare(label.logicalPixelSize,10)
            compare(item.Accessible.name,String(data.count)+" notifications")
            BleeckerTheme.dark = true; BleeckerTheme.textScale = 1.5
            compare(bg.color.toString(),BleeckerTokens.colors.light.destructive.toString()); compare(label.logicalPixelSize,10)
            item.count = 3; compare(item.text,"3"); compare(item.Accessible.name,"3 notifications")
        }
        function test_eyebrow_case_tracking_and_scaling() {
            const item = createTemporaryObject(eyebrowFactory,parent)
            compare(item.text,"Mixed Case"); compare(item.logicalPixelSize,10)
            compare(item.font.weight,Font.Bold); compare(item.tracking,1.15)
            compare(item.resolvedFamily,"Encode Sans"); compare(item.color.toString(),BleeckerTheme.palette.desert.toString())
            BleeckerTheme.textScale = 1.5; compare(item.logicalPixelSize,10)
            compare(item.Accessible.name,item.text); verify(!item.Accessible.ignored)
        }
    }
}
