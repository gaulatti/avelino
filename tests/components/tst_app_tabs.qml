import QtQuick
import QtTest
import Avelino

Item {
    id:root;width:720;height:480
    TestCase {
        id:testCase;name:"AppTabBar";when:windowShown
        readonly property var tabs:[{value:"a",label:"Home",systemImage:"house"},{value:"b",label:"Inbox",systemImage:"tray",badge:7},{value:"c",label:"Settings",systemImage:"gearshape"}]
        Component {id:spyFactory;SignalSpy {signalName:"selectionRequested"}}
        Component {
            id:factory
            BleeckerAppTabBar {
                x:100;y:100;width:300;selection:"a";tabs:testCase.tabs
                property bool testRtl:false
                LayoutMirroring.enabled:testRtl;LayoutMirroring.childrenInherit:true
                icon:Component {Rectangle {implicitWidth:parent.selected ? 26:25;implicitHeight:24;color:parent.foregroundColor;Accessible.ignored:true}}
            }
        }
        Component {
            id:ownerFactory
            Item {
                width:400;height:150
                property string value:"a"
                property string mode:"echo"
                property var requests:[]
                property string pending:""
                property alias bar:bar
                BleeckerAppTabBar {
                    id:bar;width:300;selection:parent.value;tabs:testCase.tabs
                    icon:Component {Rectangle {implicitWidth:25;implicitHeight:24;color:parent.foregroundColor;Accessible.ignored:true}}
                    onSelectionRequested:requested=>{
                        const owner=parent;owner.requests=owner.requests.concat([requested])
                        if(owner.mode==="echo")owner.value=requested
                        else if(owner.mode==="delayed")owner.pending=requested
                        else if(owner.mode==="redirect")owner.value="c"
                    }
                }
            }
        }
        function settle(bar):void {wait(50);bar.presentationItem.children[1].layout();wait(20)}
        function create(properties) {const item=createTemporaryObject(factory,root,properties||{});verify(item);settle(item);return item}
        function click(bar,index) {const button=bar.tabAt(index);mouseClick(button,button.width/2,button.height/2);wait(20)}
        function cleanup(){fixtureSetup.setAccessibilityActive(false)}
        function test_requestOnlyAndReselection() {
            const bar=create(),spy=createTemporaryObject(spyFactory,bar,{target:bar})
            click(bar,1);compare(spy.count,1);compare(spy.signalArguments[0][0],"b");compare(bar.selection,"a");verify(bar.tabAt(0).selected)
            click(bar,0);compare(spy.count,2);compare(spy.signalArguments[1][0],"a")
            bar.selection="c";settle(bar);verify(bar.tabAt(2).selected)
        }
        function test_boundOwners_data(){return ["echo","observe","delayed","redirect"].map(mode=>({tag:mode,mode:mode}))}
        function test_boundOwners(data) {
            const owner=createTemporaryObject(ownerFactory,root,{mode:data.mode});verify(owner);settle(owner.bar)
            click(owner.bar,1);click(owner.bar,1);compare(owner.requests,["b","b"])
            compare(owner.value,data.mode==="echo" ? "b":data.mode==="redirect" ? "c":"a")
            owner.value="c";settle(owner.bar);verify(owner.bar.tabAt(2).selected)
            if(data.mode==="delayed"){compare(owner.pending,"b");owner.value=owner.pending;settle(owner.bar);verify(owner.bar.tabAt(1).selected)}
        }
        function test_disabledAndUnmatched() {
            const bar=create({selection:"outside",tabs:[{value:"a",label:"Home",systemImage:"house",disabled:true},{value:"b",label:"Inbox",systemImage:"tray"}]}),spy=createTemporaryObject(spyFactory,bar,{target:bar})
            verify(!bar.tabAt(0).selected &&!bar.tabAt(1).selected);click(bar,0);compare(spy.count,0)
            bar.selection="a";settle(bar);verify(bar.tabAt(0).selected);click(bar,0);compare(spy.count,0)
            bar.enabled=false;click(bar,1);compare(spy.count,0)
        }
        function test_exactBadgesAndLabels() {
            const bar=create({tabs:[{value:"a",label:"Home",systemImage:"house",badge:"-9223372036854775808"},{value:"b",label:"Inbox",systemImage:"tray",badge:0,accessibilityLabel:""},{value:"c",label:"Settings",systemImage:"gearshape",badge:"9223372036854775807",accessibilityLabel:"Preferences"}]})
            compare(bar.tabAt(0).notificationValue,"-9223372036854775808 notifications");verify(!bar.tabAt(0).badgeItem.visible)
            compare(bar.tabAt(1).notificationValue,"0 notifications");verify(!bar.tabAt(1).badgeItem.visible);compare(bar.tabAt(1).accessibleTitle,"")
            compare(bar.tabAt(2).notificationValue,"9223372036854775807 notifications");compare(bar.tabAt(2).tabBadgeText,"99+");verify(bar.tabAt(2).badgeItem.visible)
            compare(bar.tabAt(0).accessibleTitle,"Home");compare(bar.tabAt(2).accessibleTitle,"Preferences")
        }
        function test_canonicalAndTypedValues() {
            const bar=create({selection:"e\u0301",tabs:[{value:"é",label:"Canonical",systemImage:"house"},{value:1,label:"Number",systemImage:"house"},{value:"1",label:"String",systemImage:"house"},{value:true,label:"Boolean",systemImage:"house"}]})
            verify(bar.tabAt(0).selected)
            for(const row of [[1,1],["1",2],[true,3]]){bar.selection=row[0];settle(bar);for(let i=0;i<4;i++)compare(bar.tabAt(i).selected,i===row[1])}
            const custom=create({selection:{id:"first"},tabs:[{value:{id:"first",content:1},label:"First",systemImage:"house"}],valueIdentity:value=>value.id})
            verify(custom.tabAt(0).selected)
        }
        function test_retainedReorderAndEmpty() {
            const bar=create(),first=bar.tabAt(0)
            bar.tabs=[testCase.tabs[2],testCase.tabs[0],testCase.tabs[1]];settle(bar);compare(bar.tabAt(1),first)
            bar.tabs=[];settle(bar);compare(bar.count,0);compare(bar.presentationItem.width,0);compare(bar.implicitHeight,5)
            bar.tabs=testCase.tabs;settle(bar);compare(bar.count,3);verify(bar.tabAt(0)!==first)
        }
        function test_widthAndRtl() {
            const bar=create();for(let i=0;i<3;i++)fuzzyCompare(bar.tabAt(i).width,100,0.00001)
            bar.width=30;settle(bar);compare(bar.presentationItem.width,76);compare(bar.tabAt(0).width,26);compare(bar.tabAt(1).width,25);compare(bar.tabAt(2).width,25)
            bar.testRtl=true;settle(bar);verify(bar.tabAt(0).x>bar.tabAt(1).x &&bar.tabAt(1).x>bar.tabAt(2).x)
        }
        function test_actualAccessibility() {
            fixtureSetup.setAccessibilityActive(true)
            const bar=create({tabs:[{value:"a",label:"Home",systemImage:"house",badge:"9223372036854775807",accessibilityLabel:""},{value:"b",label:"Inbox",systemImage:"tray",badge:-1,disabled:true}]}),spy=createTemporaryObject(spyFactory,bar,{target:bar})
            tryVerify(()=>fixtureSetup.accessibleAvailable(bar.tabAt(0)))
            compare(fixtureSetup.accessibleName(bar.tabAt(0)),"")
            compare(fixtureSetup.accessibleValue(bar.tabAt(0)),"9223372036854775807 notifications")
            verify(fixtureSetup.accessibleSelected(bar.tabAt(0)))
            compare(fixtureSetup.accessibleValue(bar.tabAt(1)),"-1 notifications")
            fixtureSetup.accessiblePress(bar.tabAt(1));compare(spy.count,0)
            fixtureSetup.accessiblePress(bar.tabAt(0));compare(spy.count,1);compare(spy.signalArguments[0][0],"a")
        }
        function test_badgePaintOffset_data(){return [{tag:"ltr",rtl:false,x:10},{tag:"rtl",rtl:true,x:-10}]}
        function test_badgePaintOffset(data) {
            const bar=create({testRtl:data.rtl}),badge=bar.tabAt(1).badgeItem
            const layout=badge.parent.mapToItem(root,badge.x,badge.y),paint=badge.mapToItem(root,0,0)
            fuzzyCompare(paint.x-layout.x,data.x,0.00001);fuzzyCompare(paint.y-layout.y,-7,0.00001)
        }
        function test_unspecifiedWidthKeepsNaturalCells() {
            const bar=create();bar.width=undefined;settle(bar)
            let total=0
            for(let i=0;i<bar.count;i++) {fuzzyCompare(bar.tabAt(i).width,bar.tabAt(i).naturalWidth,0.00001);total+=bar.tabAt(i).width}
            fuzzyCompare(bar.presentationItem.width,total,0.00001);fuzzyCompare(bar.width,total,0.00001)
        }
        function test_keyboard() {
            const bar=create(),spy=createTemporaryObject(spyFactory,bar,{target:bar})
            bar.tabAt(1).forceActiveFocus();verify(bar.tabAt(1).activeFocus);keyClick(Qt.Key_Space);compare(spy.count,1);compare(spy.signalArguments[0][0],"b");compare(bar.selection,"a")
        }
    }
}
