import QtQuick
import Avelino

Window {
    id:window
    readonly property bool gallery:typeof consumerDark==="undefined" || (typeof consumerHeroGallery!=="undefined" &&consumerHeroGallery)
    width:gallery ? 1120:640;height:gallery ? 820:400
    visible:true;title:"Avelino hero carousel";color:BleeckerTheme.palette.background
    function initialItems() {return Array.from({length:3},(_,i)=>({id:String(i),title:"Slide "+(i+1),width:91,height:80+(i%3)*20,color:i%4}))}
    property var model:({id:"default",items:initialItems(),width:337,height:180,slot:"fill",rtl:false,disabled:false,parentFont:false,parentRed:false,scroll:false})
    readonly property real fixtureTextScale:BleeckerTheme.textScale
    readonly property bool fixtureDark:BleeckerTheme.dark
    readonly property Item primaryFixture:fixture
    function configure(value):void {model=Object.assign({},value)}
    function update(value):void {model=Object.assign({},model,value)}
    function environment(dark,scale):void {BleeckerTheme.dark=dark;BleeckerTheme.textScale=scale}
    Component.onCompleted:{BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=gallery ? captureDark:consumerDark;BleeckerTheme.textScale=gallery ? captureTextScale:consumerTextScale}
    ProposalRow {
        x:24;y:24;spacing:8;visible:window.gallery
        Repeater {model:["fill","fixed","text","button"]
            BleeckerButton {required property string modelData;objectName:"heroOperator-slot-"+modelData;text:modelData;size:"xs";onClicked:window.update({slot:modelData})}
        }
        BleeckerButton {objectName:"heroOperator-data";text:"Edit";size:"xs";onClicked:window.update({items:window.model.items.map((item,i)=>Object.assign({},item,{title:"Updated "+item.title,height:item.height===20 ? 40:20}))})}
        BleeckerButton {objectName:"heroOperator-reorder";text:"Reverse";size:"xs";onClicked:window.update({items:window.model.items.slice().reverse()})}
        BleeckerButton {objectName:"heroOperator-empty";text:"Empty / restore";size:"xs";onClicked:window.update({items:window.model.items.length ? []:window.initialItems()})}
    }
    ProposalRow {
        x:24;y:80;spacing:8;visible:window.gallery
        BleeckerButton {objectName:"heroOperator-size";text:"Width";size:"xs";onClicked:window.update({width:window.model.width===337 ? 160:337})}
        BleeckerButton {objectName:"heroOperator-rtl";text:"RTL";size:"xs";onClicked:window.update({rtl:!window.model.rtl})}
        BleeckerButton {objectName:"heroOperator-theme";text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
        BleeckerButton {objectName:"heroOperator-scale";text:"Scale";size:"xs";onClicked:BleeckerTheme.textScale=BleeckerTheme.textScale===1 ? 1.5:1}
        BleeckerButton {objectName:"heroOperator-disabled";text:"Disabled";size:"xs";onClicked:window.update({disabled:!window.model.disabled})}
    }
    HeroCarouselCase {id:fixture;x:window.gallery ? 24:0;y:window.gallery ? 200:0;definition:window.model}
    Text {
        x:720;y:230;width:340;visible:window.gallery;wrapMode:Text.WordWrap
        text:"Caller slides retain identity across edits, reordering, scrolling and empty/restore histories. Each slide receives viewport width; fixed content remains centered.\n\nThe component adds no navigation buttons or autoplay. Native gesture timing, raster, reader and physical acceptance remain pending."
        font.family:BleeckerFonts.secondary;font.pixelSize:16;color:BleeckerTheme.palette.textSecondary
    }
}
