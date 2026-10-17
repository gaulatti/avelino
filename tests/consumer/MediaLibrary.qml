import QtQuick
import Avelino

Window {
    id:window
    readonly property bool gallery:typeof consumerDark==="undefined"
    width:gallery ? 1120:640;height:gallery ? 820:400
    visible:true;title:"Avelino media library";color:BleeckerTheme.palette.background
    function initialItems() {return Array.from({length:7},(_,i)=>({id:String(i),title:"Tile "+(i+1),width:40+i*10,height:20+(i%3)*20,color:i%4}))}
    property var model:({id:"default",items:initialItems(),minimumTileWidth:160,width:460,height:null,slot:"fill",rtl:false,disabled:false,parentFont:false,parentRed:false,scroll:false})
    readonly property real fixtureTextScale:BleeckerTheme.textScale
    readonly property Item primaryFixture:fixture
    function configure(value):void {model=Object.assign({},value)}
    function update(value):void {model=Object.assign({},model,value)}
    function environment(dark,scale):void {BleeckerTheme.dark=dark;BleeckerTheme.textScale=scale}
    Component.onCompleted:{BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=gallery ? captureDark:consumerDark;BleeckerTheme.textScale=gallery ? captureTextScale:consumerTextScale}
    ProposalRow {
        x:24;y:24;spacing:8;visible:window.gallery
        Repeater {model:["fill","fixed","text","button"]
            BleeckerButton {required property string modelData;objectName:"mediaOperator-slot-"+modelData;text:modelData;size:"xs";onClicked:window.update({slot:modelData})}
        }
        BleeckerButton {objectName:"mediaOperator-data";text:"Edit";size:"xs";onClicked:window.update({items:window.model.items.map((item,i)=>Object.assign({},item,{title:"Updated "+item.title,height:item.height===20 ? 40:20}))})}
        BleeckerButton {objectName:"mediaOperator-reorder";text:"Reverse";size:"xs";onClicked:window.update({items:window.model.items.slice().reverse()})}
        BleeckerButton {objectName:"mediaOperator-empty";text:"Empty / restore";size:"xs";onClicked:window.update({items:window.model.items.length ? []:window.initialItems()})}
    }
    ProposalRow {
        x:24;y:80;spacing:8;visible:window.gallery
        BleeckerButton {objectName:"mediaOperator-size";text:"Width";size:"xs";onClicked:window.update({width:window.model.width===460 ? 160:window.model.width===160 ? 336:460})}
        BleeckerButton {objectName:"mediaOperator-minimum";text:"Tile minimum";size:"xs";onClicked:window.update({minimumTileWidth:window.model.minimumTileWidth===160 ? 80:160})}
        BleeckerButton {objectName:"mediaOperator-scroll";text:"Viewport";size:"xs";onClicked:window.update({scroll:!window.model.scroll,height:window.model.scroll ? null:100})}
        BleeckerButton {objectName:"mediaOperator-rtl";text:"RTL";size:"xs";onClicked:window.update({rtl:!window.model.rtl})}
        BleeckerButton {objectName:"mediaOperator-theme";text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
        BleeckerButton {objectName:"mediaOperator-scale";text:"Scale";size:"xs";onClicked:BleeckerTheme.textScale=BleeckerTheme.textScale===1 ? 1.5:1}
        BleeckerButton {objectName:"mediaOperator-disabled";text:"Disabled";size:"xs";onClicked:window.update({disabled:!window.model.disabled})}
    }
    MediaLibraryCase {id:fixture;x:window.gallery ? 24:0;y:window.gallery ? 200:0;definition:window.model}
    Text {
        x:720;y:230;width:340;visible:window.gallery;wrapMode:Text.WordWrap
        text:"Caller tiles keep their state when the same identifiers are edited, reordered or moved outside the viewport. Empty data removes them.\n\nThe grid adds no selection or scrolling controls. The viewport here belongs to the caller. Native sizing, lazy timing, raster, physical input and reader acceptance remain pending."
        font.family:BleeckerFonts.secondary;font.pixelSize:16;color:BleeckerTheme.palette.textSecondary
    }
}
