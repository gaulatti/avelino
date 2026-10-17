pragma FunctionSignatureBehavior: Enforced
import QtQuick
import Avelino

Item {
    id:root
    required property var definition
    property bool styled:true
    property bool mounted:true
    property int appearances:0
    property int disappearances:0
    property int callerInstances:0
    readonly property Item activeLayout:layout.item
    readonly property Item group:activeLayout ? activeLayout.group:null
    readonly property Item control:group ? group.primaryControl:null
    readonly property Item styledItem:control ? styled ? control.partAt(0):control:null
    readonly property Item label:styledItem ? styled ? styledItem.callerItem:styledItem:null
    width:640;height:400
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    function escapeHtml(value:string):string {return value.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\"/g,"&quot;")}
    function image():string {
        const size=styled ? 9:definition.parentFont ? 32:13
        const color=styled ? BleeckerTheme.palette.sea:definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.palette.textPrimary
        const svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'" viewBox="0 0 12 12"><path d="M 2 6 L 4.7 8.7 L 10 3.2" fill="none" stroke="'+color+'" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        return '<img src="data:image/svg+xml;utf8,'+encodeURIComponent(svg)+'" width="'+size+'" height="'+size+'"/>'
    }
    function content():string {
        const f=definition
        if(f.style==="concat")return '<span style="font-family:Encode Sans;font-size:17px;font-weight:400">Status </span><b style="color:'+BleeckerTheme.nativeRed+'">'+escapeHtml(f.text)+'</b>'
        if(f.style==="attributed")return '<span style="font-family:serif;font-size:20px;font-weight:300;color:'+BleeckerTheme.nativeRed+'">Ready</span>'
        if(f.style==="image")return image()
        if(f.style==="image-text")return 'Ready '+image()
        return f.text
    }
    function ownFont():font {
        const f=definition.style
        const families={primary19:BleeckerFonts.primary,secondary19:BleeckerFonts.secondary,mono3:BleeckerFonts.monospace,mono32:BleeckerFonts.monospace,system32:Qt.application.font.family}
        const sizes={primary19:19,secondary19:19,mono3:3,mono32:32,system32:32}
        const weights={primary19:Font.Normal,secondary19:Font.Bold,mono3:Font.Normal,mono32:Font.Light,system32:Font.Bold}
        if(families[f]===undefined)return context.font
        return Qt.font({family:families[f],pointSize:BleeckerFonts.pointSizeForPixels(sizes[f]),weight:weights[f]})
    }
    function rect(item:Item):var {const p=item.mapToItem(root,0,0);return {x:p.x,y:p.y,width:item.width,height:item.height}}
    function frames():var {
        if(!label)return {}
        const result={root:[rect(group)],styled:[rect(styledItem)],label:[rect(label)]}
        if(definition.parentLayout!=="center")result.parent=[rect(activeLayout)]
        if(definition.parentLayout==="baseline")result.reference=[rect(activeLayout.reference)]
        if(["hstack","vstack"].includes(definition.parentLayout)){result.leading=[rect(activeLayout.leading)];result.trailing=[rect(activeLayout.trailing)]}
        return result
    }
    function baselines():var {
        if(definition.parentLayout!=="baseline" ||!label)return {}
        return {root:group.baselineOffset,styled:styledItem.baselineOffset,label:label.baselineOffset,reference:30}
    }
    component Caller:BleeckerText {
        id:caller;objectName:"pillCaller"
        text:root.content()
        textFormat:root.definition.style==="markdown" ? Text.MarkdownText:["concat","attributed","image","image-text"].includes(root.definition.style) ? Text.RichText:Text.PlainText
        maximumLineCount:root.definition.lineLimit===null ? 2147483647:root.definition.lineLimit
        tracking:root.definition.style==="tracking" ? 1.25:0
        kerning:root.definition.style==="kerning" ? 2:0
        baselineShift:root.definition.style==="baseline5" ? 5:0
        accessibleText:root.definition.style==="image" ? "checkmark":root.definition.style==="image-text" ? "Ready checkmark":BleeckerTextTools.plainText(text,textFormat)
        Binding {target:caller;property:"font";when:["primary19","secondary19","mono3","mono32","system32"].includes(root.definition.style);value:root.ownFont()}
        Binding {target:caller;property:"font.weight";when:root.definition.style==="bold";value:Font.Bold}
        Binding {target:caller;property:"font.italic";when:root.definition.style==="italic";value:true}
        Binding {target:caller;property:"font.underline";when:root.definition.style==="underline";value:true}
        Binding {target:caller;property:"font.strikeout";when:root.definition.style==="strike";value:true}
        Binding {target:caller;property:"color";when:["red","style-red"].includes(root.definition.style);value:BleeckerTheme.nativeRed}
        Component.onCompleted:{root.appearances++;root.callerInstances++}
        Component.onDestruction:if(root)root.disappearances++
    }
    Component {id:publicScope;BleeckerPill {Caller {}}}
    Component {id:bareScope;Caller {}}
    component Group:ProposalOverlay {
        id:group
        readonly property Item primaryControl:contents.item
        BleeckerLayout.minimumWidth:root.definition.offer===null ? minimumWidth:root.definition.offer
        BleeckerLayout.idealWidth:root.definition.offer===null ? naturalWidth:root.definition.offer
        maximumWidth:root.definition.offer===null ? BleeckerLayout.proposedWidth:root.definition.offer
        opacity:root.definition.hidden ? 0:1
        enabled:!root.definition.disabled
        Loader {id:contents;active:root.mounted;BleeckerLayout.flattenChildren:true;sourceComponent:root.styled ? publicScope:bareScope}
    }
    component PixelRectangle:Item {
        id:pixelRectangle
        property color color
        // The native sharp rectangles snap paint while retaining fractional
        // frames. The lower right corner also preserves clipped negative ties.
        PixelAlignment {id:pixelAlignment;target:pixelRectangle;origin:Qt.point(pixelRectangle.width,pixelRectangle.height)}
        SharpRectangle {
            x:pixelAlignment.offset.x;y:pixelAlignment.offset.y
            width:parent.width;height:parent.height;color:pixelRectangle.color
        }
    }
    component Leading:PixelRectangle {implicitWidth:40;implicitHeight:12;color:"#a65d57"}
    component Trailing:PixelRectangle {implicitWidth:30;implicitHeight:20;color:"#c1814d"}
    Component {id:center;ProposalOverlay {readonly property Item group:cell;maximumWidth:640;Group {id:cell}}}
    Component {id:horizontal;ProposalRow {readonly property Item group:cell;readonly property Item leading:a;readonly property Item trailing:b;spacing:11;mirrored:context.mirrored;Leading {id:a} Group {id:cell} Trailing {id:b}}}
    Component {id:vertical;ProposalColumn {readonly property Item group:cell;readonly property Item leading:a;readonly property Item trailing:b;spacing:11;padding:0;Leading {id:a} Group {id:cell} Trailing {id:b}}}
    Component {id:baseline;ProposalRow {readonly property Item group:cell;readonly property Item reference:marker;spacing:11;verticalAlignment:Qt.AlignBaseline;mirrored:context.mirrored;Group {id:cell} PixelRectangle {id:marker;implicitWidth:3;implicitHeight:30;color:"#2c5784"}}}
    InheritedControl {
        id:context;anchors.fill:parent;padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus;Accessible.ignored:true
        font.family:root.definition.parentFont ? Qt.application.font.family:BleeckerFonts.primary
        font.pointSize:BleeckerFonts.pointSizeForPixels(root.definition.parentFont ? 32:13)
        font.weight:root.definition.parentFont ? Font.Bold:Font.Normal
        palette.windowText:root.definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.palette.textPrimary
        palette.disabled.windowText:root.definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.palette.textPrimary
        ProposalOverlay {
            anchors.fill:parent;maximumWidth:640
            Loader {
                id:layout;BleeckerLayout.flattenChildren:true
                sourceComponent:root.definition.parentLayout==="center" ? center:root.definition.parentLayout==="hstack" ? horizontal:root.definition.parentLayout==="vstack" ? vertical:baseline
            }
        }
    }
}
