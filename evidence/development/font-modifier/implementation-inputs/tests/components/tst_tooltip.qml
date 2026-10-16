import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino
import "../consumer" as Fixtures

Item {
    id:root;width:1000;height:700
    Component {id:fixture;Fixtures.TooltipCase {}}
    Component {id:adapter;BleeckerTooltip {}}
    Component {id:control;BleeckerButton {text:"Caller";property int value:0;onClicked:value++}}
    Component {id:described;Rectangle {width:80;height:40;property string original:"Original";Accessible.role:Accessible.Button;Accessible.name:"Caller";Accessible.description:original}}
    Component {
        id:actionOwner
        Item {
            id:owner;width:400;height:100
            property string actionDescription:"Original action description"
            property string secondDescription:"Second action description"
            property string hint:"Action outcome"
            property bool helpAttached:false
            property T.Action activeAction:firstAction
            readonly property T.Action alternateAction:secondAction
            readonly property Item caller:caller
            readonly property Item sibling:sibling
            T.Action {id:firstAction;text:"First action";Accessible.name:text;Accessible.description:owner.actionDescription}
            T.Action {id:secondAction;text:"Second action";Accessible.name:text;Accessible.description:owner.secondDescription}
            T.Button {id:caller;width:120;height:40;action:owner.activeAction}
            T.Button {id:sibling;x:150;width:120;height:40;action:firstAction}
            BleeckerTooltip {target:owner.helpAttached ? caller:null;text:owner.hint}
        }
    }
    Component {id:implicitName;T.Button {width:120;height:40;text:"Implicit caller name";Accessible.role:Accessible.Button}}
    Component {id:bareNative;T.Button {width:120;height:40;text:"Native caller"}}
    Component {id:bareText;Text {text:"Plain caller text"}}
    Component {id:bareInput;TextInput {width:120;height:40;text:"Plain input"}}
    Component {id:bareEditor;TextEdit {width:120;height:80;text:"Plain editor"}}
    Component {
        id:windowOwner
        Window {
            id:owner;width:400;height:260;visible:true;title:"Tooltip owner lifecycle"
            readonly property Item caller:button
            readonly property BleeckerTooltip help:helpAdapter
            BleeckerButton {id:button;anchors.centerIn:parent;text:"Caller"}
            BleeckerTooltip {id:helpAdapter;target:button;text:"Caller help"}
        }
    }
    TestCase {
        name:"Tooltip";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;root.Window.window.requestActivate();tryVerify(()=>root.Window.window.active);mouseMove(root,990,690);failOnWarning(/Binding loop|Cannot assign|is not a signal/)}
        function cleanup(){mouseMove(root,990,690);fixtureSetup.setAccessibilityActive(false)}
        function description(item){return fixtureSetup.accessibleDescription(item)}
        function hint(item,value){tryVerify(()=>fixtureSetup.accessibleAvailable(item));tryVerify(()=>description(item)===value)}
        function definition(content){return {fixture:"test",content:content,hint:"Publishes the selected edition",disabled:false,rtl:false,parentFont:0,parentRed:false,width:640,height:400}}
        function create(content){const item=createTemporaryObject(fixture,root,{definition:definition(content)});verify(item);waitForPolish(item);wait(5);return item}
        function test_adapter_preserves_caller_geometry_and_state(){
            const item=create("button"),caller=item.control,parent=caller.parent
            mouseClick(caller.inputItem);compare(item.localValue,1);waitForPolish(caller);wait(5)
            const before=[caller.x,caller.y,caller.width,caller.height]
            item.definition=Object.assign({},item.definition,{hint:"Reviews the published edition"});wait(5)
            compare(item.control,caller);compare(caller.parent,parent);compare(item.appears,1);compare(item.destroyedCount,0);compare(item.localValue,1)
            compare([caller.x,caller.y,caller.width,caller.height].join(","),before.join(","))
            item.helpAttached=false;wait(5);compare(item.control,caller);mouseClick(caller.inputItem);compare(item.localValue,2)
            item.helpAttached=true;wait(5);compare(item.control,caller)
            item.mounted=false;wait(5);compare(item.control,null);compare(item.destroyedCount,1)
            item.mounted=true;wait(5);compare(item.localValue,0);compare(item.mountValues.join(","),"0,0")
        }
        function test_accessible_description_updates_and_restores_binding(){
            const caller=createTemporaryObject(described,root);verify(caller)
            const help=createTemporaryObject(adapter,root,{target:caller,text:"Action outcome"});verify(help)
            hint(caller,"Action outcome")
            caller.original="Producer revised description";wait(5);compare(description(caller),"Action outcome")
            help.text="Updated hint";compare(description(caller),"Updated hint")
            help.target=null;hint(caller,"Producer revised description")
            caller.original="Still bound";compare(description(caller),"Still bound")
            help.target=caller;hint(caller,"Updated hint")
            help.destroy();wait(5);compare(description(caller),"Still bound")
        }
        function test_hint_reaches_actual_button_input(){
            const item=create("button"),input=item.control.inputItem
            hint(input,item.definition.hint)
            item.definition=Object.assign({},item.definition,{hint:"Updated hint",disabled:true});wait(5)
            compare(description(input),"Updated hint");mouseClick(input);compare(item.localValue,0)
            item.helpAttached=false;hint(input,"")
        }
        function test_hover_popup_latches_text_without_focus_grab(){
            const item=create("button"),caller=item.control
            caller.inputItem.forceActiveFocus();verify(caller.inputItem.activeFocus)
            mouseMove(caller,caller.width/2,caller.height/2)
            tryCompare(item.help,"visible",true);compare(item.help.presentation.text,item.definition.hint)
            verify(caller.inputItem.activeFocus)
            item.definition=Object.assign({},item.definition,{hint:"New accessible hint"});wait(5)
            compare(item.help.presentation.text,"Publishes the selected edition")
            compare(description(caller.inputItem),"New accessible hint")
            mouseMove(root,990,690);tryCompare(item.help,"visible",false)
            mouseMove(caller,caller.width/2,caller.height/2);tryCompare(item.help,"visible",true)
            compare(item.help.presentation.text,"New accessible hint")
            item.helpAttached=false;tryCompare(item.help,"visible",false)
        }
        function test_empty_hint_has_no_popup(){
            const item=create("button");item.definition=Object.assign({},item.definition,{hint:""});wait(5)
            mouseMove(item.control,item.control.width/2,item.control.height/2);wait(20);compare(item.help.visible,false)
            compare(description(item.control.inputItem),"")
        }
        function test_target_removal_and_retargeting(){
            const first=createTemporaryObject(control,root,{x:20,y:20}),second=createTemporaryObject(control,root,{x:220,y:20})
            const help=createTemporaryObject(adapter,root,{target:first,text:"Help"});verify(help)
            hint(first.inputItem,"Help")
            help.target=second;hint(first.inputItem,"");hint(second.inputItem,"Help")
            second.destroy();wait(5);compare(help.target,null);compare(help.visible,false)
        }
        function test_native_action_proxy_and_shared_action_keep_updating(){
            fixtureSetup.setAccessibilityActive(true)
            const owner=createTemporaryObject(actionOwner,root);verify(owner)
            hint(owner.caller,"Original action description");hint(owner.sibling,"Original action description")
            owner.helpAttached=true;hint(owner.caller,"Action outcome")
            owner.actionDescription="Revised while attached";wait(5)
            compare(description(owner.caller),"Action outcome");compare(description(owner.sibling),"Revised while attached")
            owner.helpAttached=false;hint(owner.caller,"Revised while attached")
            owner.actionDescription="Revised after detach";hint(owner.caller,"Revised after detach")
            for(let i=0;i<8;i++){
                owner.helpAttached=true;hint(owner.caller,"Action outcome")
                owner.actionDescription="Revision "+i;owner.helpAttached=false;hint(owner.caller,"Revision "+i)
            }
        }
        function test_action_replacement_preserves_name_and_description(){
            fixtureSetup.setAccessibilityActive(true)
            const owner=createTemporaryObject(actionOwner,root,{helpAttached:true});verify(owner)
            hint(owner.caller,"Action outcome")
            owner.activeAction=owner.alternateAction;wait(5)
            compare(description(owner.caller),"Action outcome");compare(fixtureSetup.accessibleName(owner.caller),"Second action")
            owner.helpAttached=false;hint(owner.caller,"Second action description")
            owner.secondDescription="Updated second action";hint(owner.caller,"Updated second action")
            owner.helpAttached=true;hint(owner.caller,"Action outcome");owner.activeAction=null;wait(5)
            compare(description(owner.caller),"Action outcome");owner.helpAttached=false;hint(owner.caller,"")
        }
        function test_same_hint_value_remains_an_explicit_caller_description(){
            fixtureSetup.setAccessibilityActive(true)
            const owner=createTemporaryObject(actionOwner,root,{helpAttached:true});verify(owner)
            hint(owner.caller,"Action outcome")
            owner.caller.Accessible.description="Action outcome"
            owner.hint="New hint";hint(owner.caller,"New hint")
            owner.helpAttached=false;hint(owner.caller,"Action outcome")
            owner.actionDescription="An action update";wait(5);compare(description(owner.caller),"Action outcome")
            compare(description(owner.sibling),"An action update")
        }
        function test_framework_name_matches_the_unhinted_control(){
            const caller=createTemporaryObject(implicitName,root),reference=createTemporaryObject(implicitName,root,{x:150})
            verify(caller);verify(reference)
            const before=fixtureSetup.accessibleName(reference)
            const help=createTemporaryObject(adapter,root,{target:caller,text:"Hint"});verify(help);hint(caller,"Hint")
            compare(fixtureSetup.accessibleName(caller),before)
            help.text="Updated";compare(fixtureSetup.accessibleName(caller),before)
            help.target=null;wait(5);compare(fixtureSetup.accessibleName(caller),before)
        }
        function test_owner_window_hide_releases_the_popup(){
            const owner=createTemporaryObject(windowOwner,root);verify(owner)
            owner.requestActivate();tryVerify(()=>owner.active);waitForRendering(owner.caller)
            mouseMove(owner.caller,owner.caller.width/2,owner.caller.height/2);tryCompare(owner.help,"visible",true)
            owner.visible=false;tryCompare(owner.help,"visible",false)
            owner.visible=true;owner.requestActivate();tryVerify(()=>owner.active);waitForRendering(owner.caller)
            mouseMove(owner.contentItem,2,2);mouseMove(owner.caller,owner.caller.width/2,owner.caller.height/2)
            tryCompare(owner.help,"visible",true)
            owner.close();tryCompare(owner.help,"visible",false)
        }
        function test_shown_help_preserves_caller_activation(){
            const item=create("button"),caller=item.control
            mouseMove(caller,caller.width/2,caller.height/2);tryCompare(item.help,"visible",true)
            mouseClick(caller.inputItem);compare(item.localValue,1);compare(item.calls.join(","),"1")
        }
        function test_native_items_without_explicit_accessibility_metadata_data(){return [{tag:"button",factory:bareNative},{tag:"text",factory:bareText},{tag:"input",factory:bareInput},{tag:"editor",factory:bareEditor}]}
        function test_native_items_without_explicit_accessibility_metadata(data){
            const caller=createTemporaryObject(data.factory,root);verify(caller)
            const help=createTemporaryObject(adapter,root,{target:caller,text:"Native item hint"});verify(help)
            hint(caller,"Native item hint")
            help.target=null;wait(5);compare(description(caller),"")
            help.target=caller;hint(caller,"Native item hint")
        }
    }
}
