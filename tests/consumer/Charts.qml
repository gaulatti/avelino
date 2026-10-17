import QtQuick
import Avelino

Window {
    id:window
    readonly property bool gallery:typeof consumerDark==="undefined"
    readonly property real fixtureTextScale:BleeckerTheme.textScale
    width:gallery ? 1120:640;height:gallery ? 820:400
    visible:true;title:"Avelino charts";color:BleeckerTheme.palette.background
    property var model:({id:"default",kind:"line",points:[10,18,14,26,23,31,39].map((y,i)=>({id:String(i),series:"Value",label:String(i+1),x:i,y:y})),values:[10,18,14,26,23,31,39],area:false,innerRadius:0,width:460,height:260,rtl:false,disabled:false,parentFont:false,parentRed:false})
    readonly property Item primaryFixture:fixture
    function nativeNumber(value) {
        return value==="__native_nan__" ? NaN:value==="__native_positive_infinity__" ? Infinity:value==="__native_negative_infinity__" ? -Infinity:value
    }
    function configure(value):void {
        model=Object.assign({},value,{points:value.points.map(p=>Object.assign({},p,{x:nativeNumber(p.x),y:nativeNumber(p.y)})),values:value.values.map(v=>nativeNumber(v)),innerRadius:nativeNumber(value.innerRadius)})
    }
    function update(value):void {model=Object.assign({},model,value)}
    function environment(dark,scale):void {BleeckerTheme.dark=dark;BleeckerTheme.textScale=scale}
    Component.onCompleted:{BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=gallery ? captureDark:consumerDark;BleeckerTheme.textScale=gallery ? captureTextScale:consumerTextScale}
    ProposalRow {
        x:24;y:24;spacing:8;visible:window.gallery
        Repeater {model:["line","bar","pie","scatter","sparkline"]
            BleeckerButton {required property string modelData;objectName:"chartOperator-kind-"+modelData;text:modelData;size:"xs";onClicked:window.update({kind:modelData,width:modelData==="sparkline" ? 220:460,height:modelData==="sparkline" ? 62:260})}
        }
        BleeckerButton {objectName:"chartOperator-area";text:"Area";size:"xs";enabled:window.model.kind==="line";onClicked:window.update({area:!window.model.area})}
        BleeckerButton {objectName:"chartOperator-radius";text:"Donut";size:"xs";enabled:window.model.kind==="pie";onClicked:window.update({innerRadius:window.model.innerRadius===0 ? 0.58:0})}
    }
    ProposalRow {
        x:24;y:80;spacing:8;visible:window.gallery
        BleeckerButton {objectName:"chartOperator-data";text:"Data";size:"xs";onClicked:{const values=window.model.values[0]===10 ? [-9,7,0,17,-2]:[10,18,14,26,23,31,39];window.update({values:values,points:values.map((y,i)=>({id:String(i),series:"Series "+(i%3+1),label:String(i+1),x:i,y:y}))})}}
        BleeckerButton {objectName:"chartOperator-empty";text:"Empty";size:"xs";onClicked:window.update({points:[],values:[]})}
        BleeckerButton {objectName:"chartOperator-size";text:"Size";size:"xs";onClicked:window.update({width:window.model.width===460 ? 160:460,height:window.model.height===260 ? 100:260})}
        BleeckerButton {objectName:"chartOperator-rtl";text:"RTL";size:"xs";onClicked:window.update({rtl:!window.model.rtl})}
        BleeckerButton {objectName:"chartOperator-theme";text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
        BleeckerButton {objectName:"chartOperator-scale";text:"Scale";size:"xs";onClicked:BleeckerTheme.textScale=BleeckerTheme.textScale===1 ? 1.5:1}
        BleeckerButton {objectName:"chartOperator-disabled";text:"Disabled";size:"xs";onClicked:window.update({disabled:!window.model.disabled})}
    }
    ChartsCase {id:fixture;x:window.gallery ? 24:0;y:window.gallery ? 200:0;definition:window.model}
    Text {
        x:720;y:230;width:340;visible:window.gallery
        text:"Line/area, categorical stacked bars, signed sectors, scatter and sparkline share an owned renderer. Data, layout, theme and direction changes retain the chart object.\n\nNative font, geometry, raster, input and reader parity remain pending. Native bar NaN input has unresolved initialization differences."
        wrapMode:Text.WordWrap;font.family:BleeckerFonts.secondary;font.pixelSize:16;color:BleeckerTheme.palette.textSecondary
    }
}
