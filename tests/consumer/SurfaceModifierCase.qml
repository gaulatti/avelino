pragma FunctionSignatureBehavior: Enforced
import QtQuick
import QtQuick.Templates as T
import Avelino

Item {
    id:root
    required property var definition
    property bool firstBaselineParent:false
    property real firstTextGuide:NaN
    property bool mounted:true
    property int appearances:0
    property int disappearances:0
    property int callerInstances:0
    property int actions:0
    property int counter:0
    readonly property bool mirrored:LayoutMirroring.enabled
    readonly property real observedTextScale:BleeckerTheme.textScale
    readonly property bool flatBaseline:firstBaselineParent &&definition.parentLayout==="zstack" &&definition.offer===null
    readonly property Item activeGroup:firstBaselineParent ? baselineLoader.item:definition.parentLayout==="hstack" ? horizontal:definition.parentLayout==="vstack" ? vertical:null
    readonly property Item control:firstBaselineParent ? flatBaseline ? baselineLoader.item:activeGroup ? activeGroup.styledControl:null:zLoader.active ? zLoader.item:activeGroup ? activeGroup.styledControl:null
    readonly property Item parentLayout:definition.parentLayout!=="zstack" ? activeGroup:null
    readonly property Item leadingItem:parentLayout ? parentLayout.leading:null
    readonly property Item trailingItem:parentLayout ? parentLayout.trailing:null
    readonly property real parentSpacing:11
    width:definition.width;height:definition.height
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    function styleComponent():Component {
        const components={clear:clearScope,rectangle:rectangleScope,fractional:fractionalScope,opaque:opaqueScope,
            overflow:overflowScope,hidden:hiddenScope,empty:emptyScope,zero:zeroScope,wide:wideScope,
            text:textScope,guide:guideScope,"own-font":fixedScope,"system-font":fixedScope,red:redScope,button:buttonScope,
            multi:multiScope,hstack:rowScope,vstack:columnScope}
        const result=components[definition.content]
        if(!result)throw new Error("Unknown surface caller: "+definition.content)
        return result
    }
    function named(item:Item,name:string):Item {
        if(!item)return null
        if(item.objectName===name)return item
        for(const child of item.children){const found=named(child,name);if(found)return found}
        return null
    }
    function rectangle(item:Item):var {
        const p=item.mapToItem(root,0,0)
        return {x:p.x,y:p.y,width:item.width,height:item.height}
    }
    function observedItems():var {
        const result={},emitted=[]
        if(control)for(let i=0;i<control.partCount;++i)emitted.push(control.partAt(i))
        if(emitted.length){result.styled=emitted;result.root=definition.parentLayout==="zstack" &&definition.offer!==null ? [firstBaselineParent ? baselineLoader.item:centered]:emitted}
        for(const key of ["caller","first","second"]){const item=named(control,"surfaceModifier-"+key);if(item)result[key]=[item]}
        if(parentLayout)result.parent=[parentLayout]
        if(leadingItem)result.leading=[leadingItem]
        if(trailingItem)result.trailing=[trailingItem]
        if(firstBaselineParent){result.baselineParent=[baselineRow];result.reference=[reference]}
        for(const key of Object.keys(result))result[key].sort((a,b)=>{const x=rectangle(a),y=rectangle(b);return x.x-y.x||x.y-y.y||x.width-y.width||x.height-y.height})
        return result
    }
    function frames():var {
        const items=observedItems(),result={}
        for(const key of Object.keys(items))result[key]=items[key].map(rectangle)
        return result
    }
    function baselineValue(item:Item):real {
        const explicit=item.BleeckerLayout.firstBaseline
        if(Number.isFinite(explicit))return explicit
        if(typeof item.containsTextBaseline==="boolean")return item.containsTextBaseline ? item.baselineOffset:item.height
        return item.baselineOffset!==0 ? item.baselineOffset:item.height
    }
    function baselines():var {
        // Geometry-only probes remain geometry-only in the centered corpus and
        // in the nested children of explicit parents in the native supplement.
        if(!firstBaselineParent)return {}
        const items=observedItems(),result={}
        const keys=definition.parentLayout==="zstack" ? ["reference","root","styled","caller","first","second"]:["reference","parent"]
        for(const key of keys)if(items[key])result[key]=items[key].map(baselineValue)
        return result
    }
    component Shell:BleeckerSurfaceModifier {
        radius:root.definition.radius===null ? BleeckerTokens.radii.card:root.definition.radius
        property bool counted:false
        function observe():void {if(partCount>0 &&!counted){counted=true;root.appearances++;root.callerInstances++}}
        Component.onCompleted:observe()
        onPartCountChanged:Qt.callLater(observe)
        Component.onDestruction:if(root &&counted)root.disappearances++
    }
    component Leading:Rectangle {implicitWidth:40;implicitHeight:12;color:"#a65d57"}
    component Trailing:Rectangle {implicitWidth:30;implicitHeight:20;color:"#c1814d"}
    component HorizontalParent:ProposalRow {
        id:hGroup
        required property bool activeLayout
        readonly property Item styledControl:contents.item
        readonly property Item leading:parentLeading
        readonly property Item trailing:parentTrailing
        spacing:root.parentSpacing;mirrored:context.mirrored
        Leading {id:parentLeading}
        Loader {id:contents;active:root.mounted &&hGroup.activeLayout;BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
        Trailing {id:parentTrailing}
    }
    component VerticalParent:ProposalColumn {
        id:vGroup
        required property bool activeLayout
        readonly property Item styledControl:contents.item
        readonly property Item leading:parentLeading
        readonly property Item trailing:parentTrailing
        spacing:root.parentSpacing;padding:0
        Leading {id:parentLeading}
        Loader {id:contents;active:root.mounted &&vGroup.activeLayout;BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
        Trailing {id:parentTrailing}
    }
    Component {id:baselineHorizontal;HorizontalParent {activeLayout:root.firstBaselineParent &&root.definition.parentLayout==="hstack"}}
    Component {id:baselineVertical;VerticalParent {activeLayout:root.firstBaselineParent &&root.definition.parentLayout==="vstack"}}
    Component {
        id:baselineOffer
        ProposalOverlay {
            readonly property Item styledControl:contents.item
            BleeckerLayout.idealWidth:root.definition.offer;BleeckerLayout.minimumWidth:root.definition.offer
            maximumWidth:root.definition.offer
            width:root.definition.offer;height:implicitHeight
            Loader {id:contents;active:root.mounted;BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
        }
    }
    InheritedControl {
        id:context;anchors.fill:parent;padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus;Accessible.ignored:true
        font.family:root.definition.parentFont ? Qt.application.font.family:BleeckerFonts.primary
        font.pointSize:BleeckerFonts.pointSizeForPixels(root.definition.parentFont ? 32:13)
        font.weight:root.definition.parentFont ? Font.Bold:Font.Normal
        readonly property color callerForeground:root.definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.palette.textPrimary
        palette.windowText:callerForeground
        palette.disabled.windowText:callerForeground
        Item {
            id:centered;visible:!root.firstBaselineParent &&root.definition.parentLayout==="zstack"
            width:root.definition.offer===null ? root.width:root.definition.offer
            height:root.definition.offer===null ? root.height:overlay.implicitHeight
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            ProposalOverlay {
                id:overlay;anchors.fill:parent;maximumWidth:root.definition.offer===null ? root.width:root.definition.offer
                Loader {id:zLoader;active:root.mounted &&!root.firstBaselineParent &&root.definition.parentLayout==="zstack";BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
            }
        }
        HorizontalParent {
            id:horizontal;activeLayout:!root.firstBaselineParent &&root.definition.parentLayout==="hstack";visible:activeLayout
            anchors.centerIn:parent;anchors.alignWhenCentered:false
        }
        VerticalParent {
            id:vertical;activeLayout:!root.firstBaselineParent &&root.definition.parentLayout==="vstack";visible:activeLayout
            anchors.centerIn:parent;anchors.alignWhenCentered:false
        }
        ProposalRow {
            id:baselineRow;visible:root.firstBaselineParent
            spacing:root.parentSpacing;verticalAlignment:Qt.AlignBaseline;mirrored:context.mirrored
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            Loader {
                id:baselineLoader;active:root.mounted &&root.firstBaselineParent;BleeckerLayout.flattenChildren:true
                sourceComponent:root.flatBaseline ? root.styleComponent():root.definition.parentLayout==="hstack" ? baselineHorizontal:root.definition.parentLayout==="vstack" ? baselineVertical:baselineOffer
            }
            Rectangle {id:reference;implicitWidth:3;implicitHeight:30;color:"#2c5784"}
        }
    }
    Component {id:clearScope;Shell {Item {objectName:"surfaceModifier-caller";width:96;height:64}}}
    Component {id:rectangleScope;Shell {Rectangle {objectName:"surfaceModifier-caller";width:72;height:44;color:BleeckerTheme.palette.sea}}}
    Component {id:fractionalScope;Shell {Rectangle {objectName:"surfaceModifier-caller";width:72.5;height:44.25;color:BleeckerTheme.palette.sea}}}
    Component {id:hiddenScope;Shell {Rectangle {objectName:"surfaceModifier-caller";width:96;height:64;color:BleeckerTheme.palette.sea;visible:false}}}
    Component {id:zeroScope;Shell {Item {objectName:"surfaceModifier-caller"}}}
    Component {id:emptyScope;Shell {}}
    Component {id:wideScope;Shell {Rectangle {objectName:"surfaceModifier-caller";width:800;height:80;color:BleeckerTheme.palette.sea}}}
    Component {
        id:opaqueScope
        Shell {Item {
            objectName:"surfaceModifier-caller";width:96;height:64
            Rectangle {anchors.fill:parent;color:BleeckerTheme.palette.sea}
            Rectangle {anchors.left:parent.left;anchors.top:parent.top;width:32;height:32;color:BleeckerTheme.palette.terracotta}
            Rectangle {anchors.right:parent.right;anchors.bottom:parent.bottom;width:32;height:32;color:BleeckerTheme.palette.desert}
        }}
    }
    Component {
        id:overflowScope
        Shell {Item {
            objectName:"surfaceModifier-caller";width:80;height:44
            Rectangle {anchors.centerIn:parent;anchors.alignWhenCentered:false;width:160;height:100;color:BleeckerTheme.palette.sea}
        }}
    }
    Component {id:textScope;Shell {BleeckerText {objectName:"surfaceModifier-caller";text:root.definition.text}}}
    Component {id:guideScope;Shell {BleeckerText {objectName:"surfaceModifier-caller";text:root.definition.text;BleeckerLayout.firstBaseline:root.firstTextGuide}}}
    Component {
        id:fixedScope
        Shell {BleeckerText {
            objectName:"surfaceModifier-caller";text:root.definition.text
            font.family:root.definition.content==="own-font" ? BleeckerFonts.secondary:Qt.application.font.family
            font.pointSize:BleeckerFonts.pointSizeForPixels(root.definition.content==="own-font" ? 19:32)
            font.weight:Font.Bold
        }}
    }
    Component {id:redScope;Shell {BleeckerText {objectName:"surfaceModifier-caller";text:root.definition.text;color:BleeckerTheme.nativeRed}}}
    Component {
        id:buttonScope
        Shell {T.Button {
            id:button;objectName:"surfaceModifier-caller";text:"Publish "+root.counter;focusPolicy:Qt.StrongFocus
            implicitWidth:label.implicitWidth+24;implicitHeight:24;padding:0
            // Owned diagnostic bezel. Its macOS presentation is unresolved and
            // remains in the strict comparison rather than being substituted
            // with the differently styled BleeckerButton.
            background:Rectangle {color:BleeckerTheme.dark ? "#585858":"#d1d1d1";radius:6;border.width:1;border.color:BleeckerTheme.dark ? "#686868":"#bdbdbd"}
            contentItem:Item {baselineOffset:label.y+label.baselineOffset;BleeckerText {id:label;anchors.centerIn:parent;anchors.alignWhenCentered:false;text:button.text}}
            Accessible.name:text
            onClicked:{root.counter++;root.actions++}
        }}
    }
    Component {id:multiScope;Shell {
        BleeckerText {objectName:"surfaceModifier-first";text:"First child"}
        Rectangle {objectName:"surfaceModifier-second";width:72;height:44;color:BleeckerTheme.palette.sea}
    }}
    Component {id:rowScope;Shell {ProposalRow {
        objectName:"surfaceModifier-caller";spacing:5
        BleeckerText {objectName:"surfaceModifier-first";text:"First child"}
        Rectangle {objectName:"surfaceModifier-second";width:72;height:44;color:BleeckerTheme.palette.sea}
    }}}
    Component {id:columnScope;Shell {ProposalColumn {
        objectName:"surfaceModifier-caller";spacing:5;padding:0
        BleeckerText {objectName:"surfaceModifier-first";text:"First child"}
        Rectangle {objectName:"surfaceModifier-second";width:72;height:44;color:BleeckerTheme.palette.sea}
    }}}
}
