import QtQuick
import QtQuick.Window
import QtTest
import Avelino
import "../consumer" as Fixtures

Item {
    id:root;width:1000;height:1500
    PixelAlignment {id:metrics;target:root}
    Component {id:factory;Fixtures.ModalCase {}}
    Component {
        id:windowFactory
        Window {
            id:window;width:960;height:900;visible:true
            property alias counter:counter
            property alias modal:modal
            BleeckerModal {
                id:modal;title:"Edit edition";x:(window.width-width)/2;y:(window.height-height)/2
                BleeckerButton {id:counter;property int value:0;text:"Count "+value;variant:"secondary";size:"sm";onClicked:value++}
            }
        }
    }
    Component {
        id:dialogFactory
        Item {
            id:owner;width:960;height:900
            property alias dialog:dialog
            property int appears:0
            property int disappears:0
            BleeckerModalDialog {
                id:dialog;title:"Edit edition";x:100;y:100
                content:Component {
                    BleeckerButton {
                        objectName:"dialogCounter";property int value:0;text:"Count "+value;variant:"secondary";size:"sm";onClicked:value++
                        Component.onCompleted:owner.appears++
                        Component.onDestruction:if(owner)owner.disappears++
                    }
                }
            }
        }
    }
    TestCase {
        name:"Modal";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop|Object set as mask/)}
        function cleanup(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
        function definition(content){return {fixture:"test",title:"Edit edition",modalWidth:480,outerOffer:null,content:content,disabled:false,rtl:false,parentFont:0,parentRed:false,width:960,height:900}}
        function create(content){const item=createTemporaryObject(factory,root,{definition:definition(content)});verify(item);settle(item);return item}
        function settle(item){waitForPolish(item);if(item.control){waitForPolish(item.control);waitForPolish(findChild(item,"bleeckerModalHeaderRow"));waitForPolish(findChild(item,"bleeckerModalColumn"))};wait(5)}
        function update(item,values){item.definition=Object.assign({},item.definition,values);settle(item)}
        function rect(item,child){let x=0,y=0,p=child;while(p!==item){verify(p);x+=p.x;y+=p.y;p=p.parent};return {x:x,y:y,width:child.width,height:child.height}}
        function compareRect(actual,expected,message){for(const k of ["x","y","width","height"])fuzzyCompare(actual[k],expected[k],0.000001,message+" "+k)}
        function test_owned_font_source_geometry_data(){
            const pending=new Set(["unicode","bidi","content-inherited","parent-font32","parent-red"])
            return nativeModalCaptures.filter(r=>r.dpr===metrics.devicePixelRatio && !pending.has(r.configuration.fixture)).map(r=>({tag:r.configuration.fixture+"-"+r.appearance+"-"+r.textScale,row:r}))
        }
        function test_owned_font_source_geometry(data){
            const row=data.row;BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            const item=createTemporaryObject(factory,root,{definition:row.configuration});verify(item);settle(item)
            const parts=row.witness.parts
            compareRect(rect(item,item.presentationItem),parts.root,"root")
            const names={title:"bleeckerModalTitle",spacer:"bleeckerModalSpacer",close:"bleeckerModalClose",separator:"bleeckerModalSeparator","header-row":"bleeckerModalHeaderRow"}
            for(const key of Object.keys(parts)){
                if(key.startsWith("content-"))names[key]="modalContent-"+key.slice(8)
                if(!names[key])continue
                const child=findChild(item,names[key]);verify(child,key);compareRect(rect(item,child),parts[key],key)
            }
        }
        function test_content_identity_and_lifetime(){
            const item=create("counter"),first=findChild(item,"modalContent-counter")
            mouseClick(first.inputItem);compare(first.value,1);compare(item.appears,1)
            update(item,{title:"A newly revised edition",modalWidth:160});compare(findChild(item,"modalContent-counter"),first)
            mouseClick(first.inputItem);compare(first.value,2)
            update(item,{disabled:true});mouseClick(first.inputItem);compare(first.value,2)
            update(item,{disabled:false});mouseClick(first.inputItem);compare(first.value,3)
            update(item,{content:"empty"});compare(item.disappears,1);verify(findChild(item,"modalContent-counter")===null)
            update(item,{content:"counter"});compare(item.localValue,0);mouseClick(findChild(item,"modalContent-counter").inputItem);compare(item.localValue,1)
            item.mounted=false;settle(item);verify(item.control===null);compare(item.disappears,2)
            item.mounted=true;settle(item);compare(item.localValue,0);mouseClick(findChild(item,"modalContent-counter").inputItem);compare(item.localValue,1)
            compare(item.calls.join(","),"counter:1,counter:2,counter:3,counter:1,counter:1")
        }
        function test_dismiss_action_and_disabled(){
            const item=create("rectangle");mouseClick(item.control.closeInput);compare(item.dismissals,1)
            update(item,{disabled:true});mouseClick(item.control.closeInput);compare(item.dismissals,1)
        }
        function test_visual_clip_preserves_outside_input(){
            const item=create("wide-button"),button=findChild(item,"modalContent-wide-button"),body=item.presentationItem
            compare(button.width,828);compare(button.height,80)
            const center=button.mapToItem(root,button.width/2,button.height/2),left=body.mapToItem(root,0,0).x
            for(const x of [left-150,left-20,left,left+240,left+500])mouseClick(root,x,center.y)
            compare(item.calls.length,5)
            update(item,{disabled:true});mouseClick(root,left-20,center.y);compare(item.calls.length,5)
        }
        function test_native_clipped_input_data(){return nativeModalInputGroups.map(g=>({tag:g.configuration.fixture,group:g}))}
        function test_native_clipped_input(data){
            const item=createTemporaryObject(factory,root,{definition:data.group.configuration});verify(item);settle(item)
            const rows=nativeModalClippingQueries.filter(q=>q.fixture===data.group.configuration.fixture)
            for(const q of rows){
                const calls=item.calls.length,dismissals=item.dismissals
                fixtureSetup.clickModalPoint(item,q.point.x,q.point.y)
                compare(item.calls.length-calls,q.calls.length,"caller action "+q.xInModal)
                compare(item.dismissals-dismissals,q.windowVisible ? 0:1,"Close "+q.xInModal)
            }
        }
        function test_native_glyph_hit_region_data(){return nativeModalHitProfiles.filter(p=>p.dpr===metrics.devicePixelRatio).map(p=>({tag:"text"+p.textScale,profile:p}))}
        function test_native_glyph_hit_region(data){
            BleeckerTheme.textScale=data.profile.textScale
            const item=create("rectangle"),frame=data.profile.closeFrame
            for(const sample of data.profile.samples){
                const before=item.dismissals
                fixtureSetup.clickModalPoint(item,frame.x+frame.width/2+sample.x,frame.y+frame.height/2+sample.y)
                compare(item.dismissals-before,sample.activated ? 1:0,"glyph "+sample.x+","+sample.y)
            }
        }
        function test_controlled_editor_survives_layout_and_remount(){
            const item=create("editor");item.edition="Producer renamed edition";settle(item)
            update(item,{modalWidth:240,title:"Review edited edition"});compare(findChild(item,"modalContent-editor").text,item.edition)
            item.mounted=false;settle(item);item.mounted=true;settle(item);compare(findChild(item,"modalContent-editor").text,item.edition)
        }
        function test_default_dismissal_and_retained_window_reopen(){
            const window=createTemporaryObject(windowFactory,root);verify(window);tryCompare(window,"visible",true);waitForRendering(window.contentItem)
            mouseClick(window.counter.inputItem);compare(window.counter.value,1)
            mouseClick(window.modal.closeInput);tryCompare(window,"visible",false)
            window.visible=true;waitForRendering(window.contentItem);mouseClick(window.counter.inputItem);compare(window.counter.value,2)
            mouseClick(window.modal.closeInput);tryCompare(window,"visible",false)
        }
        function test_presented_dialog_dismisses_and_recreates_content(){
            const owner=createTemporaryObject(dialogFactory,root);verify(owner)
            owner.dialog.open();tryCompare(owner.dialog,"visible",true);tryVerify(()=>owner.dialog.modalItem!==null);waitForRendering(owner.dialog.modalItem)
            const first=findChild(owner.dialog.contentItem,"dialogCounter");verify(first);mouseClick(first.inputItem);compare(first.value,1);compare(owner.appears,1)
            mouseClick(owner.dialog.modalItem.closeInput);tryCompare(owner.dialog,"visible",false);tryCompare(owner,"disappears",1)
            owner.dialog.open();tryCompare(owner.dialog,"visible",true);waitForRendering(owner.dialog.modalItem)
            const next=findChild(owner.dialog.contentItem,"dialogCounter");verify(next);compare(next.value,0);compare(owner.appears,2)
            mouseClick(next.inputItem);compare(next.value,1)
            mouseClick(owner.dialog.modalItem.closeInput);tryCompare(owner.dialog,"visible",false);tryCompare(owner,"disappears",2)
        }
    }
}
