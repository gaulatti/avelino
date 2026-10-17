import QtQuick
import QtTest
import Avelino

Item {
    id:root;width:640;height:400
    PixelAlignment {id:pixel;target:root}
    Component {
        id:fixedNativeFactory
        Item {
            id:canvas;width:640;height:400
            required property var definition
            property alias modifier:surface
            property alias outer:centered
            Item {
                id:centered;anchors.centerIn:parent;anchors.alignWhenCentered:false
                width:canvas.definition.offer===null ? canvas.width:canvas.definition.offer
                height:canvas.definition.offer===null ? canvas.height:surface.implicitHeight
                BleeckerSurfaceModifier {
                    id:surface;anchors.fill:parent;radius:canvas.definition.resolvedRadius
                    maximumWidth:canvas.definition.offer===null ? canvas.width:canvas.definition.offer
                    Loader {
                        active:canvas.definition.content!=="empty";BleeckerLayout.flattenChildren:true
                        sourceComponent:Rectangle {
                            readonly property string kind:canvas.definition.content
                            width:kind==="zero" ? 0:kind==="wide" ? 800:kind==="rectangle" ? 72:kind==="fractional" ? 72.5:kind==="overflow" ? 80:96
                            height:kind==="zero" ? 0:kind==="wide" ? 80:["rectangle","overflow"].includes(kind) ? 44:kind==="fractional" ? 44.25:64
                            visible:kind!=="hidden";color:kind==="clear" ? "transparent":"#2c5784"
                        }
                    }
                }
            }
        }
    }
    Component {
        id:flatFactory
        BleeckerSurfaceModifier {
            width:640;height:400
            property alias first:a
            property alias second:b
            Rectangle {id:a;width:56;height:16;color:"red"}
            Rectangle {id:b;width:72;height:44;color:"blue"}
        }
    }
    Component {
        id:stackFactory
        BleeckerSurfaceModifier {
            width:640;height:400
            property alias stack:row
            ProposalRow {
                id:row;spacing:5
                Rectangle {width:56;height:16;color:"red"}
                Rectangle {width:72;height:44;color:"blue"}
            }
        }
    }
    Component {
        id:parentFactory
        ProposalRow {
            width:640;spacing:11
            property alias modifier:surface
            Rectangle {width:40;height:12}
            BleeckerSurfaceModifier {
                id:surface
                Rectangle {width:56;height:16}
                Rectangle {width:72;height:44}
            }
            Rectangle {width:30;height:20}
        }
    }
    Component {
        id:fontFactory
        BleeckerSurfaceModifier {
            width:640;height:400
            property alias scope:fontScope
            property alias label:label
            BleeckerFont {
                id:fontScope;family:"primary";size:32
                palette.windowText:"red"
                BleeckerText {id:label;text:"Caller"}
            }
        }
    }
    Component {
        id:buttonFactory
        BleeckerSurfaceModifier {
            width:300;height:100
            property alias caller:button
            BleeckerButton {
                id:button;text:"Caller "+localValue
                property int localValue:0
                onClicked:localValue++
            }
        }
    }
    Component {
        id:nestedFactory
        BleeckerSurfaceModifier {
            width:640;height:400;radius:24
            property alias inner:inner
            property alias first:first
            BleeckerSurfaceModifier {
                id:inner;radius:3
                Rectangle {id:first;width:56;height:16;color:"red"}
                Rectangle {width:72;height:44;color:"blue"}
            }
        }
    }
    Component {
        id:wrappingFactory
        ProposalOverlay {
            width:200;height:300;maximumWidth:60
            property alias modifier:surface
            property alias label:label
            BleeckerSurfaceModifier {
                id:surface
                BleeckerText {id:label;text:"Review the selected edition and verify delivery settings."}
            }
        }
    }
    Component {
        id:dynamicFactory
        BleeckerSurfaceModifier {
            width:640;height:400
            property alias model:repeater.model
            property alias scope:scope
            Item {
                id:scope;BleeckerLayout.flattenChildren:true
                Repeater {
                    id:repeater;model:2
                    Rectangle {width:40+index;height:20}
                }
            }
        }
    }
    TestCase {
        name:"SurfaceModifier";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true}
        function cleanup(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
        function rect(item){const p=item.mapToItem(root,0,0);return [p.x,p.y,item.width,item.height]}
        function nativeRect(frame){return [frame.x,frame.y,frame.width,frame.height]}
        function test_native_fixed_caller_frames_data(){
            return nativeSurfaceModifierCaptures.filter(function(row){
                return row.dpr===pixel.devicePixelRatio &&row.configuration.parentLayout==="zstack"
                    &&["clear","rectangle","fractional","opaque","overflow","hidden","empty","zero","wide"].includes(row.configuration.content)
            }).map(function(row){return {tag:row.configuration.fixture+"-"+row.appearance+"-"+row.textScale,row:row}})
        }
        function test_native_fixed_caller_frames(data){
            const row=data.row,definition=row.configuration
            BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            const canvas=createTemporaryObject(fixedNativeFactory,root,{definition:definition}),m=canvas.modifier
            tryCompare(m,"partCount",definition.content==="empty" ? 0:1);verify(waitForRendering(canvas))
            const frames=row.state.partInstances
            if(m.partCount){
                compare(rect(m.partAt(0)),nativeRect(frames.styled[0]))
                compare(rect(m.partAt(0).callerItem),nativeRect(frames.caller[0]))
                compare(rect(canvas.outer),definition.offer===null ? [0,0,640,400]:nativeRect(frames.root[0]))
            }else compare(frames,{})
        }
        function test_flat_leaves_keep_independent_frames(){
            const m=createTemporaryObject(flatFactory,root)
            tryCompare(m,"partCount",2);verify(waitForRendering(m))
            compare(rect(m.partAt(0)),[292,192,56,16]);compare(rect(m.partAt(1)),[284,178,72,44])
            compare(rect(m.first),rect(m.partAt(0)));compare(rect(m.second),rect(m.partAt(1)))
            const a=m.partAt(0),b=m.partAt(1),caller=m.first
            for(const radius of [-12,0,0.5,12,48,200]){
                m.radius=radius;BleeckerTheme.dark=!BleeckerTheme.dark;BleeckerTheme.textScale=1.5
                verify(waitForRendering(m));compare(m.partAt(0),a);compare(m.partAt(1),b);compare(m.first,caller)
                compare(rect(a),[292,192,56,16]);compare(rect(b),[284,178,72,44])
            }
        }
        function test_explicit_stack_is_one_caller(){
            const m=createTemporaryObject(stackFactory,root)
            tryCompare(m,"partCount",1);verify(waitForRendering(m))
            compare(m.partAt(0).callerItem,m.stack);compare(rect(m.partAt(0)),[253.5,178,133,44])
        }
        function test_parent_row_receives_flat_parts(){
            const row=createTemporaryObject(parentFactory,root),m=row.modifier
            tryCompare(m,"partCount",2);verify(waitForRendering(row))
            compare(row.implicitWidth,231);compare(m.partAt(0).x,51);compare(m.partAt(1).x,118)
            compare(m.partAt(0).y,14);compare(m.partAt(1).y,0)
        }
        function test_font_scope_and_baseline_are_preserved(){
            const m=createTemporaryObject(fontFactory,root)
            tryCompare(m,"partCount",1);verify(waitForRendering(m))
            const caller=m.label,part=m.partAt(0),height=caller.implicitHeight,baseline=caller.baselineOffset
            compare(part.parent,m.scope.contentItem);compare(part.callerItem,caller)
            compare(caller.font.family,BleeckerFonts.primary);compare(caller.font.pixelSize,32)
            compare(caller.color.toString(),"#ff0000");verify(part.containsTextBaseline)
            compare(part.baselineOffset,baseline);compare(part.height,height)
            m.radius=0;verify(waitForRendering(m));compare(m.label,caller);compare(caller.font.pixelSize,32)
        }
        function test_input_focus_state_and_accessibility_survive_updates(){
            const m=createTemporaryObject(buttonFactory,root)
            tryCompare(m,"partCount",1);verify(waitForRendering(m))
            const caller=m.caller,input=caller.inputItem,part=m.partAt(0)
            mouseClick(caller,caller.width/2,caller.height/2);compare(caller.localValue,1)
            input.forceActiveFocus();keyClick(Qt.Key_Space);compare(caller.localValue,2)
            for(const radius of [0,48,12]){
                m.radius=radius;BleeckerTheme.dark=!BleeckerTheme.dark;verify(waitForRendering(m))
                compare(m.caller,caller);compare(m.partAt(0),part);compare(caller.localValue,2)
                verify(input.activeFocus);compare(fixtureSetup.accessibleName(input),"Caller 2")
            }
            keyClick(Qt.Key_Space);compare(caller.localValue,3)
        }
        function test_dynamic_flat_scopes_and_repeater_removal(){
            const m=createTemporaryObject(dynamicFactory,root)
            tryCompare(m,"partCount",2);verify(waitForRendering(m))
            m.model=3;tryCompare(m,"partCount",3);verify(waitForRendering(m))
            m.model=0;tryCompare(m,"partCount",0)
            m.model=1;tryCompare(m,"partCount",1)
            m.scope.BleeckerLayout.flattenChildren=false;tryCompare(m,"partCount",1)
            tryVerify(function(){return m.partAt(0).callerItem===m.scope})
            m.scope.BleeckerLayout.flattenChildren=true;tryCompare(m,"partCount",1)
            tryVerify(function(){return m.partAt(0).callerItem!==m.scope})
        }
        function test_hidden_empty_and_zero_callers(){
            const m=createTemporaryObject(flatFactory,root)
            tryCompare(m,"partCount",2);m.first.visible=false;verify(waitForRendering(m))
            compare(m.partAt(0).width,56);compare(m.partAt(0).height,16)
            m.first.width=0;m.first.height=0;tryCompare(m.partAt(0),"width",0);tryCompare(m.partAt(0),"height",0)
            m.first.BleeckerLayout.participates=false;tryCompare(m,"partCount",1)
            m.second.BleeckerLayout.participates=false;tryCompare(m,"partCount",0)
        }
        function test_nested_modifiers_keep_two_layers_per_leaf(){
            const m=createTemporaryObject(nestedFactory,root)
            tryCompare(m,"partCount",2);verify(waitForRendering(m))
            const outer=m.partAt(0),inner=outer.callerItem,caller=m.first
            compare(inner.callerItem,caller);compare(outer.radius,24);compare(inner.radius,3)
            compare(rect(outer),[292,192,56,16]);compare(rect(inner),rect(outer));compare(rect(caller),rect(inner))
            m.radius=48;m.inner.radius=0;verify(waitForRendering(m))
            compare(m.partAt(0),outer);compare(outer.callerItem,inner);compare(inner.callerItem,caller)
            caller.BleeckerLayout.participates=false;tryCompare(m,"partCount",1)
            caller.BleeckerLayout.participates=true;tryCompare(m,"partCount",2)
        }
        function test_width_proposals_reach_wrapping_caller(){
            const layout=createTemporaryObject(wrappingFactory,root)
            tryCompare(layout.modifier,"partCount",1);verify(waitForRendering(layout))
            const caller=layout.label,part=layout.modifier.partAt(0)
            tryCompare(caller,"offeredWidth",60);verify(caller.width<=60)
            const narrowHeight=caller.height
            layout.maximumWidth=160;tryCompare(caller,"offeredWidth",160)
            tryVerify(function(){return caller.height<narrowHeight})
            compare(layout.label,caller);compare(layout.modifier.partAt(0),part)
            compare(part.height,caller.height);compare(part.width,caller.width)
        }
    }
}
