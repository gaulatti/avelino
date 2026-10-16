pragma FunctionSignatureBehavior: Enforced
import QtQuick
import QtQuick.Window

InheritedControl {
    id:control
    required property string title
    property real modalWidth:480
    default property alias content:contentHost.data
    property color foreground:resolvedTextColor
    // Qt presentation owners override this action when they present a sheet.
    property var dismissAction:function(){const window=control.Window.window;if(window)window.close()}
    readonly property Item presentationItem:body
    readonly property Item closeInput:close.inputItem
    readonly property bool roundedContentClipping:clipper.roundedClipping
    property bool componentReady:false
    implicitWidth:modalWidth;implicitHeight:body.implicitHeight
    padding:0;background:null;focusPolicy:Qt.NoFocus
    defaultTextColor:BleeckerTheme.nativeTextPrimary
    Accessible.ignored:true
    function validate(){
        if(!Number.isFinite(modalWidth) || modalWidth<0)throw new Error("Modal width must be finite and nonnegative")
        if(typeof dismissAction!=="function")throw new Error("Modal dismissal requires an action")
    }
    Component.onCompleted:{componentReady=true;validate()}
    onModalWidthChanged:if(componentReady)validate()
    onDismissActionChanged:if(componentReady)validate()
    Item {
        id:body;objectName:"bleeckerModalPresentation"
        width:control.modalWidth;implicitHeight:header.implicitHeight+41+column.implicitHeight
        height:implicitHeight;x:(control.width-width)/2;y:(control.height-height)/2
        SurfaceShadow {
            objectName:"bleeckerModalShadow";surfaceWidth:body.width;surfaceHeight:body.height
            radius:BleeckerTokens.radii.dialog;roundedRectangle:true;blurRadius:32;offsetY:12
            shadowColor:BleeckerTheme.alpha(BleeckerTheme.palette.deepSea,0.24);fillColor:BleeckerTheme.palette.card
        }
        Rectangle {anchors.fill:parent;radius:BleeckerTokens.radii.dialog;color:BleeckerTheme.palette.card;antialiasing:true;Accessible.ignored:true}
        CircularContent {
            id:clipper;anchors.fill:parent;radius:BleeckerTokens.radii.dialog;clipsInput:false
            ProposalRow {
                id:header;objectName:"bleeckerModalHeaderRow"
                x:(body.width-width)/2;y:20;maximumWidth:Math.max(0,body.width-40);spacing:0;mirrored:control.mirrored
                Item {
                    id:titleCell
                    BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:heading.unwrappedWidth
                    implicitWidth:heading.width;implicitHeight:heading.height
                    OwnedText {
                        id:heading;objectName:"bleeckerModalTitle";text:control.title
                        wrapWidth:titleCell.BleeckerLayout.proposedWidth;width:fittedWidth
                        horizontalAlignment:control.mirrored ? Qt.AlignRight:Qt.AlignLeft
                        font.family:BleeckerTheme.primaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(18);font.weight:Font.DemiBold
                        color:control.foreground;clip:true
                        Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
                    }
                }
                Item {objectName:"bleeckerModalSpacer";implicitWidth:8;BleeckerLayout.fillsWidth:true;Accessible.ignored:true}
                BleeckerIconButton {
                    id:close;objectName:"bleeckerModalClose";variant:"ghost";accessibilityLabel:"Close"
                    icon:Component{ModalCloseGlyph{pixelSize:close.glyphPixelSize;color:close.foregroundColor}}
                    onClicked:control.dismissAction()
                }
            }
            PixelAlignment {id:inputMetrics;target:close}
            QtObject {
                id:closeMask
                function contains(point:point):bool{
                    const p=close.inputItem.mapToItem(close,point.x,point.y),origin=close.mapToItem(null,0,0),dpr=inputMetrics.devicePixelRatio
                    const edge=Math.ceil(close.glyphPixelSize*0.8*dpr)/dpr
                    const inset=Math.round((close.iconEdge-edge)/2*dpr)/dpr
                    const x=Math.round((origin.x+(close.width-close.iconEdge)/2+inset)*dpr)/dpr-origin.x
                    const y=Math.round((origin.y+(close.height-close.iconEdge)/2+inset)*dpr)/dpr-origin.y
                    return p.x>=x && p.x<x+edge && p.y>=y && p.y<y+edge
                }
            }
            Binding {target:close.inputItem;property:"containmentMask";value:closeMask}
            BleeckerSeparator {objectName:"bleeckerModalSeparator";width:body.width;y:header.implicitHeight+40;height:1}
            ProposalColumn {
                id:column;objectName:"bleeckerModalColumn";y:header.implicitHeight+41
                maximumWidth:body.width;width:body.width;padding:20
                Item {
                    id:contentHost;objectName:"bleeckerModalContent";BleeckerLayout.flattenChildren:true
                    readonly property font font:control.presentationFont
                    readonly property color foregroundColor:control.foreground
                }
            }
        }
    }
}
