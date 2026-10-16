import QtQuick
import QtTest
import Avelino
Item {
    id:root;width:400;height:240
    property string original:"Initial description"
    property bool animate:false
    Rectangle {
        id:caller;x:40;y:40;width:120;height:40
        Accessible.role:Accessible.Button;Accessible.name:"Caller";Accessible.description:root.original
        Behavior on Accessible.description {
            enabled:root.animate
            SequentialAnimation {PauseAnimation {duration:80} PropertyAction {}}
        }
    }
    BleeckerTooltip {id:help;target:null;text:"Reader hint"}
    TestCase {
        name:"TooltipDescriptionBehavior";when:windowShown
        function description(){return fixtureSetup.accessibleDescription(caller)}
        function test_original_behavior_keeps_running(){
            compare(description(),"Initial description")
            root.animate=true;help.target=caller;tryVerify(()=>description()==="Reader hint")
            root.original="Deferred description";help.target=null;compare(description(),"Initial description")
            tryVerify(()=>description()==="Deferred description")
            root.original="After detach";compare(description(),"Deferred description")
            tryVerify(()=>description()==="After detach")
        }
    }
}
