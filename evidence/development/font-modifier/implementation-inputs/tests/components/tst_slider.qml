import QtQuick
import QtTest
import Avelino

Item {
    id: root
    width: 700; height: 300
    property real modelValue: 0.35
    property int edits: 0
    Component { id: factory; BleeckerSlider { width: 320 } }
    Component {
        id: boundFactory
        BleeckerSlider { width: 320; value: root.modelValue; onMoved: { root.modelValue=value;root.edits++ } }
    }
    TestCase {
        name: "SliderContracts"
        when: windowShown
        function init() { BleeckerTheme.dark=false;BleeckerTheme.textScale=1;root.modelValue=0.35;root.edits=0;failOnWarning(/Binding loop/) }
        function cleanup() { BleeckerTheme.dark=false;BleeckerTheme.textScale=1 }
        function test_layout_data() {
            const rows=[]
            for (const dark of [false,true]) for (const scale of [1,1.5]) for (const value of [0,0.35,1])
                rows.push({tag:[dark,scale,value].join('-'),dark,scale,value})
            return rows
        }
        function test_layout(d) {
            BleeckerTheme.dark=d.dark;BleeckerTheme.textScale=d.scale
            const slider=createTemporaryObject(factory,root,{value:d.value})
            compare(slider.height,16);compare(slider.handle.width,20);compare(slider.handle.height,16)
            fuzzyCompare(slider.handle.x,d.value*300,0.00001)
            const track=findChild(slider,"bleeckerSliderTrack"),fill=findChild(slider,"bleeckerSliderFill")
            compare(track.height,6);compare(track.y,5);fuzzyCompare(fill.width,d.value*320,0.00001)
        }
        function test_pointer_binding_external_updates_and_disabled() {
            const slider=createTemporaryObject(boundFactory,root)
            mouseClick(slider,319,8);compare(root.modelValue,1);verify(root.edits>0)
            mouseClick(slider,1,8);compare(root.modelValue,0)
            root.modelValue=0.8;fuzzyCompare(slider.value,0.8,0.00001)
            const count=root.edits;slider.enabled=false;mouseClick(slider,1,8)
            slider.forceActiveFocus();keyClick(Qt.Key_Right)
            compare(root.modelValue,0.8);compare(root.edits,count)
        }
        function test_drag_and_keyboard_qt_adapter() {
            const slider=createTemporaryObject(boundFactory,root)
            mousePress(slider,slider.handle.x+10,8);mouseMove(slider,235,8,20);mouseRelease(slider,235,8)
            fuzzyCompare(root.modelValue,0.75,0.00001)
            const next=createTemporaryObject(factory,root,{x:340})
            keyClick(Qt.Key_Tab);verify(next.activeFocus);keyClick(Qt.Key_Backtab)
            verify(slider.activeFocus);verify(slider.visualFocus)
            keyClick(Qt.Key_Right);fuzzyCompare(root.modelValue,0.85,0.00001)
            keyClick(Qt.Key_Left);fuzzyCompare(root.modelValue,0.75,0.00001)
        }
        function test_steps_and_bounds() {
            const slider=createTemporaryObject(factory,root,{from:10,to:22,stepSize:3,value:16})
            slider.forceActiveFocus();keyClick(Qt.Key_Right);compare(slider.value,19)
            keyClick(Qt.Key_Right);compare(slider.value,22);keyClick(Qt.Key_Right);compare(slider.value,22)
            mouseClick(slider,1,8);compare(slider.value,10)
            mouseClick(slider,160,8);compare(slider.value,16)
            slider.from=-5;slider.to=5;slider.stepSize=0.5;slider.value=-1.5
            keyClick(Qt.Key_Right);compare(slider.value,-1)
            slider.value=0.35;compare(slider.value,0.35)
            slider.from=0;slider.to=1;slider.stepSize=0.3;slider.value=0.3
            fuzzyCompare(slider.position,1/3,0.00001)
            mouseClick(slider,319,8);fuzzyCompare(slider.value,0.9,0.00001)
            slider.value=1;compare(slider.value,1);compare(slider.position,1)
            slider.to=0.3;slider.stepSize=0.1;slider.value=0.1
            compare(slider.intervals,3);mouseClick(slider,319,8)
            compare(slider.value,0.30000000000000004)
            slider.to=1;slider.stepSize=0.26;slider.value=0.26
            compare(slider.intervals,3);mouseClick(slider,319,8);compare(slider.value,0.78)
        }
        function test_dense_ticks_and_nonintegral_range() {
            const slider=createTemporaryObject(factory,root,{stepSize:0.000001,value:0.35})
            compare(slider.position,0.35);wait(30)
            verify(grabImage(slider).width>0)
        }
        function test_disabled_tab_traversal_and_rtl_geometry() {
            const slider=createTemporaryObject(factory,root)
            const disabled=createTemporaryObject(factory,root,{y:40,enabled:false})
            const next=createTemporaryObject(factory,root,{y:80})
            slider.forceActiveFocus(Qt.TabFocusReason);keyClick(Qt.Key_Tab);verify(next.activeFocus);verify(!disabled.activeFocus)
            slider.value=0.25;slider.LayoutMirroring.enabled=true
            fuzzyCompare(slider.handle.x,225,0.00001)
            fuzzyCompare(findChild(slider,"bleeckerSliderFill").x,240,0.00001)
        }
    }
}
