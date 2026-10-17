import QtQuick
import Avelino

Item {
    id:root
    required property var definition
    property bool mounted:true
    property int appearances:0
    property int disappearances:0
    property int callerInstances:0
    function nativeNumber(value) {return value==="__native_nan__" ? NaN:value==="__native_positive_infinity__" ? Infinity:value==="__native_negative_infinity__" ? -Infinity:value}
    readonly property var configured:Object.assign({},definition,{points:definition.points.map(p=>Object.assign({},p,{x:nativeNumber(p.x),y:nativeNumber(p.y)})),values:definition.values.map(v=>nativeNumber(v)),innerRadius:nativeNumber(definition.innerRadius)})
    readonly property Item control:loader.item
    width:640;height:400
    function frame() {
        if(!control)return {}
        const size=control.__chart.chartSize
        const position=control.mapToItem(root,(control.width-size.width)/2,(control.height-size.height)/2)
        return {x:position.x,y:position.y,width:size.width,height:size.height}
    }
    function state() {return {appearances:appearances,disappearances:disappearances,wrapperInstances:callerInstances}}
    function measurements() {return control ? control.measurements:{}}
    Component {id:line;BleeckerLineChart {points:root.configured.points;area:root.definition.area}}
    Component {id:bar;BleeckerBarChart {points:root.configured.points}}
    Component {id:pie;BleeckerPieChart {points:root.configured.points;innerRadius:root.configured.innerRadius}}
    Component {id:scatter;BleeckerScatterChart {points:root.configured.points}}
    Component {id:sparkline;BleeckerSparkline {values:root.configured.values}}
    InheritedControl {
        anchors.fill:parent;padding:0;background:null;contentItem:null;Accessible.ignored:true
        font.family:root.definition.parentFont ? Qt.application.font.family:BleeckerFonts.primary
        font.pointSize:BleeckerFonts.pointSizeForPixels(root.definition.parentFont ? 28:13)
        font.weight:root.definition.parentFont ? Font.Bold:Font.Normal
        palette.windowText:root.definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.palette.textPrimary
        Loader {
        id:loader
        active:root.mounted
        x:(root.width-width)/2;y:(root.height-height)/2
        width:root.definition.width;height:root.definition.height
        LayoutMirroring.enabled:root.definition.rtl;LayoutMirroring.childrenInherit:true
        sourceComponent:root.definition.kind==="line" ? line:root.definition.kind==="bar" ? bar:root.definition.kind==="pie" ? pie:root.definition.kind==="scatter" ? scatter:root.definition.kind==="sparkline" ? sparkline:null
        onSourceComponentChanged:if(root.callerInstances>0)root.disappearances++
        onLoaded:{root.appearances++;root.callerInstances++;item.locale=Qt.locale("en_US")}
    }
    }
    Binding {target:loader.item;property:"enabled";when:loader.item!==null;value:!root.definition.disabled}
}
