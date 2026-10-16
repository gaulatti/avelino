pragma FunctionSignatureBehavior: Enforced
import QtQuick

InheritedControl {
    id:scope
    default property alias content:host.data
    required property string family
    required property real size
    property string weight:"regular"
    property real textScale:inheritedScale(parent)
    readonly property real bleeckerTextScale:textScale
    readonly property real requestedPixelSize:size*textScale
    readonly property real resolvedPixelSize:resolveSize()
    property bool componentReady:false
    readonly property int partCount:host.count
    readonly property bool containsTextBaseline:host.containsTextBaseline
    function inheritedScale(ancestor:Item):real {
        let current=ancestor
        while(current){
            if(typeof current.bleeckerTextScale==="number")return current.bleeckerTextScale
            current=current.parent
        }
        return BleeckerTheme.textScale
    }
    function resolveSize():real {
        const value=requestedPixelSize
        if(!Number.isFinite(value))throw new Error("BleeckerFont size and text scale must produce a finite size")
        if(value<=0)return 12
        return family==="mono" ? value:Math.round(value)||12
    }
    function resolveFamily():string {
        switch(family){
        case "primary":return BleeckerFonts.primary
        case "secondary":return BleeckerFonts.secondary
        case "mono":return BleeckerFonts.monospace
        default:throw new Error("Unknown Bleecker font family: "+family)
        }
    }
    function resolveWeight():int {
        const values={ultraLight:Font.Thin,thin:Font.ExtraLight,light:Font.Light,regular:Font.Normal,
            medium:Font.Medium,semibold:Font.DemiBold,bold:Font.Bold,heavy:Font.ExtraBold,black:Font.Black}
        if(values[weight]===undefined)throw new Error("Unknown Bleecker font weight: "+weight)
        if(family==="mono" && ["ultraLight","thin"].includes(weight))return Font.Light
        if(family==="mono" && weight==="black")return Font.ExtraBold
        return values[weight]
    }
    function partAt(index:int):Item {return host.itemAt(index)}
    function validate():void {
        resolveFamily();resolveWeight();resolveSize()
        if(!Number.isFinite(size)||!Number.isFinite(textScale))throw new Error("BleeckerFont size and text scale must be finite")
    }
    padding:0;background:null;focusPolicy:Qt.NoFocus;hoverEnabled:false;wheelEnabled:false
    font.family:resolveFamily()
    font.pointSize:BleeckerFonts.pointSizeForPixels(resolvedPixelSize)
    font.weight:resolveWeight()
    implicitWidth:host.implicitWidth;implicitHeight:host.implicitHeight;baselineOffset:host.baselineOffset
    BleeckerLayout.flattenChildren:true
    BleeckerLayout.minimumWidth:host.minimumWidth
    BleeckerLayout.idealWidth:host.naturalWidth
    BleeckerLayout.firstBaseline:containsTextBaseline ? baselineOffset:NaN
    Accessible.ignored:true
    Component.onCompleted:{componentReady=true;validate();host.layout()}
    onFamilyChanged:if(componentReady)validate()
    onWeightChanged:if(componentReady)validate()
    onSizeChanged:if(componentReady)validate()
    onTextScaleChanged:if(componentReady)validate()
    onParentChanged:if(componentReady)host.layout()
    contentItem:ProposalOverlay {
        id:host
        maximumWidth:scope.BleeckerLayout.proposedWidth
        BleeckerLayout.flattenChildren:true
    }
}
