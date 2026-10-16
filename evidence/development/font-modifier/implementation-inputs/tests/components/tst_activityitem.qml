import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino
import "../consumer" as Fixtures

Item {
    id:root;width:900;height:1250
    PixelAlignment {id:metrics;target:root}
    Component {id:factory;Fixtures.ActivityItemCase {}}
    Component {
        id:focusFactory
        Item {
            width:800;height:200
            T.Button {id:before;objectName:"beforeActivity";text:"Before";width:70;height:30;focusPolicy:Qt.StrongFocus}
            BleeckerActivityItem {
                x:100;y:40;maximumWidth:400;title:"Edition updated";detail:"Ready for review";timestamp:"2 min ago"
                BleeckerButton {objectName:"focusReview";text:"Review";size:"sm"}
                BleeckerButton {objectName:"focusArchive";text:"Archive";size:"sm"}
            }
            T.Button {objectName:"afterActivity";text:"After";x:650;width:70;height:30;focusPolicy:Qt.StrongFocus}
        }
    }
    TestCase {
        name:"ActivityItem";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
        function cleanup(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
        function definition(actions,width){return {fixture:"test",api:"BleeckerActivityItem",title:"Edition updated",detail:"Ready for review",timestamp:"2 min ago",symbol:"clock",actions:actions,proposalWidth:width,width:720,height:800,intrinsic:false,disabled:false,rtl:false,parentFont:0,parentForeground:"inherit",environmentLocale:"en_US"}}
        function create(actions,width){const item=createTemporaryObject(factory,root,{definition:definition(actions,width===undefined ? 400:width)});verify(item);settle(item);return item}
        function settle(item){waitForPolish(item.control);waitForPolish(findChild(item,"bleeckerActivityRow"));wait(5)}
        function update(item,values){const next=Object.assign({},item.definition,values);item.definition=next;settle(item)}
        function action(item,name){return findChild(item,"activityAction"+name)}
        function compareBounds(item,child,rect,message){
            // Source GeometryReader frames exclude text's device-pixel paint
            // translation. Compare layout positions separately from raster.
            let point={x:0,y:0},parent=child
            while(parent!==item.control){point.x+=parent.x;point.y+=parent.y;parent=parent.parent;verify(parent)}
            compare(child.width,rect.width,message+" width");compare(child.height,rect.height,message+" height")
            fuzzyCompare(point.x,rect.x,0.000001,message+" x");fuzzyCompare(point.y,rect.y,0.000001,message+" y")
        }
        function test_native_dense_layout_data(){
            // The native query tool keeps each profile alive for its complete
            // increasing-width sequence. Text retains measured wraps within
            // pixel-rounded fitted widths, so a fresh view is a different input.
            const groups={}
            for(const row of nativeActivityLayout){
                if(row.dpr!==metrics.devicePixelRatio || row.actions==="plain")continue
                const key=row.actions+"-"+row.textScale
                if(!groups[key])groups[key]={tag:key,rows:[]}
                groups[key].rows.push(row)
            }
            return Object.values(groups)
        }
        function test_native_dense_layout(data){
            const rows=data.rows;compare(rows.length,221);BleeckerTheme.textScale=rows[0].textScale
            const item=create(rows[0].actions,0),body=findChild(item,"bleeckerActivityRow")
            const names={badge:"bleeckerActivityBadge","text-column":"bleeckerActivityLabels",title:"bleeckerActivityTitle",detail:"bleeckerActivityDetail",timestamp:"bleeckerActivityTimestamp",spacer:"bleeckerActivitySpacer","action-review":"activityActionReview","action-archive":"activityActionArchive","action-nested":"activityActionNested","action-rect":"activityActionRect","action-tall":"activityActionTall","action-zero":"activityActionZero"}
            for(const row of rows){
                update(item,{proposalWidth:row.proposalWidth})
                const source=row.componentRect,prefix=row.actions+" width "+row.proposalWidth+" "
                compare(item.control.implicitWidth,source.width,prefix+"native fitted width")
                compare(item.control.implicitHeight,source.height,prefix+"native fitted height")
                for(const key of Object.keys(names)){
                    if(!row.witnessRects[key])continue
                    const child=findChild(item,names[key]);verify(child,key)
                    const rect=row.witnessRects[key]
                    compareBounds(item,child,{x:rect.x-source.x,y:rect.y-source.y,width:rect.width,height:rect.height},prefix+key)
                }
                compare(body.y,8)
            }
        }
        function test_caller_state_and_recreation(){
            const item=create("counter"),counter=action(item,"Counter")
            mouseClick(counter.inputItem);compare(counter.value,1);compare(item.appears,1)
            update(item,{title:"New title",detail:"New detail",timestamp:"Just now",symbol:"house"})
            compare(action(item,"Counter"),counter);compare(counter.value,1)
            mouseClick(counter.inputItem);compare(item.localValue,2)
            update(item,{actions:"empty"});verify(action(item,"Counter")===null);compare(item.disappears,1)
            update(item,{actions:"counter"});compare(item.localValue,0);compare(item.appears,2)
            update(item,{actions:"button"});compare(item.disappears,2)
            update(item,{actions:"counter"});compare(item.localValue,0);compare(item.appears,3)
            update(item,{disabled:true});mouseClick(action(item,"Counter").inputItem);compare(item.calls.length,2)
            update(item,{disabled:false});mouseClick(action(item,"Counter").inputItem);compare(item.calls.join(","),"counter,counter,counter")
        }
        function test_release_body_targets_and_cancellation(){
            const item=create("multi"),review=action(item,"Review"),archive=action(item,"Archive")
            for(const name of ["bleeckerActivityBadge","bleeckerActivityTitle","bleeckerActivityDetail","bleeckerActivityTimestamp","bleeckerActivitySpacer"]){mouseClick(findChild(item,name));compare(item.calls.length,0,name)}
            mouseClick(review.inputItem);mouseClick(archive.inputItem);compare(item.calls.join(","),"review,archive")
            mousePress(review.inputItem);mouseMove(root,890,1230);mouseRelease(root,890,1230);compare(item.calls.length,2)
            mousePress(review.inputItem);wait(1100);compare(item.calls.length,2);mouseRelease(review.inputItem);compare(item.calls.length,3)
            update(item,{disabled:true});mouseClick(review.inputItem);compare(item.calls.length,3)
            update(item,{disabled:false,actions:"hidden"});mouseClick(action(item,"Review").inputItem);compare(item.calls.length,3)
        }
        function test_press_updates_data(){return ["disabled","remove","width","title"].map(kind=>({tag:kind,kind:kind}))}
        function test_press_updates(data){
            const item=create("button"),input=action(item,"Review").inputItem,point=input.mapToItem(root,input.width/2,input.height/2)
            mousePress(input)
            if(data.kind==="disabled")update(item,{disabled:true})
            else if(data.kind==="remove")update(item,{actions:"empty"})
            else if(data.kind==="width")update(item,{proposalWidth:12})
            else update(item,{title:"Changed title"})
            mouseRelease(root,point.x,point.y);compare(item.calls.length,data.kind==="title" ? 1:0)
        }
        function test_fixed_labels_inherited_action_and_empty_line_boxes(){
            const item=create("plain"),title=findChild(item,"bleeckerActivityTitle"),detail=findChild(item,"bleeckerActivityDetail"),stamp=findChild(item,"bleeckerActivityTimestamp")
            update(item,{parentFont:32,parentForeground:"red"});BleeckerTheme.textScale=1.5;settle(item)
            compare(title.resolvedPixelSize,14);compare(detail.resolvedPixelSize,12);compare(stamp.resolvedPixelSize,10)
            compare(title.color,BleeckerTheme.nativeRed);compare(detail.color,BleeckerTheme.palette.textSecondary)
            compare(action(item,"Plain").logicalPixelSize,32)
            update(item,{title:"",detail:"",timestamp:"",actions:"empty"})
            for(const label of [title,detail,stamp]){compare(label.width,0);compare(label.height,14)}
            compare(item.control.implicitHeight,64)
        }
        function test_bidirectional_tab_traversal_has_only_action_stops(){
            const item=createTemporaryObject(focusFactory,root);verify(item);wait(20)
            const before=findChild(item,"beforeActivity"),after=findChild(item,"afterActivity"),review=findChild(item,"focusReview").inputItem,archive=findChild(item,"focusArchive").inputItem
            before.forceActiveFocus(Qt.TabFocusReason);verify(before.activeFocus)
            keyClick(Qt.Key_Tab);verify(review.activeFocus,"Forward Tab reaches first action")
            keyClick(Qt.Key_Tab);verify(archive.activeFocus,"Forward Tab reaches second action")
            keyClick(Qt.Key_Tab);verify(after.activeFocus,"Forward Tab leaves activity")
            keyClick(Qt.Key_Backtab);verify(archive.activeFocus,"Backward Tab reaches second action")
            keyClick(Qt.Key_Backtab);verify(review.activeFocus,"Backward Tab reaches first action")
            keyClick(Qt.Key_Backtab);verify(before.activeFocus,"Backward Tab leaves activity")
        }
    }
}
