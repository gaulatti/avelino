pragma FunctionSignatureBehavior: Enforced
import QtQuick

InheritedControl {
    id:control
    default property list<Item> labels
    property string variant:"primary"
    property string size:"md"
    // A finite outer frame proposal. The decorated body may overflow it.
    property real widthOffer:-1
    // A containing layout's available width, without a fixed outer allocation.
    property real maximumWidth:-1
    signal clicked()
    readonly property int partCount:parts.count
    readonly property bool down:internals.down
    readonly property real labelPadding:size==="xs" ? 10:size==="sm" ? 14:size==="lg" ? 24:18
    readonly property real minimumHeight:variant==="link" ? 0:size==="xs" ? 28:size==="sm" ? 36:size==="lg" ? 48:40
    readonly property real textSize:size==="xs" ? 12:size==="sm" ? 13:size==="lg" ? 15:14
    readonly property var p:BleeckerTheme.palette
    readonly property color foregroundColor:variant==="primary" ? p.primaryForeground:variant==="outline" ? p.sea:variant==="destructive" ? p.destructiveForeground:p.textPrimary
    readonly property color fillColor:colorFor(down)
    function colorFor(pressed:bool):color {
        switch(variant){
        case "primary":return pressed ? p.deepSea:p.primary
        case "secondary":return pressed ? p.muted:p.card
        case "outline":return pressed ? BleeckerTheme.alpha(p.sea,0.08):"transparent"
        case "subtle":return pressed ? BleeckerTheme.alpha(p.sand,0.3):BleeckerTheme.alpha(p.lightSand,0.75)
        case "ghost":case "link":return pressed ? p.muted:"transparent"
        case "destructive":return pressed ? BleeckerTheme.alpha(p.destructive,0.9):p.destructive
        default:throw new Error("Unknown Bleecker button variant: "+variant)
        }
    }
    readonly property color strokeColor:variant==="primary" ? p.primary:variant==="secondary" ? p.border:variant==="outline" ? BleeckerTheme.alpha(p.sea,0.5):variant==="destructive" ? p.destructive:"transparent"
    property bool componentReady:false
    BleeckerLayout.flattenChildren:true
    padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus
    font.family:BleeckerTheme.primaryFont
    font.pointSize:BleeckerFonts.pointSizeForPixels(textSize*BleeckerTheme.textScale)
    font.weight:Font.Medium
    palette.windowText:foregroundColor
    palette.disabled.windowText:foregroundColor
    Accessible.ignored:true
    implicitWidth:internals.width
    implicitHeight:internals.height
    readonly property QtObject internals:QtObject {property bool down:false;property real width:0;property real height:0}
    function refreshGeometry():void {
        if(!parts)return
        let width=0,height=0
        for(let index=0;index<parts.count;++index){
            const part=parts.itemAt(index)
            if(part){width=Math.max(width,part.implicitWidth);height=Math.max(height,part.implicitHeight)}
        }
        internals.width=width;internals.height=height
    }
    function refreshPressed():void {
        if(!parts)return
        let pressed=false
        for(let index=0;index<parts.count;++index){
            const part=parts.itemAt(index)
            if(part && part.inputItem.down)pressed=true
        }
        internals.down=pressed
    }
    function partAt(index:int):Item {return parts.itemAt(index)}
    function validate():void {
        if(!["primary","secondary","outline","subtle","ghost","link","destructive"].includes(variant))
            throw new Error("Unknown Bleecker button variant: "+variant)
        if(!["xs","sm","md","lg"].includes(size))throw new Error("Unknown Bleecker button size: "+size)
        if(!Number.isFinite(widthOffer) || (widthOffer<0 && widthOffer!==-1))
            throw new Error("ButtonStyle width offer must be nonnegative or -1")
        if(!Number.isFinite(maximumWidth) || (maximumWidth<0 && maximumWidth!==-1))
            throw new Error("ButtonStyle maximum width must be nonnegative or -1")
    }
    Component.onCompleted:{componentReady=true;validate()}
    onVariantChanged:if(componentReady)validate()
    onSizeChanged:if(componentReady)validate()
    onWidthOfferChanged:if(componentReady)validate()
    onMaximumWidthChanged:if(componentReady)validate()
    readonly property Repeater parts:Repeater {
        parent:control
        model:control.labels
        delegate:ButtonStylePart {required property Item modelData;labelItem:modelData;style:control}
        onItemAdded:{control.refreshGeometry();control.refreshPressed()}
        onItemRemoved:{control.refreshGeometry();control.refreshPressed()}
    }
}
