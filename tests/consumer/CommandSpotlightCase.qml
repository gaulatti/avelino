import QtQuick
import QtQuick.Templates as T
import Avelino

Item {
    id:fixture
    required property var definition
    property string query:definition.query
    signal queryRequested(string requestedQuery)
    readonly property Item control:spotlight
    readonly property Item presentationItem:spotlight.presentationItem
    property var counts:({})
    property var instances:({})
    property var appearances:({})
    property var disappearances:({})
    property var active:({})
    width:720;height:520
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    function created(key){instances[key]=(instances[key]||0)+1}
    function counted(key,value){counts[key]=value}
    function activity(key,value){if(value){appearances[key]=(appearances[key]||0)+1;active[key]=true}else{disappearances[key]=(disappearances[key]||0)+1;delete active[key]}}
    function state(){return {rowCounts:counts,rowInstances:instances,rowAppearances:appearances,rowDisappearances:disappearances,appearedKeys:Object.keys(active).sort(),lifecycle:{appearances:1,disappearances:0,wrapperInstances:1}}}
    function bounds(item){const p=item.mapToItem(fixture,0,0);return {x:p.x,y:p.y,width:item.width,height:item.height}}
    function frame() {
        const body=spotlight.presentationItem,search=spotlight.searchField,scroll=spotlight.viewport
        const result={caller:bounds(caller),body:bounds(body),search:bounds(search),scroll:bounds(scroll),stack:bounds(spotlight.rowContainer),
            header:{x:body.x+caller.x,y:body.y+caller.y,width:520,height:search.height+24},
            separator:{x:body.x+caller.x,y:body.y+caller.y+search.height+24,width:520,height:1}}
        for(let i=0;i<spotlight.count;i++) {
            const row=spotlight.rowAt(i)
            if(!row||!row.rowActive)continue
            result["row-"+row.rowData.key]=bounds(spotlight.rowCellAt(i))
            result["content-"+row.rowData.key]=bounds(row)
        }
        return result
    }
    function decode(value) {
        if(definition.valueKind==="boolean")return value==="true"
        if(definition.valueKind==="record"){const pair=value.split("|");return {namespace:pair[0],index:pair[1]}}
        // Preserve the full signed native integer range as canonical wire text.
        return value
    }
    T.Control {
        id:caller
        x:(fixture.width-width)/2;y:(fixture.height-height)/2
        width:fixture.definition.callerWidth===undefined||fixture.definition.callerWidth===null ? 520:fixture.definition.callerWidth
        height:fixture.definition.callerHeight===undefined||fixture.definition.callerHeight===null ? 380:fixture.definition.callerHeight
        padding:0;background:null
        font.family:fixture.definition.parentFont ? Qt.application.font.family:BleeckerTheme.primaryFont
        font.pointSize:BleeckerFonts.pointSizeForPixels(fixture.definition.parentFont ? 28:13)
        font.weight:fixture.definition.parentFont ? Font.Bold:Font.Normal
        palette.windowText:fixture.definition.parentRed ? "red":BleeckerTheme.nativeTextPrimary
        BleeckerCommandSpotlight {
            id:spotlight;width:parent.width;height:parent.height
            query:fixture.query
            items:fixture.definition.entries.map(entry=>Object.assign({},entry,{id:fixture.decode(entry.id)}))
            itemIdentity:fixture.definition.valueKind==="record" ? entry=>entry.id.namespace+"|"+entry.id.index:null
            row:Component {CommandSpotlightRow {observer:fixture}}
            enabled:!fixture.definition.disabled
            onQueryRequested:value=>fixture.queryRequested(value)
        }
    }
}
