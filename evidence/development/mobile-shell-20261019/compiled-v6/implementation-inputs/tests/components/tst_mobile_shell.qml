import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino
import "../consumer" as Fixtures

Item {
    id:root
    width:900;height:600
    PixelAlignment {id:metrics;target:root}
    Component {id:factory;Fixtures.MobileShellCase {}}
    Component {id:slotFactory;ShellSlot {width:300;height:90;sourceComponent:Component {BleeckerButton {text:"Fixed caller";width:180;height:36}}}}
    TestCase {
        name:"DesktopMobileShellSource"
        when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;failOnWarning(/Binding loop/)}
        function cleanup(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
        function test_native_slots_data(){return nativeMobileShellProfiles.filter(r=>r.dpr===metrics.devicePixelRatio).map(r=>({tag:r.name,row:r}))}
        function test_native_slots(data){
            const row=data.row;BleeckerTheme.dark=row.dark
            const fixture=createTemporaryObject(factory,root,{definition:row})
            verify(fixture);wait(40)
            compare(fixture.toolbarItem.parent,null,"Unhosted toolbar must remain outside the body")
            const actual=fixture.snapshot().frames
            compare(Object.keys(actual).sort(),Object.keys(row.frames).sort())
            for(const name of Object.keys(row.frames))for(const axis of ["x","y","width","height"])
                compare(actual[name][axis],row.frames[name][axis],name+" "+axis)
        }
        function test_fixed_control_slot_keeps_explicit_size_and_bindings(){
            const slot=createTemporaryObject(slotFactory,root)
            verify(slot);wait(30)
            compare(slot.item.width,180);compare(slot.item.height,36)
            compare(slot.item.x,60);compare(slot.item.y,27)
            const caller=slot.item
            slot.width=400;slot.height=100;wait(30)
            compare(slot.item,caller);compare(caller.width,180);compare(caller.height,36)
            compare(caller.x,110);compare(caller.y,32)
        }
        function test_retained_caller_height_changes(){
            const row={width:360,height:240,header:36,footer:24,content:"flex",hiddenHeader:false}
            const fixture=createTemporaryObject(factory,root,{definition:row})
            wait(30);const header=fixture.shell.headerItem,footer=fixture.shell.footerItem
            fixture.definition=Object.assign({},row,{header:36.5,footer:300})
            wait(40);compare(fixture.shell.headerItem,header);compare(fixture.shell.footerItem,footer)
            compare(header.height,36.5);compare(footer.height,300)
            compare(fixture.shell.presentationItem.height,337.5)
        }
    }
}
