import QtQuick
import QtQuick.Templates as T

RadioGroupBase {
    id:control
    anchors.alignWhenCentered:false
    required property var selection
    property var options:[]
    property var valueIdentity:null
    property int orientation:Qt.Vertical
    property real maximumWidth:-1
    property color foreground:resolvedTextColor
    signal selectionRequested(var requestedValue)
    readonly property bool horizontal:isHorizontal(orientation)
    readonly property real glyphPixelSize:font.pointSize>0 ? font.pointSize/BleeckerFonts.pointSizeForPixels(1):font.pixelSize
    readonly property real naturalWidth:layout.item ? layout.item.naturalWidth:0
    readonly property real minimumWidth:layout.item ? layout.item.minimumWidth:0
    readonly property real effectiveMaximumWidth:BleeckerLayout.proposedWidth<0 ? maximumWidth
        : maximumWidth<0 ? BleeckerLayout.proposedWidth:Math.min(maximumWidth,BleeckerLayout.proposedWidth)
    readonly property real proposal:BleeckerTextTools.proposedWidth(effectiveMaximumWidth,0)
    readonly property real layoutOffer:proposal<0 ? availableWidth:Math.min(availableWidth,proposal)
    readonly property Item presentationItem:layout.item
    readonly property int count:layout.item ? layout.item.count:0
    function optionAt(index:int):Item {return layout.item ? layout.item.optionAt(index):null}
    implicitWidth:proposal<0 ? naturalWidth:Math.max(minimumWidth,Math.min(naturalWidth,proposal))
    implicitHeight:layout.implicitHeight
    padding:0;background:null
    defaultTextColor:BleeckerTheme.nativeTextPrimary
    BleeckerLayout.minimumWidth:minimumWidth
    BleeckerLayout.idealWidth:naturalWidth
    Accessible.ignored:true
    RadioOptions {id:rows;options:control.options;selection:control.selection;valueIdentity:control.valueIdentity}
    Connections {
        target:rows
        function onRowsMoved(){Qt.callLater(function(){if(control.horizontal && layout.item)layout.item.layout()})}
    }
    Loader {
        id:layout;objectName:"bleeckerRadioGroupPresentation"
        anchors.centerIn:control;anchors.alignWhenCentered:false
        sourceComponent:control.horizontal ? horizontalLayout:verticalLayout
    }
    Component {
        id:verticalLayout
        Column {
            id:column;spacing:10
            property int itemRevision:0
            readonly property int count:verticalItems.count
            readonly property real naturalWidth:{const revision=itemRevision;let width=0;for(let i=0;i<count;i++){const item=optionAt(i);if(item)width=Math.max(width,item.naturalWidth)}return width}
            readonly property real minimumWidth:{const revision=itemRevision;let width=0;for(let i=0;i<count;i++){const item=optionAt(i);if(item)width=Math.max(width,item.minimumWidth)}return width}
            function optionAt(index:int):Item{return verticalItems.itemAt(index)}
            Repeater {id:verticalItems;model:rows;delegate:optionDelegate;onItemAdded:column.itemRevision++;onItemRemoved:column.itemRevision++}
        }
    }
    Component {
        id:horizontalLayout
        ProposalRow {
            id:row;spacing:16;maximumWidth:control.layoutOffer;mirrored:control.mirrored
            readonly property int count:horizontalItems.count
            function optionAt(index:int):Item{return horizontalItems.itemAt(index)}
            Repeater {id:horizontalItems;model:rows;delegate:optionDelegate}
        }
    }
    Component {
        id:optionDelegate
        T.Button {
            id:button
            required property int index
            required property var optionValue
            required property string optionLabel
            required property bool optionDisabled
            required property bool optionSelected
            required property string optionKey
            readonly property real naturalWidth:minimumWidth+label.unwrappedWidth
            readonly property real minimumWidth:glyph.implicitWidth+8
            readonly property real offeredWidth:control.horizontal ? BleeckerLayout.proposedWidth:control.layoutOffer
            readonly property real titleOffer:offeredWidth<0 ? -1:Math.max(0,offeredWidth-minimumWidth)
            readonly property real imageTop:label.baselineOffset-label.capHeight/2-glyph.height/2
            readonly property Item titleItem:label
            readonly property Item iconItem:glyph
            readonly property bool selected:optionSelected
            objectName:"bleeckerRadioOption"+index
            text:optionLabel;font:control.presentationFont
            enabled:!optionDisabled
            implicitWidth:minimumWidth+(titleOffer<0 ? label.unwrappedWidth:Math.min(label.implicitWidth,titleOffer))
            implicitHeight:Math.max(Math.max(0,-imageTop)+label.height,Math.max(0,imageTop)+glyph.height)
            x:control.horizontal ? 0:control.mirrored ? parent.width-width:0
            width:implicitWidth;height:implicitHeight
            BleeckerLayout.minimumWidth:minimumWidth
            BleeckerLayout.idealWidth:naturalWidth
            padding:0;background:null;autoRepeat:false;checkable:false
            focusPolicy:Qt.StrongFocus
            opacity:enabled ? (down ? 0.5:1):0.2962962962962963
            Accessible.name:optionLabel
            onIndexChanged:if(pressed)control.cancelPointerPress(button)
            onClicked:if(control.enabled && enabled)control.selectionRequested(optionValue)
            containmentMask:RadioHitMask {
                iconRect:Qt.rect(glyph.x+glyph.contentInset,glyph.y+glyph.contentInset,
                                 Math.max(0,glyph.width-2*glyph.contentInset),Math.max(0,glyph.height-2*glyph.contentInset))
                titleRect:Qt.rect(label.x,label.y,label.width,label.height)
            }
            contentItem:Item {
                RadioGlyph {
                    id:glyph;objectName:"bleeckerRadioIcon"
                    x:control.mirrored ? parent.width-width:0;y:Math.max(0,button.imageTop)
                    selected:button.optionSelected;pixelSize:control.glyphPixelSize;bold:control.font.weight>=Font.Bold
                    color:control.foreground
                }
                OwnedText {
                    id:label;objectName:"bleeckerRadioTitle"
                    text:button.optionLabel;font:control.font;color:control.foreground
                    x:control.mirrored ? 0:glyph.width+8;y:Math.max(0,-button.imageTop)
                    wrapWidth:button.titleOffer
                    width:button.titleOffer<0 ? implicitWidth:Math.min(implicitWidth,button.titleOffer)
                    clip:true
                }
            }
        }
    }
}
