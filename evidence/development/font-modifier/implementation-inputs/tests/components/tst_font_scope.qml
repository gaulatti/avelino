import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

Item {
    id:root
    width:640;height:400
    PixelAlignment {id:pixel;target:root}
    Component {
        id:plainScope
        BleeckerFont {
            family:"primary";size:14
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            BleeckerText {objectName:"fontScopeText";text:"Keep edition"}
        }
    }
    Component {
        id:baselineScope
        ProposalRow {
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            property alias scope:font
            property alias reference:reference
            spacing:11;verticalAlignment:Qt.AlignBaseline
            BleeckerFont {id:font;family:"primary";size:14;BleeckerText {objectName:"fontScopeText";text:"Keep edition"}}
            Rectangle {id:reference;implicitWidth:3;implicitHeight:30;color:"#2c5784"}
        }
    }
    Component {
        id:nestedScope
        ProposalRow {
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            spacing:11
            Rectangle {implicitWidth:40;implicitHeight:12;color:"#a65d57"}
            BleeckerFont {
                id:outer;family:"secondary";size:48
                BleeckerFont {
                    family:"primary";size:14
                    BleeckerText {objectName:"first";text:"First child"}
                    Rectangle {objectName:"second";implicitWidth:72;implicitHeight:44;color:"#2c5784"}
                }
            }
            Rectangle {implicitWidth:30;implicitHeight:20;color:"#c1814d"}
        }
    }
    Component {
        id:scaleScope
        Item {
            width:640;height:400
            property real bleeckerTextScale:2
            property alias inner:inner
            BleeckerFont {
                family:"primary";size:14
                anchors.centerIn:parent;anchors.alignWhenCentered:false
                BleeckerFont {id:inner;family:"secondary";size:19;weight:"bold";BleeckerText {objectName:"fontScopeText";text:"Keep edition"}}
            }
        }
    }
    Component {
        id:pointerScope
        Item {
            width:640;height:400
            property int count:0
            property alias scope:font
            MouseArea {anchors.fill:parent;onClicked:parent.count++}
            BleeckerFont {
                id:font;family:"primary";size:14
                anchors.centerIn:parent;anchors.alignWhenCentered:false
                BleeckerText {objectName:"fontScopeText";text:"Keep edition"}
            }
        }
    }
    Component {
        id:inputScope
        BleeckerFont {
            family:"primary";size:14
            property int count:0
            T.Button {
                objectName:"fontScopeButton";width:100;height:40;implicitWidth:100;implicitHeight:40
                text:"Activate";focusPolicy:Qt.StrongFocus
                contentItem:T.Label {text:parent.text;font:parent.font;color:"#2d2d2d"}
                background:Rectangle {color:"#e6d5b8"}
                onClicked:parent.parent.count++
            }
        }
    }
    TestCase {
        name:"FontScope"
        when:windowShown
        function init(){BleeckerTheme.textScale=1;BleeckerTheme.dark=false;BleeckerTheme.reducedMotion=true}
        function cleanup(){BleeckerTheme.textScale=1;BleeckerTheme.dark=false}
        function nativeCase(id,scale){
            const row=nativeFontModifierCaptures.find(r=>r.configuration.fixture===id &&r.appearance==="light"
                &&r.textScale===scale &&r.dpr===pixel.devicePixelRatio)
            verify(row,"Missing native font context: "+id+" / "+scale)
            return row
        }
        function simple(row){const f=row.configuration;return f.fixture===f.family+"-"+f.weight || f.fixture.startsWith("size-")}
        function test_native_resolution_data(){
            return nativeFontModifierCaptures.filter(r=>r.dpr===pixel.devicePixelRatio &&simple(r)).map(r=>({
                tag:r.configuration.fixture+"-"+r.appearance+"-"+r.textScale,row:r}))
        }
        function test_native_resolution(data){
            const row=data.row,f=row.configuration
            BleeckerTheme.textScale=row.textScale;BleeckerTheme.dark=row.appearance==="dark"
            const font=createTemporaryObject(plainScope,root,{family:f.family,size:f.size,weight:f.weight})
            verify(font)
            const label=findChild(font,"fontScopeText")
            compare(font.requestedPixelSize,f.size*row.textScale)
            compare(font.resolvedPixelSize,row.state.ambientFontsAtProbe.label.resolvedPointSize)
            compare(label.font.pointSize,BleeckerFonts.pointSizeForPixels(row.state.ambientFontsAtProbe.label.resolvedPointSize))
            compare(font.partCount,1)
            compare(font.partAt(0),label)
            if(f.family!=="mono"){
                const expected=row.state.partInstances.label[0]
                tryCompare(label,"width",expected.width)
                tryCompare(label,"height",expected.height)
                const point=label.mapToItem(root,0,0)
                compare(point.x,expected.x);compare(point.y,expected.y)
                const styles={ultraLight:"Thin",thin:"ExtraLight",light:"Light",regular:"Regular",medium:"Medium",
                    semibold:"SemiBold",bold:"Bold",heavy:"ExtraBold",black:"Black"}
                compare(label.textRenderer.resolvedStyle,styles[f.weight])
            }
        }
        function test_native_first_baseline_data(){
            return nativeFontBaselineCaptures.filter(r=>r.dpr===pixel.devicePixelRatio &&simple(r)
                &&r.configuration.family!=="mono").map(r=>({tag:r.configuration.fixture+"-"+r.appearance+"-"+r.textScale,row:r}))
        }
        function test_native_first_baseline(data){
            const row=data.row,f=row.configuration
            BleeckerTheme.textScale=row.textScale;BleeckerTheme.dark=row.appearance==="dark"
            const parent=createTemporaryObject(baselineScope,root)
            verify(parent)
            parent.scope.family=f.family;parent.scope.size=f.size;parent.scope.weight=f.weight
            const label=findChild(parent,"fontScopeText"),expected=row.state.partInstances
            tryCompare(label,"baselineOffset",row.state.baselines.label)
            tryCompare(parent,"width",expected.parent[0].width)
            tryCompare(parent,"height",expected.parent[0].height)
            tryVerify(()=>{
                const point=label.mapToItem(root,0,0)
                return point.x===expected.label[0].x &&point.y===expected.label[0].y
            })
            const point=label.mapToItem(root,0,0)
            compare(point.x,expected.label[0].x);compare(point.y,expected.label[0].y)
            const ref=parent.reference.mapToItem(root,0,0)
            compare(ref.x,expected.reference[0].x);compare(ref.y,expected.reference[0].y)
            compare(point.y+label.baselineOffset,ref.y+30)
        }
        function test_nested_font_scopes_keep_flat_children(){
            const row=createTemporaryObject(nestedScope,root)
            verify(row)
            const expected=nativeCase("multi-parent-hstack",1).state.partInstances
            tryCompare(row,"width",expected.parent[0].width);tryCompare(row,"height",expected.parent[0].height)
            for(const key of ["first","second"]){
                const item=findChild(row,key),frame=expected[key][0]
                const point=item.mapToItem(root,0,0)
                compare(item.width,frame.width);compare(item.height,frame.height)
                compare(point.x,frame.x);compare(point.y,frame.y)
            }
        }
        function test_local_scale_inherits_without_multiplying(){
            const context=createTemporaryObject(scaleScope,root)
            verify(context)
            const label=findChild(context,"fontScopeText")
            tryCompare(context.inner,"textScale",2);compare(context.inner.resolvedPixelSize,38)
            const expected=nativeCase("content-scaled-subtree",1).state.partInstances.label[0]
            tryCompare(label,"width",expected.width);tryCompare(label,"height",expected.height)
            BleeckerTheme.textScale=1.5
            compare(context.inner.textScale,2);compare(context.inner.resolvedPixelSize,38)
            context.bleeckerTextScale=1.5
            tryCompare(context.inner,"resolvedPixelSize",29)
        }
        function test_updates_preserve_caller_and_accessibility(){
            const font=createTemporaryObject(plainScope,root),label=findChild(font,"fontScopeText")
            fixtureSetup.setAccessibilityActive(true)
            compare(fixtureSetup.accessibleName(label),"Keep edition")
            for(const family of ["secondary","primary"]){
                font.family=family;font.size=19.5;font.weight="black";BleeckerTheme.textScale=1.5
                compare(findChild(font,"fontScopeText"),label)
                compare(font.partAt(0),label)
                compare(font.resolvedPixelSize,29)
            }
            label.text="Caller update"
            compare(fixtureSetup.accessibleName(label),"Caller update")
        }
        function test_no_extra_pointer_target(){
            const context=createTemporaryObject(pointerScope,root),label=findChild(context,"fontScopeText")
            verify(context)
            mouseClick(label,label.width/2,label.height/2)
            compare(context.count,1)
        }
        function test_input_control_keeps_font_and_activation(){
            const font=createTemporaryObject(inputScope,root),button=findChild(font,"fontScopeButton")
            verify(font)
            compare(button.font.family,BleeckerFonts.primary)
            mouseClick(button,20,20)
            compare(font.count,1)
            BleeckerTheme.textScale=1.5;font.family="secondary"
            compare(findChild(font,"fontScopeButton"),button)
            compare(button.font.family,BleeckerFonts.secondary)
            button.forceActiveFocus();keyClick(Qt.Key_Space)
            compare(font.count,2)
        }
    }
}
