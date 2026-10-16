pragma FunctionSignatureBehavior: Enforced
import QtQuick
import QtQuick.Templates as T

Item {
    id:part
    required property Item labelItem
    required property var style
    readonly property Item inputItem:input
    readonly property Item presentationItem:body
    readonly property Item labelLayout:row
    readonly property bool roundedContentClipping:clipper.roundedClipping
    readonly property point contentOriginOffset:bodyAlignment.offset
    readonly property real parentOffer:BleeckerLayout.proposedWidth
    readonly property real effectiveOffer:style.widthOffer>=0 ? style.widthOffer
        :style.maximumWidth<0 ? parentOffer:parentOffer<0 ? style.maximumWidth:Math.min(style.maximumWidth,parentOffer)
    BleeckerLayout.minimumWidth:style.widthOffer>=0 ? style.widthOffer:style.labelPadding*2+row.minimumWidth
    BleeckerLayout.idealWidth:style.widthOffer>=0 ? style.widthOffer:style.labelPadding*2+row.naturalWidth
    implicitWidth:style.widthOffer>=0 ? style.widthOffer:body.width
    implicitHeight:body.height
    x:(style.width-width)/2;y:(style.height-height)/2
    function attach():void {if(labelItem && labelHost)labelItem.parent=labelHost}
    Component.onCompleted:{attach();Qt.callLater(function(){console.warn("PART_SYNC",part.style.variant,part.labelItem.text,part.width,body.width,clipper.width,background.width,row.implicitWidth,row.width,labelHost.width,clipper.debugContentsWidth,clipper.debugTextureWidth,clipper.debugSourceRect,clipper.debugPath)})}
    Timer {interval:500;running:true;onTriggered:console.info("PART_SIZES",part.style.variant,part.labelItem.text,part.width,body.width,clipper.width,background.width,row.implicitWidth,row.width,labelHost.width,clipper.debugContentsWidth,clipper.debugTextureWidth,clipper.debugSourceRect,clipper.debugPath)}
    Component.onDestruction:if(labelItem && labelItem.parent===labelHost)labelItem.parent=null
    onLabelItemChanged:attach()
    onImplicitWidthChanged:if(style)style.refreshGeometry()
    onImplicitHeightChanged:if(style)style.refreshGeometry()
    T.Button {
        id:input;objectName:"bleeckerButtonStyleInput"
        x:(part.width-width)/2;y:(part.height-height)/2
        width:body.width;height:body.height
        padding:0;background:null;contentItem:null;focusPolicy:Qt.StrongFocus
        text:typeof part.labelItem.text==="string" ? part.labelItem.text:""
        Accessible.name:part.labelItem.Accessible.name.length ? part.labelItem.Accessible.name:text
        onDownChanged:part.style.refreshPressed()
        onClicked:part.style.clicked()
    }
    Item {
        id:body;objectName:"bleeckerButtonStylePresentation"
        x:(part.width-width)/2;y:(part.height-height)/2
        width:row.implicitWidth+part.style.labelPadding*2
        height:Math.max(part.style.minimumHeight,row.implicitHeight)
        opacity:part.enabled ? 1:0.45
        PixelAlignment {id:bodyAlignment;target:body}
        Item {
            id:visual;anchors.fill:parent
            transform:Translate {x:bodyAlignment.offset.x;y:bodyAlignment.offset.y}
            Item {
                id:offset; width:parent.width;height:parent.height
                RoundedContent {
                    id:clipper;anchors.fill:parent;radius:BleeckerTokens.radii.button;clipsInput:false
                    ContinuousSurface {
                        id:background;objectName:"bleeckerButtonStyleBackground"
                        anchors.fill:parent;radius:BleeckerTokens.radii.button;borderWidth:0;color:part.style.colorFor(false)
                    }
                    ProposalRow {
                        id:row;x:part.style.labelPadding;y:(parent.height-height)/2
                        maximumWidth:part.effectiveOffer<0 ? -1:Math.max(0,part.effectiveOffer-part.style.labelPadding*2)
                        mirrored:part.style.mirrored;spacing:0
                        Item {id:labelHost;BleeckerLayout.flattenChildren:true}
                    }
                }
                Rectangle {
                    anchors.fill:parent;radius:BleeckerTokens.radii.button
                    color:"transparent";border.width:1;border.color:part.style.strokeColor;antialiasing:true
                }
            }
            states:State {
                name:"pressed";when:part.style.down
                PropertyChanges {target:visual;scale:0.99}
                PropertyChanges {target:offset;y:1}
                PropertyChanges {target:background;color:part.style.colorFor(true)}
            }
            transitions:Transition {
                NumberAnimation {properties:"scale,y";duration:BleeckerTheme.reducedMotion ? 0:BleeckerTokens.durations.control;easing.type:Easing.OutCubic}
                ColorAnimation {properties:"color";duration:BleeckerTheme.reducedMotion ? 0:BleeckerTokens.durations.control;easing.type:Easing.OutCubic}
            }
        }
    }
}
