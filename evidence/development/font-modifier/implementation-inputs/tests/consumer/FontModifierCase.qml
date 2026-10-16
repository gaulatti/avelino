pragma FunctionSignatureBehavior: Enforced
import QtQuick
import QtQuick.Templates as T
import Avelino

Item {
    id:root
    required property var definition
    property bool baselineParent:false
    property bool mounted:true
    property int appearances:0
    property int disappearances:0
    property int callerInstances:0
    readonly property string parentMode:baselineParent ? "baseline":definition.parentLayout
    readonly property Item control:zLoader.active ? zLoader.item:hLoader.active ? hLoader.item:vLoader.active ? vLoader.item:bLoader.item
    readonly property Item parentLayout:parentMode==="hstack" ? horizontal:parentMode==="vstack" ? vertical:parentMode==="baseline" ? baseline:null
    readonly property Item leadingItem:parentMode==="hstack" ? hLeading:parentMode==="vstack" ? vLeading:null
    readonly property Item trailingItem:parentMode==="hstack" ? hTrailing:parentMode==="vstack" ? vTrailing:null
    width:definition.width;height:definition.height
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    function styleComponent():Component {
        const components={text:textScope,"empty-view":emptyScope,zero:zeroScope,rectangle:rectangleScope,hidden:hiddenScope,
            "own-font":fixedScope,"system-font":fixedScope,"nil-font":fixedScope,red:redScope,bold:boldScope,italic:italicScope,
            attributed:attributedScope,"nested-font":nestedScope,"scaled-subtree":scaledScope,"inner-scale":innerScaleScope,
            multi:multiScope,vstack:columnScope,hstack:rowScope}
        const component=components[definition.content]
        if(!component)throw new Error("Unknown font-modifier caller content: "+definition.content)
        return component
    }
    function named(item:Item,name:string):Item {
        if(!item)return null
        if(item.objectName===name)return item
        for(const child of item.children){const found=named(child,name);if(found)return found}
        return null
    }
    function rectangle(item:Item):var {
        const point=item.mapToItem(root,0,0)
        return {x:point.x,y:point.y,width:item.width,height:item.height}
    }
    function frames():var {
        const result={},emitted=[]
        if(control)for(let index=0;index<control.partCount;++index)emitted.push(rectangle(control.partAt(index)))
        if(emitted.length){
            result.styled=emitted
            result.root=parentMode==="zstack" &&definition.offer!==null ? [rectangle(centered)]:emitted
        }
        for(const key of ["label","first","second"]){
            const item=named(control,"fontModifier-"+key)
            if(item)result[key]=[rectangle(item)]
        }
        if(parentLayout)result.parent=[rectangle(parentLayout)]
        if(leadingItem)result.leading=[rectangle(leadingItem)]
        if(trailingItem)result.trailing=[rectangle(trailingItem)]
        if(baselineParent)result.reference=[rectangle(reference)]
        for(const key of Object.keys(result))result[key].sort((a,b)=>a.x-b.x||a.y-b.y||a.width-b.width||a.height-b.height)
        return result
    }
    function baselines():var {
        if(!baselineParent)return {}
        const result={reference:reference.height}
        if(control &&control.partCount){
            const item=control.partAt(0),point=item.mapToItem(baseline,0,0)
            result.root=baseline.baselineOffset-point.y;result.styled=result.root
        }
        for(const key of ["label","first","second"]){
            const item=named(control,"fontModifier-"+key)
            if(item){
                const immediate=control &&control.partCount===1 &&control.partAt(0)===item
                result[key]=immediate ? result.root:item.baselineOffset
            }
        }
        return result
    }
    component Shell:BleeckerFont {
        family:root.definition.family;size:root.definition.size;weight:root.definition.weight
        property bool counted:false
        function observe():void {if(partCount>0 && !counted){counted=true;root.appearances++;root.callerInstances++}}
        Component.onCompleted:observe()
        onPartCountChanged:Qt.callLater(observe)
        Component.onDestruction:if(root &&counted)root.disappearances++
    }
    InheritedControl {
        id:context;anchors.fill:parent;padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus;Accessible.ignored:true
        font.family:root.definition.outerFontModifier ? BleeckerFonts.secondary:Qt.application.font.family
        font.pointSize:BleeckerFonts.pointSizeForPixels(root.definition.outerFontModifier ? Math.round(32*BleeckerTheme.textScale):root.definition.parentFont ||root.definition.outerSystem ? 32:13)
        font.weight:root.definition.outerFontModifier ? Font.Black:root.definition.parentFont ||root.definition.outerSystem ? Font.Bold:Font.Normal
        palette.windowText:BleeckerTheme.palette.textPrimary
        palette.disabled.windowText:BleeckerTheme.palette.textPrimary
        Item {
            id:centered;visible:root.parentMode==="zstack"
            width:root.definition.offer===null ? root.width:root.definition.offer
            height:root.definition.offer===null ? root.height:overlay.implicitHeight
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            ProposalOverlay {
                id:overlay;anchors.fill:parent
                maximumWidth:root.definition.offer===null ? root.width:root.definition.offer
                Loader {id:zLoader;active:root.mounted &&root.parentMode==="zstack";BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
            }
        }
        ProposalRow {
            id:horizontal;visible:root.parentMode==="hstack"
            anchors.centerIn:parent;anchors.alignWhenCentered:false;spacing:11;mirrored:context.mirrored
            Rectangle {id:hLeading;implicitWidth:40;implicitHeight:12;color:"#a65d57"}
            Loader {id:hLoader;active:root.mounted &&root.parentMode==="hstack";BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
            Rectangle {id:hTrailing;implicitWidth:30;implicitHeight:20;color:"#c1814d"}
        }
        ProposalColumn {
            id:vertical;visible:root.parentMode==="vstack"
            anchors.centerIn:parent;anchors.alignWhenCentered:false;spacing:11;padding:0
            Rectangle {id:vLeading;implicitWidth:40;implicitHeight:12;color:"#a65d57"}
            Loader {id:vLoader;active:root.mounted &&root.parentMode==="vstack";BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
            Rectangle {id:vTrailing;implicitWidth:30;implicitHeight:20;color:"#c1814d"}
        }
        ProposalRow {
            id:baseline;visible:root.baselineParent
            anchors.centerIn:parent;anchors.alignWhenCentered:false;spacing:11;verticalAlignment:Qt.AlignBaseline
            Loader {id:bLoader;active:root.mounted &&root.baselineParent;BleeckerLayout.flattenChildren:true;sourceComponent:root.styleComponent()}
            Rectangle {id:reference;implicitWidth:3;implicitHeight:30;color:"#2c5784"}
        }
    }
    Component {id:textScope;Shell {BleeckerText {objectName:"fontModifier-label";text:root.definition.text}}}
    Component {id:emptyScope;Shell {}}
    Component {id:zeroScope;Shell {Item {objectName:"fontModifier-label"}}}
    Component {id:rectangleScope;Shell {Rectangle {objectName:"fontModifier-label";implicitWidth:72;implicitHeight:44;color:"#2c5784"}}}
    Component {id:hiddenScope;Shell {BleeckerText {objectName:"fontModifier-label";text:root.definition.text;visible:false}}}
    Component {
        id:fixedScope
        Shell {
            BleeckerText {
                objectName:"fontModifier-label";text:root.definition.text
                font.family:root.definition.content==="own-font" ? BleeckerFonts.secondary:Qt.application.font.family
                font.pointSize:BleeckerFonts.pointSizeForPixels(root.definition.content==="system-font" ? 32:13)
                font.weight:root.definition.content==="nil-font" ? Font.Normal:Font.Bold
            }
        }
    }
    Component {id:redScope;Shell {BleeckerText {objectName:"fontModifier-label";text:root.definition.text;color:BleeckerTheme.nativeRed}}}
    Component {id:boldScope;Shell {BleeckerText {objectName:"fontModifier-label";text:root.definition.text;font.weight:Font.Bold}}}
    Component {id:italicScope;Shell {BleeckerText {objectName:"fontModifier-label";text:root.definition.text;font.italic:true}}}
    Component {
        id:attributedScope
        Shell {
            T.Label {
                objectName:"fontModifier-label";color:palette.windowText;textFormat:Text.RichText
                text:"<span style=\"font-family:'"+Qt.application.font.family+"';font-size:20px;font-weight:700\">Keep </span>edition"
            }
        }
    }
    Component {
        id:nestedScope
        Shell {BleeckerFont {family:"secondary";size:19;weight:"bold";BleeckerText {objectName:"fontModifier-label";text:root.definition.text}}}
    }
    Component {
        id:scaledScope
        Shell {
            Item {
                property real bleeckerTextScale:2
                BleeckerLayout.flattenChildren:true
                BleeckerFont {family:"secondary";size:19;weight:"bold";BleeckerText {objectName:"fontModifier-label";text:root.definition.text}}
            }
        }
    }
    Component {id:innerScaleScope;Shell {BleeckerText {property real bleeckerTextScale:2;objectName:"fontModifier-label";text:root.definition.text}}}
    Component {
        id:multiScope
        Shell {
            BleeckerText {objectName:"fontModifier-first";text:"First child"}
            Rectangle {objectName:"fontModifier-second";implicitWidth:72;implicitHeight:44;color:"#2c5784"}
        }
    }
    Component {
        id:columnScope
        Shell {
            ProposalColumn {
                objectName:"fontModifier-label";spacing:5;padding:0
                BleeckerText {objectName:"fontModifier-first";text:"First child"}
                BleeckerText {objectName:"fontModifier-second";text:"Second child"}
            }
        }
    }
    Component {
        id:rowScope
        Shell {
            ProposalRow {
                objectName:"fontModifier-label";spacing:5
                BleeckerText {objectName:"fontModifier-first";text:"First child"}
                BleeckerText {objectName:"fontModifier-second";text:"Second child"}
            }
        }
    }
}
