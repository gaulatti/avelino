import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino
Item {
    id:root;width:700;height:600
    property int mounts:0
    property int unmounts:0
    property string bodyText:"Body copy"
    PixelAlignment {id:metrics;target:root}
    Component {id:factory;BleeckerAccordion {title:"Details";width:320;content:counterBody}}
    Component {
        id:counterBody
        T.Button {
            objectName:"counterBody";property int count:0
            text:"Counter "+count;implicitWidth:label.implicitWidth;implicitHeight:label.implicitHeight
            padding:0;background:null;focusPolicy:Qt.StrongFocus
            onClicked:count++
            contentItem:ButtonLabel {id:label;text:parent.text;font.family:BleeckerTheme.primaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(12)}
            Component.onCompleted:root.mounts++
            Component.onDestruction:root.unmounts++
        }
    }
    Component {id:body;ButtonLabel {text:root.bodyText;font.family:BleeckerTheme.primaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(12);wrapWidth:parent.availableWidth}}
    Component {id:zeroBody;Item {implicitWidth:0;implicitHeight:0}}
    TestCase {
        name:"AccordionContracts";when:windowShown
        function init(){BleeckerTheme.reducedMotion=true;BleeckerTheme.textScale=1;root.mounts=0;root.unmounts=0;root.bodyText="Body copy";failOnWarning(/Binding loop/)}
        function cleanup(){BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true}
        function header(item){return findChild(item,"bleeckerAccordionHeader")}
        function titlePoint(item){const title=findChild(item,"bleeckerAccordionTitle");return Qt.point(title.x+5,title.y+title.height/2)}
        function titleClick(item){const p=titlePoint(item);mouseClick(header(item),p.x,p.y)}
        function test_lifecycle_and_hit_regions(){
            const item=createTemporaryObject(factory,root);compare(item.expanded,false);compare(item.height,45);compare(root.mounts,0)
            mouseClick(header(item),140,8);compare(item.expanded,false);compare(root.mounts,0)
            titleClick(item);tryCompare(item,"expanded",true);compare(item.height,70);tryCompare(root,"mounts",1)
            const first=item.loadedContent;mouseClick(first);compare(first.count,1)
            titleClick(item);tryCompare(item,"expanded",false);tryCompare(root,"unmounts",1);compare(item.loadedContent,null);compare(item.height,45)
            const glyph=findChild(item,"bleeckerAccordionChevron");mouseClick(header(item),glyph.x+glyph.width/2,glyph.y+glyph.height/2)
            tryCompare(item,"expanded",true);tryCompare(root,"mounts",2);compare(item.loadedContent.count,0)
        }
        function test_initial_value_and_later_updates(){
            const item=createTemporaryObject(factory,root,{initiallyExpanded:true});tryCompare(item,"expanded",true)
            const first=item.loadedContent;mouseClick(first);compare(first.count,1)
            item.initiallyExpanded=false;item.title="Updated title";compare(item.expanded,true);compare(item.loadedContent,first);compare(first.count,1)
        }
        function test_empty_zero_long_and_intrinsic(){
            const item=createTemporaryObject(factory,root,{initiallyExpanded:true,content:null});compare(item.height,45)
            item.content=zeroBody;tryCompare(item,"height",55)
            item.content=body;tryCompare(item,"height",70)
            item.title="";tryCompare(item,"height",67)
            item.title="Keep selected editions available for review";item.width=180;tryCompare(item,"height",104)
            item.title="Details";item.width=item.implicitWidth;tryCompare(item,"width",metrics.devicePixelRatio<2 ? 97 : 95.5)
        }
        function test_canceled_press_and_disabled(){
            const item=createTemporaryObject(factory,root),p=titlePoint(item)
            mousePress(header(item),p.x,p.y);verify(header(item).down)
            mouseMove(header(item),140,8);mouseRelease(header(item),140,8);compare(item.expanded,false)
            item.enabled=false;titleClick(item);compare(item.expanded,false);verify(!header(item).enabled)
            item.enabled=true;titleClick(item);compare(item.expanded,true)
        }
        function test_keyboard_and_content_updates(){
            const item=createTemporaryObject(factory,root,{content:body})
            header(item).forceActiveFocus(Qt.TabFocusReason);keyClick(Qt.Key_Space);tryCompare(item,"expanded",true)
            const first=item.loadedContent;root.bodyText="Updated body copy";compare(first.text,root.bodyText)
            keyClick(Qt.Key_Space);tryCompare(item,"expanded",false)
        }
        function test_motion_and_fixed_font(){
            const item=createTemporaryObject(factory,root);BleeckerTheme.reducedMotion=false
            titleClick(item);tryCompare(item,"expanded",true);verify(item.transitionProgress<1)
            tryCompare(item,"transitionProgress",1,1000)
            BleeckerTheme.textScale=1.5;compare(item.height,70)
            titleClick(item);BleeckerTheme.reducedMotion=true;tryCompare(item,"transitionProgress",0);compare(item.loadedContent,null)
        }
    }
}
