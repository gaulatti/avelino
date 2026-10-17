import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

TestCase {
    id:testCase;name:"CommandSpotlight";when:windowShown;width:720;height:520;visible:true
    property var requests:[]
    property bool echo:false
    property var removalTarget:null
    property int nextToken:0
    Item {id:scene;anchors.fill:parent}
    Item {id:focusSink;focus:true}
    Component {
        id:buttonRow
        T.Button {
            required property var rowData
            required property int rowIndex
            required property bool rowActive
            property int counter:0
            property int token:0
            implicitWidth:100;implicitHeight:rowData.height
            font:rowFont
            padding:0;background:null
            contentItem:Rectangle {color:"#2c5784"}
            Component.onCompleted:token=++testCase.nextToken
            onClicked:{counter++;if(testCase.removalTarget)testCase.removalTarget.items=[]}
        }
    }
    Component {id:fixedRow;Rectangle {required property var rowData;width:rowData.width;height:rowData.height}}
    Component {id:fillRow;Rectangle {required property var rowData;implicitWidth:10;implicitHeight:rowData.height;BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:10;BleeckerLayout.fillsWidth:true}}
    Component {
        id:spotlight
        BleeckerCommandSpotlight {
            x:(scene.width-width)/2;y:(scene.height-height)/2;query:"Owner";row:buttonRow
            onQueryRequested:value=>{testCase.requests=testCase.requests.concat(value);if(testCase.echo)query=value}
        }
    }
    function entries(count,height=20){return Array.from({length:count},(_,i)=>({id:String(i),height:height,width:48,title:"Command "+i}))}
    function init(){requests=[];echo=false;removalTarget=null;BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
    function cleanup(){BleeckerTheme.textScale=1;BleeckerTheme.dark=false}
    function test_fixed_surface_and_scaled_header() {
        const control=createTemporaryObject(spotlight,scene,{width:30,height:30,items:entries(3)})
        tryCompare(control.rowContainer,"activeCount",3)
        compare(control.implicitWidth,520);compare(control.implicitHeight,380)
        compare(control.presentationItem.width,520);compare(control.presentationItem.height,380)
        compare(control.presentationItem.x,-245);compare(control.presentationItem.y,-175)
        compare(control.searchField.width,496);compare(control.searchField.height,40);compare(control.viewport.height,315)
        BleeckerTheme.textScale=1.5;tryCompare(control.searchField,"height",60);compare(control.viewport.height,295)
    }
    function test_intrinsic_flexible_tall_and_rtl_rows() {
        const control=createTemporaryObject(spotlight,scene,{items:entries(3),row:fixedRow})
        tryCompare(control.rowContainer,"activeCount",3)
        compare(control.rowAt(0).width,48);compare(control.rowCellAt(0).width,72);compare(control.rowCellAt(0).height,38)
        compare(control.rowAt(0).x,12);compare(control.rowAt(0).y,9);compare(control.rowContainer.contentHeight,130)
        control.LayoutMirroring.enabled=true;tryCompare(control.rowCellAt(0),"x",448)
        control.row=fillRow;tryVerify(()=>control.rowAt(0)!==null)
        tryCompare(control.rowAt(0),"width",496);compare(control.rowCellAt(0).width,520)
        control.items=entries(3,84);tryCompare(control.rowContainer,"contentHeight",268)
    }
    function test_query_does_not_filter_or_write_its_owner() {
        const control=createTemporaryObject(spotlight,scene,{items:entries(3)})
        tryCompare(control.rowContainer,"activeCount",3)
        control.query="No matching command";compare(control.count,3);compare(control.searchField.text,"No matching command")
        control.searchField.forceActiveFocus();control.searchField.selectAll();keyClick(Qt.Key_Q)
        compare(requests, ["q"]);compare(control.query,"No matching command");compare(control.searchField.text,"q");compare(control.count,3)
        focusSink.forceActiveFocus();tryCompare(control.searchField,"text","No matching command")
    }
    function test_echo_and_clear_request() {
        echo=true
        const control=createTemporaryObject(spotlight,scene,{items:entries(3)})
        tryCompare(control.rowContainer,"activeCount",3)
        control.searchField.forceActiveFocus();control.searchField.selectAll();keyClick(Qt.Key_Q)
        compare(control.query,"q")
        focusSink.forceActiveFocus();tryCompare(control.searchField,"activeFocus",false)
        const clear=findChild(control.searchField,"bleeckerSearchClear");verify(clear!==null)
        mouseClick(clear,clear.width/2,clear.height/2);compare(control.query,"");compare(requests,["q",""])
        verify(!control.searchField.activeFocus)
    }
    function test_clear_preserves_observing_owner_and_blurred_focus() {
        const control=createTemporaryObject(spotlight,scene,{items:entries(3)})
        tryCompare(control.rowContainer,"activeCount",3)
        focusSink.forceActiveFocus()
        const clear=findChild(control.searchField,"bleeckerSearchClear");verify(clear!==null)
        mouseClick(clear,clear.width/2,clear.height/2)
        compare(requests,[""]);compare(control.query,"Owner");compare(control.searchField.text,"Owner")
        verify(!control.searchField.activeFocus)
    }
    function test_visible_removal_recreates_local_state() {
        const original=entries(3),control=createTemporaryObject(spotlight,scene,{items:original})
        tryCompare(control.rowContainer,"activeCount",3);const item=control.rowAt(0),token=item.token
        mouseClick(item,item.width/2,item.height/2);compare(item.counter,1)
        control.items=[original[2],original[0],original[1]];control.rowContainer.layout();compare(control.rowAt(1),item)
        control.items=[];control.rowContainer.layout();compare(control.rowContainer.contentHeight,12)
        control.items=original;tryVerify(()=>control.rowAt(0)!==null&&control.rowAt(0).rowActive)
        compare(control.rowAt(0).counter,0);verify(control.rowAt(0).token!==token)
    }
    function test_lazy_offscreen_removal_preserves_local_state() {
        const original=entries(80),control=createTemporaryObject(spotlight,scene,{items:original})
        tryCompare(control.rowContainer,"activeCount",8);verify(control.rowContainer.instantiatedCount<80)
        const item=control.rowAt(0),token=item.token
        mouseClick(item,item.width/2,item.height/2);mouseClick(item,item.width/2,item.height/2);compare(item.counter,2)
        control.items=original.slice().reverse();control.rowContainer.layout()
        control.scrollTo(control.rowContainer.contentHeight);tryVerify(()=>item.rowActive)
        control.scrollTo(0);tryVerify(()=>!item.rowActive)
        control.items=[];control.rowContainer.layout();verify(control.rowContainer.cachedCount>0)
        control.items=original;tryVerify(()=>control.rowAt(0)!==null&&control.rowAt(0).rowActive)
        compare(control.rowAt(0),item);compare(item.token,token);compare(item.counter,2)
        mouseClick(item,item.width/2,item.height/2);compare(item.counter,3)
    }
    function test_unicode_and_typed_identifiers() {
        const control=createTemporaryObject(spotlight,scene,{items:[{id:"é",height:20},{id:1,height:20},{id:"1",height:20},{id:true,height:20}]})
        tryCompare(control.rowContainer,"activeCount",4);const item=control.rowAt(0)
        control.items=[{id:"é",height:20},{id:1,height:20},{id:"1",height:20},{id:true,height:20}];control.rowContainer.layout()
        compare(control.rowAt(0),item);compare(item.rowData.id,"é")
    }
    function test_disabled_input_and_removal_during_action() {
        const control=createTemporaryObject(spotlight,scene,{items:entries(3)})
        tryCompare(control.rowContainer,"activeCount",3);const item=control.rowAt(0)
        control.enabled=false;mouseClick(item,item.width/2,item.height/2);compare(item.counter,0)
        compare(control.searchField.enabled,false)
        control.enabled=true;removalTarget=control;mouseClick(item,item.width/2,item.height/2)
        tryCompare(control,"count",0)
    }
}
