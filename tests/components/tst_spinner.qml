import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino
Item {
    id:root;width:640;height:400
    PixelAlignment {id:metrics;target:root}
    Component {id:factory;BleeckerLoadingSpinner {}}
    Component {id:buttonFactory;BleeckerButton {text:"Publish";loading:true}}
    TestCase {
        name:"SpinnerPresentation";when:windowShown
        function init(){BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=false;BleeckerTheme.textScale=1;failOnWarning(/Binding loop/)}
        function cleanup(){BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
        function test_source_sizes_data(){return [{tag:"small",size:"sm",edge:16},{tag:"medium",size:"md",edge:32},{tag:"large",size:"lg",edge:32}]}
        function test_source_sizes(data){
            const item=createTemporaryObject(factory,root,{size:data.size})
            verify(item instanceof T.BusyIndicator);compare(item.width,data.edge);compare(item.height,data.edge);compare(item.visualItem.width,data.edge)
            item.width=12;item.height=12;compare(item.visualItem.width,data.edge);compare(item.visualItem.height,data.edge)
            item.width=64;item.height=48;compare(item.visualItem.x,(64-data.edge)/2);compare(item.visualItem.y,(48-data.edge)/2)
        }
        function test_native_context_bounds_data(){return nativeSpinnerContexts.filter(c=>c.api==="BleeckerLoadingSpinner").map((c,i)=>({tag:"native-context-"+i,row:c}))}
        function test_native_context_bounds(data){
            const row=data.row;BleeckerTheme.dark=row.appearance==="dark"
            const item=createTemporaryObject(factory,root,{size:row.size,enabled:!row.disabled}),sourceIndicator=row.nativeProgressIndicators[0]
            compare(item.implicitWidth,row.componentSize.width);compare(item.implicitHeight,row.componentSize.height)
            compare(item.visualItem.width,sourceIndicator.width);compare(item.visualItem.height,sourceIndicator.height)
        }
        function test_native_loading_buttons_data(){return nativeSpinnerContexts.filter(c=>c.api==="BleeckerButton" && c.dpr===metrics.devicePixelRatio).map(c=>({tag:c.path,row:c}))}
        function test_native_loading_buttons(data){
            const row=data.row;BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            const item=createTemporaryObject(buttonFactory,root,{size:row.size,variant:row.variant})
            compare(item.width,row.componentSize.width);compare(item.height,row.componentSize.height)
            const spy=createTemporaryQmlObject('import QtTest; SignalSpy {}',root);spy.target=item;spy.signalName="clicked"
            mouseClick(item);compare(spy.count,0);item.loading=false;mouseClick(item);compare(spy.count,1)
        }
        function test_owned_spokes_and_color_updates(){
            const item=createTemporaryObject(factory,root);compare(item.animationPhase,0);compare(item.animating,false)
            for(let i=0;i<8;i++){
                const spoke=findChild(item,"bleeckerSpinnerSpoke"+i);verify(spoke!==null);compare(spoke.width,4);compare(spoke.height,10)
            }
            const first=findChild(item,"bleeckerSpinnerSpoke0");compare(first.opacity,70/255);compare(first.color,"#000000")
            BleeckerTheme.dark=true;compare(first.color,"#ffffff")
            item.color="#d63d3d";compare(first.color,"#d63d3d")
        }
        function test_animation_visibility_and_reduced_motion(){
            const item=createTemporaryObject(factory,root);compare(item.running,true);compare(item.focusPolicy,Qt.NoFocus)
            BleeckerTheme.reducedMotion=false;tryCompare(item,"animating",true);tryVerify(()=>item.animationPhase>0)
            BleeckerTheme.reducedMotion=true;tryCompare(item,"animating",false);compare(item.animationPhase,0);compare(item.running,true)
            item.visible=false;BleeckerTheme.reducedMotion=false;compare(item.animating,false)
            item.visible=true;tryCompare(item,"animating",true)
            item.running=false;tryCompare(item,"animating",false);compare(item.contentItem.visible,false)
        }
        function test_loading_button_suppression_and_restore(){
            const item=createTemporaryObject(buttonFactory,root);const spy=createTemporaryQmlObject('import QtTest; SignalSpy {}',root)
            spy.target=item;spy.signalName="clicked";mouseClick(item);compare(spy.count,0)
            item.loading=false;mouseClick(item);compare(spy.count,1)
            item.enabled=false;mouseClick(item);compare(spy.count,1)
        }
    }
}
