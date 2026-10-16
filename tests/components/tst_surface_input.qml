import QtQuick
import QtTest
import Avelino

Item {
    id:root;width:300;height:160
    Component {
        id:factory
        BleeckerSurface {
            width:140;height:60
            property alias caller:button
            BleeckerButton {
                id:button;anchors.fill:parent
                property int localValue:0
                text:"Caller "+localValue
                onClicked:localValue++
            }
        }
    }
    TestCase {
        name:"SurfaceCallerInput";when:windowShown
        function init(){BleeckerTheme.reducedMotion=true;BleeckerTheme.textScale=1;BleeckerTheme.dark=false}
        function cleanup(){BleeckerTheme.dark=false}
        function test_overlay_keeps_input_state_focus_and_accessibility_data(){
            return [{tag:"square",radius:0},{tag:"rounded",radius:12}]
        }
        function test_overlay_keeps_input_state_focus_and_accessibility(data){
            const surface=createTemporaryObject(factory,root,{radius:data.radius})
            const caller=surface.caller,parent=caller.parent,input=caller.inputItem
            verify(waitForRendering(surface))
            verify(fixtureSetup.accessibleAvailable(input));compare(fixtureSetup.accessibleName(input),"Caller 0")
            mouseClick(caller,caller.width/2,caller.height/2);compare(caller.localValue,1)
            input.forceActiveFocus();keyClick(Qt.Key_Space);compare(caller.localValue,2)
            for(const radius of [0,24,data.radius]){
                surface.radius=radius;BleeckerTheme.dark=!BleeckerTheme.dark
                verify(waitForRendering(surface))
                compare(surface.caller,caller);compare(caller.parent,parent);compare(caller.inputItem,input)
                compare(caller.localValue,2);verify(input.activeFocus)
                compare(fixtureSetup.accessibleName(input),"Caller 2")
            }
            keyClick(Qt.Key_Space);compare(caller.localValue,3)
        }
    }
}
