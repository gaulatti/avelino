import QtQuick
import QtTest
import Avelino
Item {
    id:root;width:700;height:600
    property bool intrinsicActions:false
    property int mounts:0
    property int unmounts:0
    property int observedCounter:0
    PixelAlignment {id:metrics;target:root}
    Component {id:empty;BleeckerEmptyState {title:"No editions yet";message:"Create an edition to get started.";actions:action}}
    Component {id:error;BleeckerErrorState {message:"Create an edition to get started.";actions:action}}
    Component {id:overlay;BleeckerLoadingOverlay {}}
    Component {id:zero;Item {implicitWidth:0;implicitHeight:0}}
    Component {
        id:action
        BleeckerButton {
            property int count:0
            text:"Create "+count;maximumWidth:root.intrinsicActions ? -1 : parent.availableWidth
            onClicked:count++
            onCountChanged:root.observedCounter=count
            Component.onCompleted:{root.mounts++;root.observedCounter=count}
            Component.onDestruction:root.unmounts++
        }
    }
    Component {id:two;Row {spacing:12;BleeckerButton {text:"Create"} BleeckerButton {text:"Import";variant:"secondary"}}}
    Component {
        id:archive
        Item {implicitWidth:metrics.devicePixelRatio<2 ? 34 : 34.5;implicitHeight:metrics.devicePixelRatio<2 ? 30 : 30.5}
    }
    Component {
        id:loadingHarness
        Item {
            id:harness;width:640;height:400
            property string actionName:"center"
            property alias overlayVisible:busy.visible
            property alias overlayMessage:busy.message
            property alias count:under.count
            readonly property Item button:under
            BleeckerButton {
                id:under;property int count:0;text:"Underlying";onClicked:count++
                x:harness.actionName==="outside" ? 20 : 320-width/2
                y:harness.actionName==="edge" ? 305 : harness.actionName==="outside" ? 10 : 200-height/2
            }
            BleeckerLoadingOverlay {id:busy;x:160;y:50;width:320;height:300;visible:false;message:"Create an edition to get started."}
        }
    }
    TestCase {
        name:"PresentationStates";when:windowShown
        function init(){root.mounts=0;root.unmounts=0;root.intrinsicActions=false;BleeckerTheme.reducedMotion=true;BleeckerTheme.textScale=1;failOnWarning(/Binding loop/)}
        function cleanup(){BleeckerTheme.textScale=1;BleeckerTheme.dark=false}
        function test_native_geometry_data(){return nativePresentationCaptures.filter(c=>c.api!=="BleeckerButton" && c.dpr===metrics.devicePixelRatio).map(c=>({tag:c.path,row:c}))}
        function test_native_geometry(data){
            const row=data.row;root.intrinsicActions=row.variant==="intrinsic";BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            let item
            const props=row.variant==="intrinsic" ? {} : {width:Number(row.size)}
            if(row.api==="BleeckerLoadingOverlay"){if(row.variant!=="intrinsic")props.height=300;props.message=row.text;item=createTemporaryObject(overlay,root,props)}
            else {
                props.title=row.title;props.message=row.text;props.enabled=!row.flag;item=createTemporaryObject(row.api==="BleeckerErrorState" ? error : empty,root,props)
                if(row.actionsMode==="empty")item.actions=null
                if(row.actionsMode==="zero")item.actions=zero
                if(row.actionsMode==="two")item.actions=two
                if(row.variant==="custom-icon")item.icon=archive
            }
            const body=row.api==="BleeckerLoadingOverlay" ? item : item.presentationItem
            compare(body.width,row.componentSize.width);compare(body.height,row.componentSize.height)
            if(row.api!=="BleeckerLoadingOverlay")compare(item.loadedActions===null,row.actionsMode==="empty")
        }
        function test_updates_lifecycle_and_input(){
            const item=createTemporaryObject(empty,root,{width:320}),first=item.loadedActions
            compare(root.mounts,1);mouseClick(first);compare(first.count,1)
            item.title="Updated title";item.message="Updated message";compare(item.loadedActions,first);compare(first.count,1);compare(root.mounts,1)
            first.inputItem.forceActiveFocus(Qt.TabFocusReason);keyClick(Qt.Key_Space);compare(first.count,2)
            item.enabled=false;mouseClick(first);keyClick(Qt.Key_Space);compare(first.count,2)
            item.actions=null;tryCompare(root,"unmounts",1);compare(item.loadedActions,null)
            item.actions=action;tryCompare(root,"mounts",2);compare(item.loadedActions.count,0)
            mousePress(item.loadedActions);mouseMove(root,690,590);mouseRelease(root,690,590);compare(item.loadedActions.count,0)
        }
        function test_error_defaults_and_fixed_fonts(){
            const item=createTemporaryObject(error,root,{width:320});compare(item.title,"Something went wrong")
            const title=findChild(item,"bleeckerEmptyStateTitle"),message=findChild(item,"bleeckerEmptyStateMessage")
            compare(title.resolvedPixelSize,17);compare(message.resolvedPixelSize,13);compare(message.horizontalAlignment,Qt.AlignHCenter)
            BleeckerTheme.textScale=1.5;compare(title.resolvedPixelSize,17);compare(message.resolvedPixelSize,13)
            const loading=createTemporaryObject(overlay,root);compare(loading.message,"Loading…");compare(findChild(loading,"bleeckerLoadingOverlayMessage").resolvedPixelSize,14)
        }
        function test_native_action_states_data(){return nativePresentationBehavior.filter(b=>b.api!=="BleeckerLoadingOverlay").map((b,i)=>({tag:"source-action-"+i,row:b}))}
        function test_native_action_states(data){
            const row=data.row;BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            const factory=row.api==="BleeckerErrorState" ? error : empty
            let item=createTemporaryObject(factory,root,{title:"No editions yet",width:320,enabled:row.action!=="disabled-click"})
            const button=item.loadedActions
            if(row.action==="outside-release"){
                mousePress(button);mouseMove(root,690,590);mouseRelease(root,690,590)
            }else mouseClick(button)
            if(row.action==="producer-update"){item.title="Updated title";item.message="Updated message"}
            if(row.action==="remove" || row.action==="reopen"){item.destroy();wait(0);item=null}
            if(row.action==="reopen")item=createTemporaryObject(factory,root,{title:"No editions yet",width:320})
            compare(root.observedCounter,row.counter);compare(root.mounts,row.mounts);compare(root.unmounts,row.unmounts)
            compare(item!==null,row.presentAfterAction)
            if(item){compare(item.title,row.titleAfterAction);compare(item.message,row.messageAfterAction)}
        }
        function test_native_overlay_pointer_data(){return nativePresentationBehavior.filter(b=>b.api==="BleeckerLoadingOverlay").map((b,i)=>({tag:"source-overlay-"+i,row:b}))}
        function test_native_overlay_pointer(data){
            const row=data.row;BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            const harness=createTemporaryObject(loadingHarness,root,{actionName:row.action})
            mouseClick(harness.button);compare(harness.count,row.underlyingPositiveControl)
            harness.count=0;harness.overlayVisible=true
            if(row.action==="removed")harness.overlayVisible=false
            if(row.action==="producer-update")harness.overlayMessage="Updated loading message"
            mouseClick(harness.button);compare(harness.count,row.underlying);compare(harness.overlayVisible,row.overlayAfterAction);compare(harness.overlayMessage,row.messageAfterAction)
        }
    }
}
