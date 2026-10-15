import QtQuick
import QtTest
import Avelino
import "../consumer" as Fixtures

Item {
    id:root;width:800;height:1040
    PixelAlignment {id:metrics;target:root}
    Component {id:factory;Fixtures.SidebarBrandCase {}}
    Component {id:sidebar;BleeckerSidebarItem {title:"Editions";selected:false;maximumWidth:320;property int calls:0;onClicked:calls++;icon:Fixtures.SidebarGlyph {}}}
    Component {id:lockup;BleeckerBrandLockup {name:"Bleecker";maximumWidth:240}}
    Component {id:onePoint;Rectangle {width:40;height:40;color:"white";BleeckerBrandMark {size:1;anchors.centerIn:parent}}}
    TestCase {
        name:"SidebarBrandContract";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
        function cleanup(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
        function test_source_geometry_data(){return nativeSidebarBrandCaptures.filter(c=>c.api!=="BleeckerButton" && c.dpr===metrics.devicePixelRatio).map(c=>({tag:c.path,row:c}))}
        function test_source_geometry(data){
            const row=data.row;BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            const item=createTemporaryObject(factory,root,{definition:row});verify(item);wait(30)
            const body=item.presentationItem;verify(body)
            compare(body.width,row.componentSize.width,"Source component width");compare(body.height,row.componentSize.height,"Source component height")
            if(row.api==="BleeckerSidebarItem"){
                const label=findChild(item,"bleeckerSidebarTitle"),box=findChild(item,"bleeckerSidebarTitleBox"),icon=findChild(item,"bleeckerSidebarIcon"),r=row.layoutWitnessRects
                compare(label.width,r.title.width);compare(label.height,r.title.height)
                compare(12+box.x,r.title.x-row.componentRect.x);compare((body.height-label.height)/2,r.title.y-row.componentRect.y)
                compare(icon.width,20);compare(icon.height,r.icon.height)
            }else if(row.api==="BleeckerBrandLockup"){
                const label=findChild(item,"bleeckerBrandLockupName"),mark=findChild(item,"bleeckerBrandLockupMark"),r=row.layoutWitnessRects
                compare(label.width,r.title.width);compare(label.height,r.title.height);compare(mark.width,25);compare(mark.height,32)
            }
        }
        function test_source_pointer_and_selection_data(){return nativeSidebarBrandBehavior.map((row,index)=>({tag:"native-"+index,row:row}))}
        function test_source_pointer_and_selection(data){
            const row=data.row;BleeckerTheme.textScale=row.textScale
            const item=createTemporaryObject(sidebar,root,{selected:row.initialSelected,enabled:row.action!=="disabled"});wait(20)
            const input=item.inputItem
            const x=row.action==="corner" ? 0.5:row.action==="blank-spacer" ? input.width-8:input.width/2
            const y=row.action==="corner" ? 0.5:input.height/2
            if(row.action==="outside-release"){mousePress(input,x,y);mouseMove(root,790,1020);mouseRelease(root,790,1020)}else mouseClick(input,x,y)
            if(row.action==="repeat")mouseClick(input,x,y)
            if(row.action==="producer-title")item.title="Updated sidebar title"
            if(row.action==="producer-selection" || row.action==="caller-selection")item.selected=!item.selected
            compare(item.calls,row.calls);compare(item.selected,row.selectedAfterAction);compare(item.title,row.titleAfterAction)
        }
        function test_keyboard_fixed_fonts_and_caller_updates(){
            const item=createTemporaryObject(sidebar,root);wait(20)
            const input=item.inputItem;input.forceActiveFocus(Qt.TabFocusReason);keyClick(Qt.Key_Space);compare(item.calls,1);compare(item.selected,false)
            item.title="Updated";item.selected=true;BleeckerTheme.textScale=1.5;wait(20)
            verify(input.activeFocus);compare(findChild(item,"bleeckerSidebarTitle").resolvedPixelSize,14)
            keyClick(Qt.Key_Space);compare(item.calls,2);compare(item.selected,true)
            item.enabled=false;keyClick(Qt.Key_Space);compare(item.calls,2)
        }
        function test_brand_name_updates_and_fixed_font(){
            const item=createTemporaryObject(lockup,root);wait(20);const mark=findChild(item,"bleeckerBrandLockupMark")
            item.name="First line\nSecond line";BleeckerTheme.textScale=1.5;wait(20)
            compare(findChild(item,"bleeckerBrandLockupMark"),mark);compare(findChild(item,"bleeckerBrandLockupName").resolvedPixelSize,20)
            item.name="";wait(20);compare(item.presentationItem.width,41);compare(item.presentationItem.height,32)
        }
        function test_one_point_template_has_no_visible_source_coverage(){
            const item=createTemporaryObject(onePoint,root);wait(30);const image=grabImage(item)
            for(let y=0;y<image.height;y++)for(let x=0;x<image.width;x++)compare(image.pixel(x,y),Qt.rgba(1,1,1,1))
        }
    }
}
