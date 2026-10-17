import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

TestCase {
    id:testCase;name:"DropdownMenu";when:windowShown;width:600;height:360;visible:true
    property var calls:[]
    property int labelCalls:0
    property string labelTitle:"Actions"
    property var removalTarget:null
    Item {id:scene;anchors.fill:parent}
    Component {id:entry;BleeckerMenuItem {property int token:0;title:"Repeated";onTriggered:{testCase.calls=testCase.calls.concat(token);if(testCase.removalTarget)testCase.removalTarget.items=[]}}}
    Component {id:plainLabel;BleeckerText {text:testCase.labelTitle}}
    Component {id:emptyLabel;Rectangle {width:80;height:30;color:"orange"}}
    Component {id:buttonLabel;T.Button {text:"Actions";onClicked:testCase.labelCalls++}}
    Component {id:styledLabel;BleeckerText {text:"Styled";font.pixelSize:28;font.weight:Font.Bold;color:"red"}}
    Component {
        id:groupedLabel
        Item {
            property alias first:first
            BleeckerText {id:first;text:"First"}
            BleeckerText {text:"Second";x:90}
            Rectangle {width:80;height:30;color:"orange"}
        }
    }
    Component {
        id:imageLabel
        Item {
            Image {source:Qt.resolvedUrl("../../assets/brand/BleeckerLogo.png");width:16.5;height:13}
            BleeckerText {text:"Actions"}
        }
    }
    Component {
        id:dropdown
        BleeckerDropdownMenu {x:100;y:50;label:plainLabel}
    }
    function makeItems(count){const result=[];for(let i=0;i<count;++i)result.push(createTemporaryObject(entry,scene,{token:i}));return result}
    function makeControl(count,label=plainLabel){const control=createTemporaryObject(dropdown,scene,{items:makeItems(count),label:label});verify(control!==null);tryVerify(()=>control.labelRoot!==null);return control}
    function opened(control){control.open();tryCompare(control.menu,"visible",true);tryCompare(control.menu,"count",control.count);waitForRendering(control.itemAt(0))}
    function init(){calls=[];labelCalls=0;labelTitle="Actions";removalTarget=null;BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
    function cleanup(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1}

    function test_metadata_context_ignores_parent_style_and_custom_scale() {
        const control=makeControl(3)
        tryCompare(control.labelMetadata,"text","Actions")
        const original=control.labelMetadata.textFont,initialWidth=control.implicitWidth,initialHeight=control.implicitHeight
        control.font.pixelSize=48;control.font.italic=true;control.font.underline=true
        control.palette.windowText="red";BleeckerTheme.textScale=1.5
        wait(30);compare(control.labelMetadata.textFont,original);compare(control.implicitWidth,initialWidth);compare(control.implicitHeight,initialHeight)
        control.width=400;control.height=0
        compare(control.presentationItem.width,initialWidth);compare(control.presentationItem.height,initialHeight)
        control.width=24;compare(control.presentationItem.width,24)
        control.controlSize="mini";tryVerify(()=>control.implicitHeight<initialHeight)
    }
    function test_first_text_hidden_and_opacity_metadata() {
        const control=makeControl(3,groupedLabel)
        tryCompare(control.labelMetadata,"text","First")
        control.labelRoot.first.opacity=0;wait(20);compare(control.labelMetadata.text,"First")
        control.labelRoot.first.visible=false;tryCompare(control.labelMetadata,"text","Second")
        control.visible=false;wait(20);compare(control.labelMetadata.text,"Second")
        control.visible=true;control.labelRoot.first.visible=true;tryCompare(control.labelMetadata,"text","First")
    }
    function test_unsupported_visual_label_has_indicator_only() {
        const control=makeControl(3,emptyLabel)
        tryCompare(control.labelMetadata,"hasText",false);tryCompare(control,"implicitWidth",19)
        verify(control.presentationItem.height>0)
    }
    function test_local_text_styling_and_owner_update() {
        const control=makeControl(3,styledLabel)
        tryCompare(control.labelMetadata,"text","Styled")
        compare(control.labelMetadata.textFont.pixelSize,28);compare(control.labelMetadata.textColor,"#ff0000")
        control.labelRoot.text="Changed";tryCompare(control.labelMetadata,"text","Changed")
    }
    function test_first_image_metadata_ignores_outer_image_frame() {
        const control=makeControl(3,imageLabel)
        tryVerify(()=>control.labelMetadata.imageSource.toString().length>0)
        const image=control.labelRoot.children[0]
        compare(control.labelMetadata.imageWidth,image.implicitWidth);compare(control.labelMetadata.imageHeight,image.implicitHeight)
        compare(control.labelMetadata.text,"Actions")
        image.width=200;image.height=80;waitForRendering(control)
        compare(control.labelMetadata.imageWidth,image.implicitWidth);compare(control.labelMetadata.imageHeight,image.implicitHeight)
    }
    function test_label_button_does_not_receive_trigger_input() {
        const control=makeControl(3,buttonLabel)
        tryCompare(control.labelMetadata,"text","Actions")
        mouseClick(control.presentationItem,control.presentationItem.width/2,control.presentationItem.height/2)
        tryCompare(control.menu,"visible",true);compare(labelCalls,0);compare(calls,[])
        control.close();tryCompare(control.menu,"visible",false);compare(calls,[])
    }
    function test_lazy_menu_repeated_titles_and_owner_callback() {
        const control=makeControl(3)
        compare(control.count,3);compare(control.menu.count,0)
        verify(control.items[0].id!==control.items[1].id)
        opened(control)
        const item=control.itemAt(1)
        compare(item.text,"Repeated");compare(item.systemImage,"circle")
        mouseClick(item,item.width/2,item.height/2)
        tryCompare(control.menu,"visible",false);wait(150);compare(calls,[1]);compare(control.menu.count,3)
    }
    function test_reorder_title_and_role_updates_keep_identity() {
        const control=makeControl(3);opened(control)
        const source=control.items.slice(),first=control.itemAt(0),second=control.itemAt(1)
        control.items=[source[1],source[0],source[2]]
        tryVerify(()=>control.itemAt(0)===second);compare(control.itemAt(1),first)
        source[1].title="Updated";source[1].destructive=true;source[1].systemImage="trash"
        tryCompare(second,"text","Updated");compare(second.destructive,true);compare(second.systemImage,"trash")
        mouseClick(second,second.width/2,second.height/2);compare(calls,[1])
    }
    function test_empty_and_disabled_trigger_reject_input() {
        const control=makeControl(0)
        mouseClick(control.presentationItem,control.presentationItem.width/2,control.presentationItem.height/2)
        compare(control.menu.visible,false);compare(calls,[])
        control.items=makeItems(3);control.enabled=false
        mouseClick(control.presentationItem,control.presentationItem.width/2,control.presentationItem.height/2)
        compare(control.menu.visible,false);compare(calls,[])
    }
    function test_keyboard_open_navigation_activation_and_escape() {
        const control=makeControl(3)
        control.presentationItem.forceActiveFocus();keyClick(Qt.Key_Down)
        tryCompare(control.menu,"visible",true);tryCompare(control.menu,"count",3)
        control.itemAt(0).forceActiveFocus();keyClick(Qt.Key_Down);keyClick(Qt.Key_Return)
        tryCompare(control.menu,"visible",false);compare(calls,[1])
        opened(control);control.itemAt(0).forceActiveFocus();keyClick(Qt.Key_Escape)
        tryCompare(control.menu,"visible",false);compare(calls,[1])
    }
    function test_callback_can_remove_all_rows() {
        const control=makeControl(3);opened(control);removalTarget=control
        const item=control.itemAt(0);mouseClick(item,item.width/2,item.height/2)
        tryCompare(control,"count",0);compare(calls,[0])
        tryCompare(control.menu,"visible",false)
    }
    function test_drag_release_activates_the_visible_target_once() {
        const control=makeControl(3);opened(control)
        const first=control.itemAt(0),last=control.itemAt(2)
        mousePress(first,first.width/2,first.height/2)
        mouseMove(last,last.width/2,last.height/2,-1,Qt.LeftButton)
        mouseRelease(last,last.width/2,last.height/2)
        tryCompare(control.menu,"visible",false);wait(150);compare(calls,[2])
    }
    function test_disable_during_press_cancels_activation() {
        const control=makeControl(3);opened(control)
        const item=control.itemAt(0);mousePress(item,item.width/2,item.height/2)
        control.enabled=false;mouseRelease(item,item.width/2,item.height/2);wait(150)
        compare(calls,[]);control.close()
    }
    function test_all_forty_commands_remain_scrollable() {
        const control=makeControl(40);opened(control)
        compare(control.menu.count,40);control.menu.contentItem.positionViewAtEnd()
        tryVerify(()=>control.menu.contentItem.contentY>0)
        const item=control.itemAt(39);waitForRendering(item);mouseClick(item,item.width/2,item.height/2)
        tryCompare(control.menu,"visible",false);wait(150);compare(calls,[39])
    }
}
