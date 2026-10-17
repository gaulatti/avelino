import QtQuick
import QtTest
import Avelino

TestCase {
    id:testCase
    name:"ControlLifetime"
    width:400;height:240;when:windowShown
    property int destroyedControls:0
    Item {id:disabledParent;anchors.fill:parent;enabled:false}
    Component {
        id:inheritedControl
        InheritedControl {Component.onDestruction:++testCase.destroyedControls}
    }
    function test_destroy_control_under_disabled_parent() {
        const before=destroyedControls
        const control=inheritedControl.createObject(disabledParent)
        verify(control!==null);verify(!control.enabled)
        control.destroy();tryCompare(testCase,"destroyedControls",before+1);wait(1)
    }
}
