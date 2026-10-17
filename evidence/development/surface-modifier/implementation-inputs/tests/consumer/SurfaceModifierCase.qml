pragma FunctionSignatureBehavior: Enforced
import QtQuick
import QtQuick.Templates as T
import Avelino

Item {
    id:root
    required property var definition
    property bool mounted:true
    property int appearances:0
    property int disappearances:0
    property int callerInstances:0
    property int actions:0
    property int counter:0
    readonly property bool mirrored:LayoutMirroring.enabled
    readonly property real observedTextScale:BleeckerTheme.textScale
    readonly property Item control:zLoader.active ? zLoader.item:hLoader.active ? hLoader.item:vLoader.item
    readonly property Item parentLayout:definition.parentLayout==="hstack" ? horizontal:definition.parentLayout==="vstack" ? vertical:null
    readonly property Item leadingItem:definition.parentLayout==="hstack" ? hLeading:definition.parentLayout==="vstack" ? vLeading:null
    readonly property Item trailingItem:definition.parentLayout==="hstack" ? hTrailing:definition.parentLayout==="vstack" ? vTrailing:null
    width:definition.width;height:definition.height
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    function styleComponent():Component {
        const components={clear:clearScope,rectangle:rectangleScope,fractional:fractionalScope,opaque:opaqueScope,
            overflow:overflowScope,hidden:hiddenScope,empty:emptyScope,zero:zeroScope,wide:wideScope,
            text:textScope,"own-font":fixedScope,"system-font":fixedScope,red:redScope,button:buttonScope,
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
    function frames():var {
        const result={},emitted=[]
        if(control)for(let i=0;i<control.partCount;++i)emitted.push(rectangle(control.partAt(i)))
        if(emitted.length){result.styled=emitted;result.root=definition.parentLayout==="zstack" &&definition.offer!==null ? [rectangle(centered)]:emitted}
        for(const key of ["caller","first","second"]){const item=named(control,"surfaceModifier-"+key);if(item)result[key]=[rectangle(item)]}
        if(parentLayout)result.parent=[rectangle(parentLayout)]
        if(leadingItem)result.leading=[rectangle(leadingItem)]
        if(trailingItem)result.trailing=[rectangle(trailingItem)]
        for(const key of Object.keys(result))result[key].sort((a,b)=>a.x-b.x||a.y-b.y||a.width-b.width||a.height-b.height)
        return result
    }
    // The sealed centered corpus never requested a baseline guide. This empty
    // map records that scope; it does not establish native baseline behavior.
    function baselines():var {return {}}
    component Shell:BleeckerSurfaceModifier {
        radius:root.definition.radius===null ? BleeckerTokens.radii.card:root.definition.radius
        property bool counted:false
        function observe():void {if(partCount>0 &&!counted){counted=true;root.appearances++;root.callerInstances++}}
        Component.onCompleted:observe()
        onPartCountChanged:Qt.callLater(observe)
        Component.onDestruction:if(root &&counted)root.disappearances++
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
            id:centered;visible:root.definition.parentLayout==="zstack"
            width:root.definition.offer===null ? root.width:root.definition.offer
            height:root.definition.offer===null ? root.height:overlay.implicitHeight
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            ProposalOverlay {
                id:overlay;anchors.fill:parent;maximumWidth:root.definition.offer===null ? root.width:root.definition.offer
                Loader {id:zLoader;active:root.mounted &&root.definition.parentLayout==="zstack";BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
            }
        }
        ProposalRow {
            id:horizontal;visible:root.definition.parentLayout==="hstack";spacing:11;mirrored:context.mirrored
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            Rectangle {id:hLeading;implicitWidth:40;implicitHeight:12;color:"#a65d57"}
            Loader {id:hLoader;active:root.mounted &&root.definition.parentLayout==="hstack";BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
            Rectangle {id:hTrailing;implicitWidth:30;implicitHeight:20;color:"#c1814d"}
        }
        ProposalColumn {
            id:vertical;visible:root.definition.parentLayout==="vstack";spacing:11;padding:0
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            Rectangle {id:vLeading;implicitWidth:40;implicitHeight:12;color:"#a65d57"}
            Loader {id:vLoader;active:root.mounted &&root.definition.parentLayout==="vstack";BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
            Rectangle {id:vTrailing;implicitWidth:30;implicitHeight:20;color:"#c1814d"}
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
            contentItem:Item {BleeckerText {id:label;anchors.centerIn:parent;anchors.alignWhenCentered:false;text:button.text}}
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
