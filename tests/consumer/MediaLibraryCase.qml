import QtQuick
import Avelino

Item {
    id:root
    required property var definition
    property bool mounted:true
    property int appearances:0
    property int disappearances:0
    property int callerInstances:0
    property var firstKeys:Object.create(null)
    property var tileInstances:Object.create(null)
    property var tileAppearances:Object.create(null)
    property var tileDisappearances:Object.create(null)
    property var activeTileStates:Object.create(null)
    property var actions:[]
    readonly property Item control:body.item ? body.item.control:null
    width:640;height:400;clip:true
    function nativeNumber(value) {return value==="__native_nan__" ? NaN:value==="__native_positive_infinity__" ? Infinity:value==="__native_negative_infinity__" ? -Infinity:value}
    function keyFor(id) {
        const canonical=BleeckerSelectionTools.canonicalString(String(id))
        if(firstKeys[canonical]===undefined)firstKeys[canonical]=String(id)
        return firstKeys[canonical]
    }
    function newInstance(key) {const next=(tileInstances[key]||0)+1;tileInstances[key]=next;return next}
    function appeared(key,ordinal) {tileAppearances[key]=(tileAppearances[key]||0)+1;activeTileStates[key]=[ordinal]}
    function disappeared(key,ordinal,currentId) {
        // Swift dictionaries retain the spelling first inserted into each map.
        // A first disappearance can arrive after an NFC-to-NFD data update.
        const spelling=Object.keys(tileDisappearances).find(value=>BleeckerSelectionTools.stringsEqual(value,currentId))
        const eventKey=spelling===undefined ? String(currentId):spelling
        tileDisappearances[eventKey]=(tileDisappearances[eventKey]||0)+1;activeTileStates[key]=[]
    }
    function recordAction(id) {actions=actions.concat(id)}
    function resetCounters() {appearances=0;disappearances=0;callerInstances=0;firstKeys=Object.create(null);tileInstances=Object.create(null);tileAppearances=Object.create(null);tileDisappearances=Object.create(null);activeTileStates=Object.create(null);actions=[]}
    function rect(item) {
        const a=item.mapToItem(root,0,0),b=item.mapToItem(root,item.width,item.height)
        return {x:a.x,y:a.y,width:b.x-a.x,height:b.y-a.y}
    }
    function frame() {
        if(!control)return {}
        const tiles=Object.create(null)
        for(let i=0;i<control.itemCount;++i){const item=control.itemAt(i);if(item &&item.tileActive)tiles[item.lifecycleKey]=rect(item)}
        return {grid:rect(control),caller:rect(body.item.caller),tiles:tiles}
    }
    function state() {return {appearances:appearances,disappearances:disappearances,wrapperInstances:callerInstances,tileInstances:tileInstances,tileAppearances:tileAppearances,tileDisappearances:tileDisappearances,activeTileStates:activeTileStates,actions:actions}}
    function measurements() {return control ? control.layoutSnapshot():{}}
    function scrollTo(id) {
        if(!body.item ||!definition.scroll)return
        const index=definition.items.findIndex(value=>BleeckerSelectionTools.stringsEqual(value.id,id))
        if(index<0)throw new Error("Unknown MediaLibrary scroll target")
        const grid=control,flick=body.item.flick
        if(index===0)flick.contentY=0
        else if(index===grid.itemCount-1)flick.contentY=Math.max(0,grid.contentHeight-flick.height)
        else flick.contentY=Math.max(0,Math.floor(index/Math.max(1,grid.columns))*(grid.contentHeight/Math.max(1,Math.ceil(grid.itemCount/Math.max(1,grid.columns))))-flick.height/2)
    }
    InheritedControl {
        anchors.fill:parent;padding:0;background:null;contentItem:null;Accessible.ignored:true
        font.family:root.definition.parentFont ? Qt.application.font.family:BleeckerFonts.primary
        font.pointSize:BleeckerFonts.pointSizeForPixels(root.definition.parentFont ? 28:13)
        font.weight:root.definition.parentFont ? Font.Bold:Font.Normal
        palette.windowText:root.definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.palette.textPrimary
        Loader {
            id:body;anchors.fill:parent;active:root.mounted
            onLoaded:{root.appearances++;root.callerInstances++}
            onActiveChanged:if(!active &&root.callerInstances>0)root.disappearances++
            sourceComponent:Component {
                Item {
                    id:scene
                    readonly property alias control:grid
                    readonly property alias caller:caller
                    readonly property alias flick:flick
                    readonly property real offeredWidth:root.nativeNumber(root.definition.width)
                    readonly property real offeredHeight:root.definition.height===undefined ||root.definition.height===null ? NaN:root.nativeNumber(root.definition.height)
                    Item {
                        id:caller
                        x:(root.width-width)/2;y:(root.height-height)/2
                        width:Number.isNaN(scene.offeredWidth)||scene.offeredWidth===Infinity ? root.width:Math.max(0,scene.offeredWidth)
                        height:root.definition.height===undefined ||root.definition.height===null ||Number.isNaN(scene.offeredHeight)||scene.offeredHeight===Infinity ? grid.contentHeight:Math.max(0,scene.offeredHeight)
                        Flickable {id:flick;anchors.fill:parent;clip:true;visible:root.definition.scroll;contentWidth:width;contentHeight:grid.contentHeight;boundsBehavior:Flickable.StopAtBounds}
                        BleeckerMediaLibrary {
                            id:grid
                            parent:root.definition.scroll ? flick.contentItem:caller
                            x:0;y:root.definition.scroll ? 0:(caller.height-height)/2;width:caller.width
                            items:root.definition.items;minimumTileWidth:root.nativeNumber(root.definition.minimumTileWidth)
                            enabled:!root.definition.disabled
                            LayoutMirroring.enabled:root.definition.rtl;LayoutMirroring.childrenInherit:true
                            tile:Component {MediaLibraryTile {fixture:root}}
                        }
                    }
                }
            }
        }
    }
}
