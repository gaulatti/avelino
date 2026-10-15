import QtQuick
import QtTest
import Avelino

Item {
    id: root
    width: 760; height: 300
    property var chosen: "a"
    property int activations: 0
    Component {
        id: factory
        BleeckerSegmentedControl {
            selection: root.chosen
            options: [{value:"a",label:"Alpha"},{value:"b",label:"Disabled",disabled:true},{value:"c",label:"Gamma"}]
        }
    }
    Component {
        id: boundFactory
        BleeckerTabs {
            selection: root.chosen
            options: [{value:"a",label:"Alpha"},{value:"b",label:"Disabled",disabled:true},{value:"c",label:"Gamma"}]
            onActivated: value => { root.chosen=value;root.activations++ }
        }
    }
    TestCase {
        name: "BoundSelectionContracts"
        when: windowShown
        function init() { root.chosen="a";root.activations=0;BleeckerTheme.dark=false;BleeckerTheme.textScale=1;failOnWarning(/Binding loop/) }
        function test_typed_values_data() {
            return [{tag:"string",first:"a",second:"c",external:"external"},{tag:"number",first:0,second:2,external:9},{tag:"boolean",first:false,second:true,external:false},{tag:"empty-string",first:"",second:"c",external:"outside"}]
        }
        function test_typed_values(d) {
            root.chosen=d.first
            const item=createTemporaryObject(boundFactory,root,{options:[{value:d.first,label:"First"},{value:d.second,label:"Last"}]})
            const first=findChild(item,"bleeckerSegment0"),last=findChild(item,"bleeckerSegment1")
            mouseClick(last);compare(root.chosen,d.second);compare(item.selection,d.second);compare(root.activations,1)
            root.chosen=d.external;compare(item.selection,d.external)
            first.forceActiveFocus(Qt.TabFocusReason);keyClick(Qt.Key_Space)
            compare(root.chosen,d.first);compare(root.activations,2)
            root.chosen=d.second;verify(last.selected);verify(!first.selected)
        }
        function test_disabled_reselection_options_and_keyboard() {
            const item=createTemporaryObject(boundFactory,root)
            const first=findChild(item,"bleeckerSegment0"),disabled=findChild(item,"bleeckerSegment1"),last=findChild(item,"bleeckerSegment2")
            mouseClick(disabled);compare(root.chosen,"a");compare(root.activations,0)
            mouseClick(first);compare(root.activations,1);compare(root.chosen,"a")
            first.forceActiveFocus();keyClick(Qt.Key_Tab);verify(last.activeFocus);keyClick(Qt.Key_Space)
            compare(root.chosen,"c");compare(root.activations,2)
            item.enabled=false;mouseClick(first);compare(root.chosen,"c");compare(root.activations,2)
            root.chosen="a";compare(item.selection,"a")
            item.enabled=true;item.options=[{value:"c",label:"Gamma"},{value:"a",label:"Alpha"}]
            verify(findChild(item,"bleeckerSegment1").selected)
            item.options=[];compare(item.selection,"a");tryCompare(item,"width",8);tryCompare(item,"height",8)
        }
        function test_wrapper_matches_underlying_data() {
            const rows=[]
            for (const dark of [false,true]) for (const scale of [1,1.5]) rows.push({tag:dark+"-"+scale,dark,scale})
            return rows
        }
        function test_wrapper_matches_underlying(d) {
            BleeckerTheme.dark=d.dark;BleeckerTheme.textScale=d.scale
            const segments=createTemporaryObject(factory,root)
            const tabs=createTemporaryObject(boundFactory,root,{y:80})
            compare(tabs.width,segments.width);compare(tabs.height,segments.height)
            compare(findChild(tabs,"bleeckerSegment0").font,findChild(segments,"bleeckerSegment0").font)
        }
        function test_constrained_disabled_and_rtl_data() {
            return [{tag:"standard",scale:1},{tag:"scaled",scale:1.5}]
        }
        function test_constrained_disabled_and_rtl(d) {
            BleeckerTheme.textScale=d.scale
            const item=createTemporaryObject(boundFactory,root,{width:140,options:[{value:"a",label:"Morning edition"},{value:"b",label:"Evening edition",disabled:true},{value:"c",label:"Weekend edition"}]})
            const first=findChild(item,"bleeckerSegment0"),middle=findChild(item,"bleeckerSegment1"),last=findChild(item,"bleeckerSegment2")
            tryVerify(() => item.height>40)
            verify(first.width+middle.width+last.width+4<=132.001)
            verify(first.height>32)
            compare(middle.contentItem.opacity,0.5);compare(middle.opacity,1)
            compare(first.Accessible.name,"Morning edition");compare(first.Accessible.description,"Selected")
            root.chosen="b";compare(middle.Accessible.description,"Selected")
            compare(middle.background.color.toString(),BleeckerTheme.palette.card.toString())
            item.LayoutMirroring.enabled=true;item.LayoutMirroring.childrenInherit=true
            tryVerify(() => first.x>last.x)
            item.width=500
            tryVerify(() => item.height<100)
        }
        function test_external_update_after_pointer() {
            const item=createTemporaryObject(factory,root)
            mouseClick(findChild(item,"bleeckerSegment2"))
            compare(item.selection,"c")
            root.chosen="missing"
            compare(item.selection,"missing")
            verify(!findChild(item,"bleeckerSegment0").selected)
        }
    }
}
