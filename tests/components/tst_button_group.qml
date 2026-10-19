import QtQuick
import QtTest
import Avelino
import "../consumer" as Fixtures

Item {
    id: root
    width:320; height:180
    PixelAlignment { id:metrics; target:root }
    Component { id:factory; Fixtures.ButtonGroupCase {} }
    TestCase {
        name:"ButtonGroupSourceLayout"
        when:windowShown
        function init() { BleeckerTheme.dark=false; BleeckerTheme.textScale=1; failOnWarning(/Binding loop/) }
        function cleanup() { BleeckerTheme.dark=false; BleeckerTheme.textScale=1 }
        function test_source_frames_data() {
            return nativeButtonGroupCaptures.filter(row => row.dpr === metrics.devicePixelRatio)
                .map(row => ({tag:row.path,row:row}))
        }
        function frame(item) {
            const p=item.mapToItem(root,0,0)
            return {x:p.x,y:p.y,width:item.width,height:item.height}
        }
        function test_source_frames(data) {
            const row=data.row
            BleeckerTheme.dark=row.appearance === "dark"
            BleeckerTheme.textScale=row.textScale
            const item=createTemporaryObject(factory,root,{definition:row})
            verify(item)
            item.x=Qt.binding(() => (root.width-item.width)/2)
            item.y=Qt.binding(() => (root.height-item.height)/2)
            wait(30)
            for(const name of ["component","first","second"]) {
                if(row.frames[name] === undefined)continue
                const child=name === "component" ? item.presentationItem : findChild(item,name)
                verify(child,"Source child "+name)
                const actual=frame(child),expected=row.frames[name]
                for(const axis of ["x","y","width","height"])
                    compare(actual[axis],expected[axis],name+" "+axis)
            }
            if(row.variant === "hidden-block")compare(findChild(item,"first").visible,false)
        }
    }
}
