import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino
import "../consumer" as Fixtures

Item {
    id:root;width:1000;height:700
    PixelAlignment {id:metrics;target:root}
    Component {id:caseFactory;Fixtures.ButtonStyleCase {}}
    Component {
        id:nestedColumnFactory
        Item {
            id:owner;property real childWidth:60
            property alias row:row
            property alias column:column
            property alias smallChild:small
            ProposalRow {
                id:row
                ProposalColumn {
                    id:column
                    Rectangle {implicitWidth:owner.childWidth;implicitHeight:20;color:"red"}
                    Rectangle {id:small;implicitWidth:30;implicitHeight:10;color:"blue"}
                }
            }
        }
    }
    Component {id:emptyFactory;BleeckerButtonStyle {}}
    Component {
        id:fixedFactory
        BleeckerButtonStyle {
            id:style;x:200;y:100
            onClicked:labels[0].value++
            Rectangle {objectName:"callerLabel";implicitWidth:200;implicitHeight:80;color:"red";property int value:0}
        }
    }
    Component {id:zeroFactory;BleeckerButtonStyle {x:200;y:100;Item {}}}
    Component {
        id:fontFactory
        BleeckerButtonStyle {
            x:200;y:100
            T.Label {objectName:"callerLabel";text:"Review";color:palette.windowText}
        }
    }
    Component {
        id:ownFontFactory
        BleeckerButtonStyle {
            T.Label {
                objectName:"callerLabel";text:"Review";font.family:"Libre Franklin"
                font.pointSize:BleeckerFonts.pointSizeForPixels(13);font.weight:Font.Bold;color:"red"
            }
        }
    }
    Component {
        id:rowFactory
        Item {
            id:owner;x:100;y:100;width:640;height:400
            property int calls:0
            property alias style:style
            property alias row:row
            ProposalRow {
                id:row;spacing:11
                Rectangle {implicitWidth:40;implicitHeight:12;color:"green"}
                BleeckerButtonStyle {
                    id:style;onClicked:owner.calls++
                    Rectangle {implicitWidth:92.5;implicitHeight:27;color:"red";property string text:"First child"}
                    Rectangle {implicitWidth:72;implicitHeight:44;color:"blue"}
                }
                Rectangle {implicitWidth:30;implicitHeight:20;color:"orange"}
            }
        }
    }
    TestCase {
        name:"ButtonStyle";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop|Cannot assign|TypeError/)}
        function cleanup(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;fixtureSetup.setAccessibilityActive(false)}
        function settle(item){
            waitForPolish(item)
            const control=item instanceof BleeckerButtonStyle ? item:item.control
            if(control)tryVerify(()=>{
                const dpr=metrics.devicePixelRatio
                const aligned=value=>Math.sign(value)*Math.floor(Math.abs(value)*dpr+0.5)/dpr
                for(let index=0;index<control.partCount;++index){
                    const part=control.partAt(index),point=part.presentationItem.mapToItem(null,0,0),offset=part.contentOriginOffset
                    if(Math.abs(point.x+offset.x-aligned(point.x))>0.000001 || Math.abs(point.y+offset.y-aligned(point.y))>0.000001)return false
                }
                return true
            })
        }
        function make(factory){const item=createTemporaryObject(factory,root);verify(item);settle(item);return item}
        function test_empty_and_zero_are_distinct(){
            const empty=make(emptyFactory),zero=make(zeroFactory)
            compare(empty.partCount,0);compare(empty.implicitWidth,0);compare(empty.implicitHeight,0)
            compare(zero.partCount,1);compare(zero.implicitWidth,36);compare(zero.implicitHeight,40)
        }
        function test_caller_identity_and_disabled_action(){
            const style=make(fixedFactory),label=style.labels[0],part=style.partAt(0)
            compare(style.implicitWidth,236);compare(style.implicitHeight,80)
            mouseClick(part.inputItem);compare(label.value,1)
            style.variant="secondary";style.size="sm";BleeckerTheme.dark=true;settle(style)
            compare(style.labels[0],label);compare(style.partAt(0),part);compare(part.labelItem,label)
            compare(style.implicitWidth,228);compare(style.implicitHeight,80)
            style.enabled=false;mouseClick(part.inputItem);compare(label.value,1);compare(part.presentationItem.opacity,0.45)
            style.enabled=true;mouseClick(part.inputItem);compare(label.value,2)
        }
        function test_font_and_foreground_inherit_but_inner_override_wins(){
            const style=make(fontFactory),label=style.labels[0],own=make(ownFontFactory),explicit=own.labels[0]
            compare(label.font.family,"Encode Sans");fuzzyCompare(label.font.pointSize,BleeckerFonts.pointSizeForPixels(14),0.000001)
            compare(label.color,style.foregroundColor)
            style.size="lg";BleeckerTheme.textScale=1.5;settle(style);settle(own)
            fuzzyCompare(label.font.pointSize,BleeckerFonts.pointSizeForPixels(22.5),0.000001)
            compare(explicit.font.family,"Libre Franklin");fuzzyCompare(explicit.font.pointSize,BleeckerFonts.pointSizeForPixels(13),0.000001)
            compare(explicit.font.weight,Font.Bold);verify(Qt.colorEqual(explicit.color,"red"))
        }
        function test_flat_parts_participate_in_parent_layout(){
            const owner=make(rowFactory),style=owner.style
            owner.row.layout();settle(owner.row)
            compare(style.partCount,2);compare(owner.row.implicitWidth,339.5);compare(owner.row.implicitHeight,44)
            const first=style.partAt(0),second=style.partAt(1)
            compare(first.width,128.5);compare(first.height,40);compare(first.x,51)
            compare(second.width,108);compare(second.height,44);compare(second.x,190.5)
        }
        function test_shared_pressed_visuals_and_cross_part_cancel(){
            const owner=make(rowFactory),style=owner.style
            owner.row.layout();settle(owner.row)
            const first=style.partAt(0),second=style.partAt(1)
            mousePress(first.inputItem);verify(style.down);compare(owner.calls,0)
            mouseRelease(first.inputItem);compare(owner.calls,1);verify(!style.down)
            mousePress(second.inputItem);verify(style.down);compare(owner.calls,1)
            mouseRelease(second.inputItem);compare(owner.calls,2);verify(!style.down)
            mousePress(first.inputItem)
            const end=second.inputItem.mapToItem(root,second.inputItem.width/2,second.inputItem.height/2)
            mouseMove(root,end.x,end.y);mouseRelease(root,end.x,end.y)
            compare(owner.calls,2);verify(!style.down)
        }
        function test_transparent_corner_input_survives_pressed_transform(){
            const style=make(fixedFactory),part=style.partAt(0),label=style.labels[0]
            mousePress(part.inputItem,0.5,0.5);verify(style.down);compare(label.value,0)
            mouseRelease(part.inputItem,0.5,0.5);compare(label.value,1)
        }
        function test_zero_offer_retains_decorated_body_and_input(){
            const style=make(fixedFactory);style.widthOffer=0;settle(style)
            const part=style.partAt(0)
            compare(style.width,0);compare(part.width,0);compare(part.presentationItem.width,236)
            compare(part.inputItem.width,236);compare(part.inputItem.x,-118)
        }
        function test_row_refreshes_nested_column_before_measuring(){
            const owner=make(nestedColumnFactory)
            owner.row.layout();compare(owner.row.implicitWidth,60)
            owner.childWidth=83.5
            owner.row.layout()
            compare(owner.column.implicitWidth,83.5);compare(owner.column.width,83.5)
            compare(owner.row.implicitWidth,83.5)
            compare(owner.smallChild.x,26.75)
        }
        function test_native_keyboard_and_accessible_parts(){
            fixtureSetup.setAccessibilityActive(true)
            const owner=make(rowFactory),first=owner.style.partAt(0).inputItem,second=owner.style.partAt(1).inputItem
            first.forceActiveFocus();verify(first.activeFocus);keyClick(Qt.Key_Space);compare(owner.calls,1)
            tryVerify(()=>fixtureSetup.accessibleAvailable(first) && fixtureSetup.accessibleAvailable(second))
            compare(fixtureSetup.accessibleName(first),"First child");compare(fixtureSetup.accessibleName(second),"")
        }
        function test_style_context_changes_do_not_start_press_animation(){
            const style=make(fixedFactory),part=style.partAt(0),surface=findChild(part,"bleeckerButtonStyleBackground")
            verify(surface)
            BleeckerTheme.reducedMotion=false
            style.variant="secondary";compare(surface.color,style.fillColor)
            BleeckerTheme.dark=true;compare(surface.color,style.fillColor)
        }
        function rect(item,child){
            const origin=child.mapToItem(item,0,0)
            return {x:origin.x,y:origin.y,width:child.width,height:child.height}
        }
        function frameSets(item){
            const result={}
            function add(key,child){if(!result[key])result[key]=[];result[key].push(rect(item,child))}
            for(let index=0;index<item.control.partCount;++index){
                const part=item.control.partAt(index)
                add("body",part.presentationItem);add("root",part)
                add(item.definition.content==="multi" ? index===0 ? "first":"second":"label",part.labelItem)
            }
            if(item.parentLayout){add("parent",item.parentLayout);add("leading",item.leadingItem);add("trailing",item.trailingItem)}
            for(const values of Object.values(result))values.sort((a,b)=>a.x-b.x || a.y-b.y || a.width-b.width || a.height-b.height)
            return result
        }
        function test_owned_font_source_frames_data(){
            return nativeButtonStyleCaptures.filter(r=>r.dpr===metrics.devicePixelRatio && !["content-system-font","text-unicode","text-bidi"].includes(r.configuration.fixture))
                .map(r=>({tag:r.configuration.fixture+"-"+r.appearance+"-"+r.textScale,row:r}))
        }
        function test_owned_font_source_frames(data){
            const row=data.row
            BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            const item=createTemporaryObject(caseFactory,root,{definition:row.configuration});verify(item);settle(item)
            if(item.parentLayout){item.parentLayout.layout();settle(item.parentLayout)}
            const actual=frameSets(item),expected=row.states[1].partInstances
            compare(Object.keys(actual).sort().join(","),Object.keys(expected).sort().join(","))
            for(const key of Object.keys(expected)){
                compare(actual[key].length,expected[key].length,key+" multiplicity")
                for(let index=0;index<expected[key].length;++index)
                    for(const field of ["x","y","width","height"])
                        fuzzyCompare(actual[key][index][field],expected[key][index][field],0.000001,key+"["+index+"]."+field)
            }
            compare(item.localValue,0);compare(item.calls.length,0)
            compare(item.mountValues.join(","),row.states[1].mountValues.join(","))
        }
    }
}
