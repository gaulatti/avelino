import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

Item {
    id: root
    width: 900; height: 650
    property int actions: 0
    Component { id: avatarFactory; BleeckerAvatar { name: "Jane Doe" } }
    Component { id: timelineFactory; BleeckerTimelineItem { title: "Published"; date: "12 Oct"; T.Label { objectName: "contentLabel"; text: "Bulletin ready"; color: palette.windowText } } }
    Component { id: surfaceFactory; BleeckerSurface { Rectangle { objectName: "surfaceSlot"; width: 80; height: 30; color: "red" } } }
    Component {
        id: surfaceBorderFactory
        BleeckerSurface {
            width:80;height:60
            property alias bodyColor:body.color
            Rectangle {id:body;anchors.fill:parent;color:"red"}
        }
    }
    Component {
        id: rowSlot
        Item { implicitHeight: row.height; property string label: row.label }
    }
    Component { id: actionRow; BleeckerButton { text: row.label; size: "xs"; onClicked: root.actions++ } }
    Component { id: listFactory; BleeckerDataList { width: 200; rowContent: rowSlot } }
    Component { id: panelFactory; BleeckerPanel { title: "A long panel title wraps at its allocated content width"; Rectangle { width: 30; height: 20 } } }
    TestCase {
        name: "DataDisplayContracts"
        when: windowShown
        function init() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1; BleeckerTheme.reducedMotion = true; root.actions = 0 }
        function cleanup() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1 }
        function test_avatar_sizes_data() {
            const rows = []
            for (const dark of [false,true]) for (const size of ["xs","sm","md","lg","xl"])
                rows.push({tag:dark+"-"+size,dark:dark,size:size})
            return rows
        }
        function test_avatar_sizes(data) {
            BleeckerTheme.dark = data.dark
            const item = createTemporaryObject(avatarFactory,root,{size:data.size})
            const edge = {xs:24,sm:32,md:40,lg:52,xl:72}[data.size]
            compare(item.width,edge); compare(item.height,edge)
            const label = findChild(item,"bleeckerAvatarInitials"), border = findChild(item,"bleeckerAvatarBorder")
            compare(label.text,"JD"); verify(Math.abs(label.logicalPixelSize-edge*0.32)<0.000001)
            compare(label.font.weight,Font.DemiBold); compare(label.color.toString(),BleeckerTheme.palette.sea.toString())
            compare(border.radius,edge/2); compare(border.border.width,1)
            compare(border.border.color.toString(),BleeckerTheme.palette.border.toString())
            compare(item.Accessible.name,"Jane Doe"); compare(item.Accessible.role,Accessible.Graphic)
            BleeckerTheme.textScale = 1.5; verify(Math.abs(label.logicalPixelSize-edge*0.32)<0.000001)
        }
        function test_avatar_initials_data() {
            return [{tag:"empty",name:"",expected:""},
                    {tag:"single",name:"Jane",expected:"J"},
                    {tag:"spaces",name:"  jane   doe third ",expected:"JD"},
                    {tag:"combining",name:"e\u0301mile A",expected:"E\u0301A"},
                    {tag:"emoji",name:"👩‍💻 Developer",expected:"👩‍💻D"},
                    {tag:"flag",name:"🇨🇱 Chile",expected:"🇨🇱C"},
                    {tag:"uppercase-expansion",name:"ßeta person",expected:"SSP"},
                    {tag:"literal-space-split",name:"a\tb C",expected:"AC"}]
        }
        function test_avatar_initials(data) {
            const item = createTemporaryObject(avatarFactory,root,{name:data.name})
            compare(item.initials,data.expected)
            item.name = "New Name"; compare(item.initials,"NN"); compare(item.Accessible.name,"New Name")
        }
        function test_avatar_image_cover_circle_and_reset() {
            const item = createTemporaryObject(avatarFactory,root,{size:"xl"})
            verify(waitForRendering(item))
            const empty = grabImage(item)
            item.source = Qt.resolvedUrl("../consumer/avatar-wide.ppm")
            tryCompare(item,"imageStatus",Image.Ready)
            const canvas = findChild(item,"bleeckerAvatarImage")
            verify(waitForRendering(canvas))
            const image = grabImage(item)
            // Software QuickTest snapshots include the displayed backdrop.
            // Compare that unchanged corner rather than assuming transparent pixels.
            compare(image.pixel(0,0),empty.pixel(0,0))
            const middle = Math.floor(image.width/2)
            compare(image.red(middle,middle),32); compare(image.green(middle,middle),96); compare(image.blue(middle,middle),192)
            verify(!findChild(item,"bleeckerAvatarInitials").visible)
            item.source = ""; tryCompare(item,"imageStatus",Image.Null)
            verify(findChild(item,"bleeckerAvatarInitials").visible)
            verify(waitForRendering(canvas)); verify(grabImage(item).equals(empty))
        }
        function test_list_order_padding_separators_and_mutation() {
            const item = createTemporaryObject(listFactory,root,{rows:[{id:1,label:"Alpha",height:20},{id:2,label:"Beta",height:40},{id:3,label:"Gamma",height:24}]})
            tryCompare(item,"contentHeight",146)
            compare(item.count,3)
            for (let i=0;i<3;++i) {
                const row = item.itemAtIndex(i), slot = findChild(row,"bleeckerDataSlot"+i)
                verify(row); compare(slot.y,10); compare(slot.item.label,["Alpha","Beta","Gamma"][i])
                compare(findChild(row,"bleeckerDataSeparator"+i).visible,i!==2)
            }
            item.rows = [{id:3,label:"Gamma",height:24},{id:1,label:"Alpha",height:20}]
            tryCompare(item,"contentHeight",85)
            compare(findChild(item.itemAtIndex(0),"bleeckerDataSlot0").item.label,"Gamma")
            item.rows = []; tryCompare(item,"count",0); tryCompare(item,"contentHeight",0)
        }
        function test_list_virtualization_and_interactive_slot() {
            const rows = []; for (let i=0;i<100;++i) rows.push({id:i,label:"Row "+i,height:20})
            const item = createTemporaryObject(listFactory,root,{rows:rows,height:100,cacheBuffer:0})
            tryCompare(item,"count",100)
            verify(item.itemAtIndex(0)); compare(item.itemAtIndex(50),null)
            item.positionViewAtIndex(50,ListView.Beginning); waitForPolish(item)
            tryVerify(() => item.itemAtIndex(50)!==null)
            compare(findChild(item.itemAtIndex(50),"bleeckerDataSlot50").item.label,"Row 50")
            item.rows = [{id:1,label:"Activate",height:20}]; item.rowContent = actionRow
            item.positionViewAtBeginning(); waitForPolish(item)
            tryVerify(() => item.itemAtIndex(0)!==null)
            const button = findChild(item.itemAtIndex(0),"bleeckerDataSlot0").item
            mouseClick(button,button.width/2,button.height/2); compare(root.actions,1)
            button.forceActiveFocus(); keyClick(Qt.Key_Space); compare(root.actions,2)
        }
        function test_timeline_content_font_connector_and_wrap() {
            const item = createTemporaryObject(timelineFactory,root,{width:300})
            const title = findChild(item,"bleeckerTimelineTitle"), date = findChild(item,"bleeckerTimelineDate")
            const host = findChild(item,"bleeckerTimelineContent"), content = findChild(item,"contentLabel")
            const dot = findChild(item,"bleeckerTimelineDot"), connector = findChild(item,"bleeckerTimelineConnector")
            compare(content.parent,host); compare(content.font.family,"Libre Franklin")
            verify(Math.abs(content.font.pointSize-BleeckerFonts.pointSizeForPixels(13))<0.000001)
            compare(title.logicalPixelSize,14); compare(date.logicalPixelSize,11); compare(date.resolvedFamily,"Libre Franklin")
            compare(dot.width,9); compare(dot.height,9); compare(connector.width,1); compare(connector.y,9)
            compare(host.x,21); compare(host.y,item.headerHeight+4)
            compare(item.height,item.headerHeight+4+host.implicitHeight+18)
            const initialHeight = item.height
            item.title = "A longer timeline title wraps at its allocated width"; item.width = 170
            tryVerify(() => title.height>date.height*2)
            verify(item.height>initialHeight)
            item.last = true; verify(!connector.visible)
            compare(item.height,item.headerHeight+4+host.implicitHeight)
        }
        function test_panel_constrained_title() {
            const item = createTemporaryObject(panelFactory,root,{width:180})
            const title = findChild(item,"bleeckerPanelTitle")
            tryVerify(() => title.height>40)
            compare(title.width,132); compare(title.wrapWidth,132)
            const tall = item.height
            item.width = 500; tryVerify(() => item.height<tall)
        }
        function test_surface_radius_theme_and_content_data() {
            return [{tag:"default-light",radius:12,dark:false},{tag:"custom-light",radius:18,dark:false},
                    {tag:"default-dark",radius:12,dark:true},{tag:"square-dark",radius:0,dark:true}]
        }
        function test_surface_radius_theme_and_content(data) {
            BleeckerTheme.dark = data.dark
            const item = createTemporaryObject(surfaceFactory,root,{radius:data.radius})
            tryCompare(item,"width",80); compare(item.height,30)
            compare(findChild(item,"surfaceSlot").parent,findChild(item,"bleeckerSurfaceContent"))
            const bg = findChild(item,"bleeckerSurfaceBackground"), shadow = findChild(item,"bleeckerSurfaceShadow")
            compare(bg.radius,data.radius); compare(bg.color.toString(),BleeckerTheme.palette.card.toString())
            verify(Math.abs(shadow.shadowColor.a-(data.dark ? 0 : 0.055))<=1/65535)
            compare(shadow.blurRadius,14); compare(shadow.offsetY,5)
        }
        function test_surface_border_above_content_data() {
            const rows=[]
            for(const dark of [false,true])for(const radius of [0,12])for(const opaque of [false,true])
                rows.push({tag:dark+"-"+radius+"-"+opaque,dark:dark,radius:radius,opaque:opaque})
            return rows
        }
        function test_surface_border_above_content(data) {
            BleeckerTheme.dark=data.dark
            const item=createTemporaryObject(surfaceBorderFactory,root,{radius:data.radius,bodyColor:data.opaque ? "red":"transparent"})
            verify(waitForRendering(item))
            const image=grabImage(item),middle=Math.floor(image.width/2)
            const inner=Math.floor(image.height/2)
            if(data.opaque){
                compare(image.red(middle,inner),255);compare(image.green(middle,inner),0);compare(image.blue(middle,inner),0)
                // The source overlays its one-point border after clipping the
                // caller, so an opaque caller cannot paint over this edge.
                compare(image.red(middle,0),data.dark ? 255:235)
                compare(image.green(middle,0),data.dark ? 20:0)
                compare(image.blue(middle,0),data.dark ? 20:0)
            }else if(!data.dark){
                // Moving the border above the caller must not paint it twice.
                compare(image.red(middle,0),235);compare(image.green(middle,0),235);compare(image.blue(middle,0),235)
                compare(image.red(middle,inner),255)
            }else{
                verify(image.red(middle,0)>image.red(middle,inner))
                verify(image.green(middle,0)>image.green(middle,inner))
                verify(image.blue(middle,0)>image.blue(middle,inner))
            }
        }
    }
}
