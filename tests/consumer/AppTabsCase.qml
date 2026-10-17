import QtQuick
import QtQuick.Templates as T
import Avelino

Item {
    id:fixture
    required property var definition
    property var selection:definition.selection
    signal selectionRequested(var requestedValue)
    readonly property Item control:bar
    readonly property Item presentationItem:bar.presentationItem
    property int appearances:0
    Component.onCompleted:appearances++
    function state(){return {appearances:appearances,disappearances:0,wrapperInstances:appearances}}
    function bounds(item,untransformed) {
        const point=untransformed ? item.parent.mapToItem(fixture,item.x,item.y):item.mapToItem(fixture,0,0)
        return {x:point.x,y:point.y,width:item.width,height:item.height}
    }
    function frame(){return frameValues()}
    function frameValues() {
        const result={bar:bounds(bar.presentationItem,false),caller:bounds(caller,false)}
        for(let i=0;i<bar.count;i++) {
            const tab=bar.tabAt(i)
            if(!tab)continue
            result["button-"+i]=bounds(tab,false)
            result["icon-"+i]=bounds(tab.iconItem,false)
            result["label-"+i]=bounds(tab.titleItem,false)
            if(tab.tabBadgeVisible)result["badge-"+i]=bounds(tab.badgeItem,true)
        }
        return result
    }
    width:640;height:400
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    function decode(value) {
        if(definition.valueKind==="boolean")return value==="true"
        if(definition.valueKind==="record") {const pair=value.split("|");return {namespace:pair[0],index:pair[1]}}
        return value
    }
    function selectionState() {
        const values=[]
        for(let i=0;i<bar.count;i++){const tab=bar.tabAt(i);if(tab &&tab.selected)values.push(encode(tab.tabValue))}
        return {selectedValues:values}
    }
    function encode(value) {
        if(definition.valueKind==="boolean")return value ? "true":"false"
        if(definition.valueKind==="record")return value.namespace+"|"+String(value.index)
        return value
    }
    T.Control {
        id:caller;objectName:"appTabCaller"
        x:(fixture.width-width)/2;y:(fixture.height-height)/2
        width:fixture.definition.width;height:fixture.definition.height===undefined ||fixture.definition.height===null ? bar.implicitHeight:fixture.definition.height
        padding:0;background:null
        font.family:fixture.definition.parentFont ? Qt.application.font.family:BleeckerTheme.primaryFont
        font.pointSize:BleeckerFonts.pointSizeForPixels(fixture.definition.parentFont ? 28:13)
        font.weight:fixture.definition.parentFont ? Font.Bold:Font.Normal
        palette.windowText:fixture.definition.parentRed ? "red":BleeckerTheme.palette.textPrimary
        BleeckerAppTabBar {
            id:bar;width:parent.width;height:parent.height
            selection:fixture.decode(fixture.selection)
            tabs:fixture.definition.tabs.map(t=>Object.assign({},t,{value:fixture.decode(t.value)}))
            valueIdentity:fixture.definition.valueKind==="record" ? value=>value.namespace+"|"+value.index:null
            enabled:!fixture.definition.disabled
            icon:Component {AppTabGlyph {}}
            onSelectionRequested:value=>fixture.selectionRequested(fixture.encode(value))
        }
    }
}
