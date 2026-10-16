import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

Item {
    id:root;width:760;height:560
TestCase {
    id:testCase;name:"RadioGroup";when:windowShown
    width:760;height:560
    function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
    property var options:[{value:"daily",label:"Daily"},{value:"weekly",label:"Weekly"},{value:"monthly",label:"Monthly"}]
    Component {id:factory;BleeckerRadioGroup {property bool testRtl:false;LayoutMirroring.enabled:testRtl;LayoutMirroring.childrenInherit:true;selection:"daily";options:testCase.options}}
    Component {id:parentFactory;T.Control {font.family:"Libre Franklin";font.pointSize:BleeckerFonts.pointSizeForPixels(20);palette.windowText:"red";BleeckerRadioGroup {objectName:"inheritedRadio";selection:"daily";options:testCase.options}}}
    function create(properties) {const radio=createTemporaryObject(factory,root,properties || {});verify(radio);settle(radio);return radio}
    function settle(radio) {waitForPolish(radio);wait(5);if(radio.presentationItem)waitForPolish(radio.presentationItem);wait(5)}
    function clickOption(radio,index,part) {
        settle(radio);const input=radio.optionAt(index);verify(input);const item=part==="title" ? input.titleItem:input.iconItem
        mouseClick(item,item.width/2,item.height/2);wait(2)
    }
    function string(scalars) {let text="";for(const scalar of scalars)text+=String.fromCodePoint(scalar);return text}
    function test_sourceStringIdentity() {
        compare(nativeRadioStringPairs.length,13762)
        for(let i=0;i<nativeRadioStringPairs.length;i++) {
            const row=nativeRadioStringPairs[i]
            compare(BleeckerSelectionTools.stringsEqual(string(row.left),string(row.right)),row.equal,"Native String pair "+i)
        }
    }
    function test_controlledSelectionAndTargets() {
        const radio=create(),spy=createTemporaryObject(signalSpy,radio,{target:radio})
        compare(radio.optionAt(0).font.family,radio.font.family);fuzzyCompare(radio.optionAt(0).font.pointSize,radio.font.pointSize,0.000001)
        clickOption(radio,0,"icon");compare(spy.count,1);compare(spy.signalArguments[0][0],"daily");compare(radio.selection,"daily")
        clickOption(radio,1,"title");compare(spy.count,2);compare(spy.signalArguments[1][0],"weekly");compare(radio.selection,"daily");verify(!radio.optionAt(1).selected)
        const input=radio.optionAt(1),icon=input.iconItem,title=input.titleItem
        mouseClick(input,(icon.x+icon.width+title.x)/2,input.height/2);compare(spy.count,2)
        mouseClick(icon,icon.width/2,icon.height/2);compare(spy.count,3)
        mousePress(icon,icon.width/2,icon.height/2);wait(1200);compare(spy.count,3)
        mouseRelease(icon,icon.width/2,icon.height/2);compare(spy.count,4)
        mousePress(icon,icon.width/2,icon.height/2);mouseMove(root,700,540);mouseRelease(root,700,540);compare(spy.count,4)
    }
    Component {id:signalSpy;SignalSpy {signalName:"selectionRequested"}}
    function test_stableModelAndParentUpdates() {
        const radio=create(),spy=createTemporaryObject(signalSpy,radio,{target:radio}),first=radio.optionAt(0),second=radio.optionAt(1)
        radio.options=[{value:"monthly",label:"Renamed monthly"},{value:"daily",label:"Renamed daily"},{value:"weekly",label:"Renamed weekly",disabled:true}];settle(radio)
        compare(radio.optionAt(1),first);compare(radio.optionAt(2),second);compare(first.text,"Renamed daily");verify(!second.enabled);compare(spy.count,0)
        radio.selection="outside";settle(radio);compare(spy.count,0);for(let i=0;i<3;i++)verify(!radio.optionAt(i).selected)
        clickOption(radio,0,"icon");compare(spy.signalArguments[0][0],"monthly")
        radio.options=[];settle(radio);compare(radio.count,0);compare(radio.implicitWidth,0);compare(radio.implicitHeight,0);compare(spy.count,1)
    }
    function test_unicodeAndTypedValues() {
        const radio=create({selection:"e\u0301",options:[{value:"é",label:"Canonical"},{value:1,label:"Number"},{value:"1",label:"String"},{value:true,label:"Boolean"},{value:null,label:"None"}]}),spy=createTemporaryObject(signalSpy,radio,{target:radio})
        verify(radio.optionAt(0).selected);clickOption(radio,0,"icon");compare(spy.signalArguments[0][0],"é");compare(radio.selection,"e\u0301")
        for(const row of [[1,1],["1",2],[true,3],[null,4]]){radio.selection=row[0];settle(radio);for(let i=0;i<5;i++)compare(radio.optionAt(i).selected,i===row[1])}
        const object={id:"daily",payload:42},outside={id:"missing"}
        const custom=create({selection:outside,options:[{value:object,label:"Custom"}],valueIdentity:value=>value.id}),customSpy=createTemporaryObject(signalSpy,custom,{target:custom})
        verify(!custom.optionAt(0).selected);clickOption(custom,0,"icon");compare(customSpy.signalArguments[0][0],object)
        custom.selection={id:"daily",other:99};settle(custom);verify(custom.optionAt(0).selected)
    }
    function test_inheritedFontAndPalette() {
        const parent=createTemporaryObject(parentFactory,root);verify(parent);const radio=findChild(parent,"inheritedRadio");settle(radio)
        compare(radio.font.family,"Libre Franklin");fuzzyCompare(radio.glyphPixelSize,20,0.000001);compare(radio.foreground,Qt.color("red"))
        parent.font.family="Encode Sans";parent.font.pointSize=BleeckerFonts.pointSizeForPixels(30);parent.palette.windowText="blue";settle(radio)
        compare(radio.font.family,"Encode Sans");fuzzyCompare(radio.glyphPixelSize,30,0.000001);compare(radio.foreground,Qt.color("blue"))
        radio.font.pointSize=BleeckerFonts.pointSizeForPixels(13.5);settle(radio);fuzzyCompare(radio.glyphPixelSize,13.5,0.000001)
        compare(radio.optionAt(0).titleItem.resolvedPixelSize,14);fuzzyCompare(radio.optionAt(0).titleItem.capHeight,10.36,0.000001)
    }
    function test_layoutBoundaries() {
        const radio=create({orientation:Qt.Horizontal,maximumWidth:100});settle(radio)
        compare(radio.presentationItem.width,101);compare(radio.optionAt(0).titleItem.width,0);compare(radio.optionAt(0).titleItem.height,80)
        radio.orientation=Qt.Vertical;radio.maximumWidth=12;settle(radio)
        compare(radio.optionAt(0).titleItem.width,0);verify(radio.optionAt(0).titleItem.height>16)
        radio.maximumWidth=-1;radio.font.pointSize=BleeckerFonts.pointSizeForPixels(20);settle(radio)
        compare(radio.optionAt(0).iconItem.width,23);fuzzyCompare(radio.optionAt(0).implicitHeight,25.1,0.000001)
        radio.font.bold=true;settle(radio);compare(radio.optionAt(0).iconItem.width,24);fuzzyCompare(radio.optionAt(0).implicitHeight,25.6,0.000001)
        radio.font.bold=false;radio.font.pointSize=BleeckerFonts.pointSizeForPixels(0.3);settle(radio)
        compare(radio.optionAt(0).iconItem.width,0);compare(radio.optionAt(0).titleItem.resolvedPixelSize,12)
        radio.options=[{value:"daily",label:""}];settle(radio);compare(radio.optionAt(0).titleItem.height,14)
    }
    Component {
        id:centeredFactory
        Item {
            width:720;height:520
            property alias loader:probeLoader
            Loader {
                id:probeLoader;anchors.centerIn:parent;anchors.alignWhenCentered:false
                sourceComponent:T.Control {
                    implicitWidth:child.implicitWidth;implicitHeight:child.implicitHeight
                    padding:0;background:null
                    property alias radio:child
                    BleeckerRadioGroup {id:child;selection:"daily";options:testCase.options}
                }
            }
        }
    }
    function test_fractionalPresentationCenter() {
        const scene=createTemporaryObject(centeredFactory,root);verify(scene);const radio=scene.loader.item.radio
        for(const size of [0.3,13,13.5,20,30]) {
            radio.font.pointSize=BleeckerFonts.pointSizeForPixels(size);settle(radio)
            const local=radio.presentationItem.mapToItem(radio,0,0)
            fuzzyCompare(local.x,(radio.width-radio.presentationItem.width)/2,0.000001)
            fuzzyCompare(local.y,(radio.height-radio.presentationItem.height)/2,0.000001)
            const position=radio.presentationItem.mapToItem(scene,0,0)
            fuzzyCompare(position.x,(scene.width-radio.presentationItem.width)/2,0.000001)
            fuzzyCompare(position.y,(scene.height-radio.presentationItem.height)/2,0.000001)
        }
    }
    function test_horizontalReorderKeepsGeometry() {
        const radio=create({orientation:Qt.Horizontal}),first=radio.optionAt(0)
        radio.options=[{value:"monthly",label:"Monthly"},{value:"daily",label:"Daily"},{value:"weekly",label:"Weekly"}];settle(radio)
        compare(radio.optionAt(1),first);compare(radio.optionAt(0).x,0)
        fuzzyCompare(first.x,radio.optionAt(0).width+16,0.000001)
        fuzzyCompare(radio.optionAt(2).x,radio.optionAt(0).width+first.width+32,0.000001)
    }
    function test_rtlLeadingAlignment() {
        const radio=create({testRtl:true})
        verify(radio.mirrored);fuzzyCompare(radio.optionAt(0).x,radio.presentationItem.width-radio.optionAt(0).width,0.000001)
        radio.orientation=Qt.Horizontal;settle(radio);verify(radio.optionAt(0).x>radio.optionAt(1).x)
        verify(radio.optionAt(0).iconItem.x>radio.optionAt(0).titleItem.x)
    }
    function test_renameDuringPressKeepsButton() {
        const radio=create(),spy=createTemporaryObject(signalSpy,radio,{target:radio}),input=radio.optionAt(0),icon=input.iconItem
        const releasePoint=icon.mapToItem(root,Qt.point(icon.width/2,icon.height/2))
        mousePress(icon,icon.width/2,icon.height/2)
        radio.options=[{value:"daily",label:"Updated daily"},{value:"weekly",label:"Weekly"},{value:"monthly",label:"Monthly"}]
        settle(radio);compare(radio.optionAt(0),input);verify(input.pressed)
        mouseRelease(root,releasePoint.x,releasePoint.y);compare(spy.count,1);compare(spy.signalArguments[0][0],"daily")
    }
    function test_selectionChangeDuringPress() {
        const radio=create(),spy=createTemporaryObject(signalSpy,radio,{target:radio}),input=radio.optionAt(0),icon=input.iconItem
        const releasePoint=icon.mapToItem(root,Qt.point(icon.width/2,icon.height/2))
        mousePress(icon,icon.width/2,icon.height/2);radio.selection="monthly";settle(radio)
        mouseRelease(root,releasePoint.x,releasePoint.y);compare(spy.count,1);compare(spy.signalArguments[0][0],"daily");compare(radio.selection,"monthly")
    }
    function test_mutationDuringPress() {
        for(const mutation of ["disable","optionDisable","remove","reorder","orientation"]) {
            const radio=create(),spy=createTemporaryObject(signalSpy,radio,{target:radio}),input=radio.optionAt(0),icon=input.iconItem
            const releasePoint=icon.mapToItem(root,Qt.point(icon.width/2,icon.height/2))
            mousePress(icon,icon.width/2,icon.height/2)
            if(mutation==="disable")radio.enabled=false
            else if(mutation==="optionDisable")radio.options=[{value:"daily",label:"Daily",disabled:true},{value:"weekly",label:"Weekly"}]
            else if(mutation==="remove")radio.options=[{value:"weekly",label:"Weekly"}]
            else if(mutation==="reorder")radio.options=[{value:"monthly",label:"Monthly"},{value:"weekly",label:"Weekly"},{value:"daily",label:"Daily"}]
            else radio.orientation=Qt.Horizontal
            settle(radio)
            mouseRelease(root,releasePoint.x,releasePoint.y);compare(spy.count,0,mutation)
        }
    }
}

}
