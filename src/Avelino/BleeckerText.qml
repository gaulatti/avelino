import QtQuick

InheritedControl {
    id:label
    property string text:""
    property int textFormat:Text.PlainText
    property int maximumLineCount:2147483647
    property real kerning:0
    property real baselineShift:0
    property string accessibleText:BleeckerTextTools.plainText(text,textFormat)
    property color color:resolvedTextColor
    property real tracking:0
    property int horizontalAlignment:mirrored ? Qt.AlignRight:Qt.AlignLeft
    readonly property bool containsTextBaseline:true
    readonly property bool bleeckerTextContent:true
    readonly property bool formattedLayout:textFormat!==Text.PlainText ||maximumLineCount!==2147483647
    readonly property real offeredWidth:BleeckerLayout.proposedWidth
    readonly property Item textRenderer:formattedLayout ? formatted.item ? formatted.item.renderer:null:renderer
    readonly property real naturalWidth:formattedLayout ? formatted.item ? formatted.item.naturalWidth:0:renderer.unwrappedWidth
    readonly property real measuredWidth:formattedLayout ? formatted.item &&formatted.item.renderer ? formatted.item.renderer.contentWidth:0:renderer.implicitWidth
    readonly property real measuredHeight:formattedLayout ? formatted.item &&formatted.item.renderer ? formatted.item.renderer.implicitHeight:0:renderer.naturalHeight
    readonly property real measuredBaseline:formattedLayout ? formatted.item &&formatted.item.renderer ? formatted.item.renderer.baselineOffset:0:renderer.baselineOffset
    defaultTextColor:BleeckerTheme.nativeTextPrimary
    BleeckerLayout.minimumWidth:0
    BleeckerLayout.idealWidth:naturalWidth
    BleeckerLayout.firstBaseline:baselineOffset
    implicitWidth:offeredWidth<0 ? measuredWidth
        :Math.ceil(Math.min(measuredWidth,offeredWidth)*alignment.devicePixelRatio)/alignment.devicePixelRatio
    implicitHeight:Math.ceil((measuredHeight+Math.abs(baselineShift))*alignment.devicePixelRatio)/alignment.devicePixelRatio
    baselineOffset:measuredBaseline+Math.max(0,baselineShift)
    padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus;hoverEnabled:false;wheelEnabled:false
    PixelAlignment {id:alignment;target:label;origin:Qt.point(0,label.measuredBaseline+Math.max(0,-label.baselineShift))}
    ButtonLabel {
        id:renderer
        visible:!label.formattedLayout
        text:label.formattedLayout ? "":label.text
        font:label.presentationFont;color:label.color;tracking:label.tracking+label.kerning
        wrapWidth:label.offeredWidth;horizontalAlignment:label.horizontalAlignment
        width:Math.max(label.width,implicitWidth);height:label.height;y:Math.max(0,-label.baselineShift)
        transform:Translate {x:alignment.offset.x;y:alignment.offset.y}
        Accessible.ignored:true
    }
    // Keep plain subpixel fonts on ButtonLabel; an inactive Qt Text must not
    // resolve those requests or change the existing font-only caller path.
    component FormattedText:Text {
        id:formattedText
        property bool resourcesMounted:false
        text:label.text;textFormat:label.textFormat
        font:BleeckerTextTools.spacedFont(label.presentationFont,label.tracking+label.kerning)
        color:label.color
        LayoutMirroring.enabled:false
        Accessible.ignored:true
        Component.onCompleted:{resourcesMounted=true;BleeckerTextTools.textResourcesReady(formattedText)}
        onTextChanged:if(resourcesMounted)BleeckerTextTools.textResourcesReady(formattedText)
        onTextFormatChanged:if(resourcesMounted)BleeckerTextTools.textResourcesReady(formattedText)
    }
    Loader {
        id:formatted
        active:label.formattedLayout
        sourceComponent:Component {
            Item {
                id:formattedHost
                readonly property Item renderer:wrapped
                readonly property real naturalWidth:unwrapped.implicitWidth
                implicitWidth:naturalWidth;implicitHeight:wrapped.implicitHeight
                Accessible.ignored:true
                function resourcesReady():bool {
                    const naturalReady=BleeckerTextTools.textResourcesReady(unwrapped)
                    const displayedReady=BleeckerTextTools.textResourcesReady(wrapped)
                    return naturalReady &&displayedReady
                }
                FormattedText {id:unwrapped;visible:false;wrapMode:Text.NoWrap}
                FormattedText {
                    id:wrapped
                    wrapMode:Text.Wrap
                    maximumLineCount:label.maximumLineCount
                    elide:label.maximumLineCount===2147483647 ? Text.ElideNone:Text.ElideRight
                    horizontalAlignment:label.horizontalAlignment
                    width:label.offeredWidth<0 ? formattedHost.naturalWidth:label.offeredWidth
                    y:Math.max(0,-label.baselineShift)
                    transform:Translate {x:alignment.offset.x;y:alignment.offset.y}
                }
            }
        }
    }
    function validate():void {
        if(![Text.PlainText,Text.StyledText,Text.RichText,Text.MarkdownText,Text.AutoText].includes(textFormat))throw new Error("Unsupported BleeckerText format")
        if(maximumLineCount<1 ||!Number.isInteger(maximumLineCount))throw new Error("BleeckerText maximumLineCount must be a positive integer")
        if(!Number.isFinite(kerning)||!Number.isFinite(baselineShift)||!Number.isFinite(tracking))throw new Error("BleeckerText spacing and baseline shift must be finite")
    }
    function resourcesReady():bool {return !formattedLayout ||formatted.item!==null &&formatted.item.resourcesReady()}
    Component.onCompleted:validate()
    onTextFormatChanged:validate()
    onMaximumLineCountChanged:validate()
    onKerningChanged:validate()
    onBaselineShiftChanged:validate()
    onTrackingChanged:validate()
    Accessible.role:Accessible.StaticText
    Accessible.name:accessibleText
}
