import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

TestCase {
    id:testCase;name:"MediaLibrary";when:windowShown;width:700;height:450;visible:true
    property int nextToken:0
    property var clicks:[]
    property var removalTarget:null
    property var reflowAppearances:({})
    property var reflowDisappearances:({})
    Item {id:scene;anchors.fill:parent}
    Component {
        id:fill
        Rectangle {
            required property var tileData
            required property int tileIndex
            required property bool tileActive
            property int token:0
            implicitWidth:10;implicitHeight:tileData.height
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:10;BleeckerLayout.fillsWidth:true
            color:"#2c5784"
            Component.onCompleted:token=++testCase.nextToken
        }
    }
    Component {id:fixed;Rectangle {required property var tileData;property int token:0;width:tileData.width;height:tileData.height;Component.onCompleted:token=++testCase.nextToken}}
    Component {
        id:button
        T.Button {
            required property var tileData
            implicitWidth:10;implicitHeight:tileData.height;padding:0;background:null
            contentItem:Rectangle {color:"#2c5784"}
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:10;BleeckerLayout.fillsWidth:true
            onClicked:{testCase.clicks=testCase.clicks.concat(tileData.id);if(testCase.removalTarget)testCase.removalTarget.items=[]}
        }
    }
    Component {id:library;BleeckerMediaLibrary {tile:fill}}
    Component {
        id:centeredTextLibrary
        InheritedControl {
            id:scope;width:640;height:400;clip:true;padding:0;background:null;contentItem:null
            property real offeredWidth:460
            readonly property alias control:grid
            font.family:BleeckerFonts.primary;font.pointSize:BleeckerFonts.pointSizeForPixels(13)
            Item {
                x:(scope.width-width)/2;y:(scope.height-height)/2
                width:scope.offeredWidth;height:grid.contentHeight
                BleeckerMediaLibrary {
                    id:grid;width:parent.width
                    tile:Component {
                        InheritedControl {
                            id:tile
                            required property var tileData
                            required property bool tileActive
                            implicitWidth:label.naturalWidth;implicitHeight:label.implicitHeight
                            padding:0;background:null;contentItem:null
                            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:implicitWidth
                            BleeckerText {id:label;text:tile.tileData.title;font:tile.presentationFont}
                            BleeckerLayout.onProposalChanged:label.BleeckerLayout.propose(BleeckerLayout.proposedWidth)
                            onTileActiveChanged:{
                                const counts=tileActive ? testCase.reflowAppearances:testCase.reflowDisappearances
                                counts[tileData.id]=(counts[tileData.id]||0)+1
                            }
                        }
                    }
                }
            }
        }
    }
    Component {
        id:scrolling
        Flickable {
            width:460;height:100;clip:true;contentWidth:width;contentHeight:library.contentHeight
            readonly property alias control:library
            BleeckerMediaLibrary {id:library;width:parent.width;tile:fill}
        }
    }
    function rows(count) {return Array.from({length:count},(_,i)=>({id:String(i),width:40+i*10,height:20+(i%3)*20}))}
    function init(){clicks=[];removalTarget=null;reflowAppearances={};reflowDisappearances={}}
    function cleanup(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
    function test_text_reflow_preserves_visible_lifecycle_data() {
        return nativeMediaLibraryHistories.filter(row=>row.configuration.id==="text-long" &&row.dpr===testCase.Screen.devicePixelRatio)
            .map(row=>({tag:row.appearance+"-text"+row.textScale,history:row}))
    }
    function test_text_reflow_preserves_visible_lifecycle(data) {
        const history=data.history
        BleeckerTheme.dark=history.appearance==="dark";BleeckerTheme.textScale=history.textScale
        const scope=createTemporaryObject(centeredTextLibrary,scene)
        for(const step of history.steps.slice(0,7)) {
            scope.offeredWidth=step.configuration.width
            scope.control.minimumTileWidth=step.configuration.minimumTileWidth
            scope.control.items=step.configuration.items
            tryCompare(scope.control,"contentHeight",step.frame.grid.height)
            wait(50)
            compare(reflowAppearances,step.lifecycle.tileAppearances,step.step+" appearances "+JSON.stringify(reflowAppearances))
            compare(reflowDisappearances,step.lifecycle.tileDisappearances,step.step+" disappearances "+JSON.stringify(reflowDisappearances))
        }
    }
    function test_adaptive_columns_and_variable_rows() {
        const grid=createTemporaryObject(library,scene,{width:337,items:rows(7)})
        tryCompare(grid,"activeCount",7);compare(grid.columns,2);compare(grid.columnWidth,160.5);compare(grid.contentHeight,228)
        compare(grid.itemAt(0).width,160.5);compare(grid.itemAt(0).mapToItem(grid,0,0),Qt.point(0,10))
        compare(grid.itemAt(1).mapToItem(grid,0,0),Qt.point(176.5,0))
        grid.width=335;tryCompare(grid,"columns",1);compare(grid.contentHeight,356)
        grid.width=512;tryCompare(grid,"columns",3);compare(grid.contentHeight,172)
    }
    function test_fixed_overflow_and_rtl() {
        const grid=createTemporaryObject(library,scene,{width:160,tile:fixed,items:[{id:"a",width:220,height:20}]})
        tryCompare(grid,"activeCount",1);compare(grid.itemAt(0).width,220);compare(grid.itemAt(0).mapToItem(grid,0,0).x,-30)
        grid.mirrored=true;grid.layout();compare(grid.itemAt(0).mapToItem(grid,0,0).x,-30)
    }
    function test_identity_updates_reorder_insert_remove_and_empty_reset() {
        const grid=createTemporaryObject(library,scene,{width:460,items:rows(3)})
        tryCompare(grid,"activeCount",3);const first=grid.itemAt(0),second=grid.itemAt(1),token=first.token
        grid.items=[{id:"2",height:30},{id:"0",height:80},{id:"1",height:40}];grid.layout()
        compare(grid.itemAt(1),first);compare(grid.itemAt(2),second);compare(first.token,token);compare(first.tileData.height,80);compare(first.tileIndex,1)
        grid.items=[{id:"new",height:20},{id:"0",height:80}];grid.layout();compare(grid.itemAt(1),first)
        grid.items=[];grid.layout();compare(grid.itemCount,0);compare(grid.instantiatedCount,0);compare(grid.contentHeight,0)
        grid.items=[{id:"0",height:80}];grid.layout();verify(grid.itemAt(0).token!==token)
    }
    function test_unicode_identity_and_typed_identifiers() {
        const grid=createTemporaryObject(library,scene,{width:460,items:[{id:"é",height:20},{id:1,height:20},{id:"1",height:20},{id:true,height:20}]})
        tryCompare(grid,"activeCount",4);const item=grid.itemAt(0)
        grid.items=[{id:"é",height:40},{id:1,height:20},{id:"1",height:20},{id:true,height:20}];grid.layout()
        compare(grid.itemAt(0),item);compare(item.tileData.id,"é");compare(item.height,40)
        compare(grid.instantiatedCount,4)
    }
    function test_zero_width_retains_state_and_initial_zero_is_lazy() {
        const grid=createTemporaryObject(library,scene,{width:0,items:rows(7)})
        wait(20);compare(grid.instantiatedCount,0);compare(grid.activeCount,0);compare(grid.contentHeight,0)
        grid.width=460;tryCompare(grid,"activeCount",7);const item=grid.itemAt(0)
        grid.width=0;tryCompare(grid,"activeCount",0);compare(grid.itemAt(0),item)
        grid.width=460;tryCompare(grid,"activeCount",7);compare(grid.itemAt(0),item)
    }
    function test_lazy_viewport_scroll_and_state_restoration() {
        const flick=createTemporaryObject(scrolling,scene);flick.control.items=rows(50)
        tryCompare(flick.control,"activeCount",4);compare(flick.control.instantiatedCount,4);compare(flick.control.contentHeight,1634)
        const first=flick.control.itemAt(0)
        flick.contentY=flick.contentHeight-flick.height
        tryVerify(()=>flick.control.itemAt(49)!==null &&flick.control.itemAt(49).tileActive);verify(flick.control.instantiatedCount<50);verify(!first.tileActive)
        flick.contentY=0;tryVerify(()=>first.tileActive);compare(flick.control.itemAt(0),first)
    }
    function test_caller_button_input_and_disabled_inheritance() {
        const grid=createTemporaryObject(library,scene,{width:460,tile:button,items:rows(2)})
        tryCompare(grid,"activeCount",2);const item=grid.itemAt(0)
        mouseClick(item,item.width/2,item.height/2);compare(clicks,["0"])
        grid.enabled=false;mouseClick(item,item.width/2,item.height/2);compare(clicks,["0"])
    }
    function test_action_can_remove_its_own_tile() {
        const grid=createTemporaryObject(library,scene,{width:460,tile:button,items:rows(2)})
        tryCompare(grid,"activeCount",2);removalTarget=grid
        const item=grid.itemAt(0);mouseClick(item,item.width/2,item.height/2)
        compare(clicks,["0"]);compare(grid.itemCount,0);compare(grid.instantiatedCount,0);wait(1)
    }
    function test_initial_identity_projection() {
        const grid=createTemporaryObject(library,scene,{width:460,items:[{key:"a",height:20}],itemIdentity:(value)=>value.key})
        tryCompare(grid,"activeCount",1);compare(grid.itemAt(0).tileData.key,"a")
    }
}
