import QtQuick
import QtQuick.Templates as T

T.Control {
    id:control
    required property string title
    required property Component content
    property string type:"info"
    property real maximumWidth:-1
    property Component icon:AlertGlyph {type:control.type;color:control.tone}
    readonly property Item loadedContent:slot.item
    readonly property Item presentationItem:body
    readonly property bool roundedContentClipping:clipper.roundedClipping
    readonly property color tone:[BleeckerTheme.palette.sea,BleeckerTheme.palette.live,BleeckerTheme.palette.destructive,BleeckerTheme.palette.desert][BleeckerValueTools.alertTypeIndex(type)]
    readonly property real proposedContentWidth:BleeckerTextTools.proposedWidth(maximumWidth,28+12+glyph.implicitWidth)
    readonly property bool mirroredLayout:LayoutMirroring.enabled
    implicitWidth:body.width
    implicitHeight:body.height
    padding:0;background:null;focusPolicy:Qt.NoFocus
    font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13)
    palette.windowText:BleeckerTheme.palette.textPrimary
    Accessible.ignored:true
    contentItem:Item {
        Item {
            id:body;objectName:"bleeckerAlertPresentation"
            x:(parent.width-width)/2;y:(parent.height-height)/2
            width:28+glyph.width+12+Math.max(heading.width,slot.item ? slot.width:0)
            height:28+Math.max(glyph.height+1,heading.height+(control.content ? 4+slot.height:0))
            Rectangle {anchors.fill:parent;radius:BleeckerTokens.radii.ui;color:BleeckerTheme.alpha(control.tone,0.09);antialiasing:true;Accessible.ignored:true}
            CircularContent {
                id:clipper;anchors.fill:parent
                Loader {
                    id:glyph;objectName:"bleeckerAlertIcon";sourceComponent:control.icon
                    x:control.mirroredLayout ? body.width-14-width:14;y:15
                    Accessible.ignored:true
                }
                OwnedText {
                    id:heading;objectName:"bleeckerAlertTitle"
                    text:control.title;wrapWidth:control.proposedContentWidth
                    x:control.mirroredLayout ? body.width-14-glyph.width-12-width:14+glyph.width+12;y:14
                    font.pointSize:BleeckerFonts.pointSizeForPixels(14);font.weight:Font.DemiBold
                    color:BleeckerTheme.palette.textPrimary
                    Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
                }
                Loader {
                    id:slot;objectName:"bleeckerAlertContent";sourceComponent:control.content
                    readonly property real availableWidth:control.proposedContentWidth
                    readonly property font font:control.font
                    readonly property color foregroundColor:BleeckerTheme.palette.textPrimary
                    x:control.mirroredLayout ? body.width-14-glyph.width-12-width:14+glyph.width+12;y:14+heading.height+4
                }
            }
            Rectangle {anchors.fill:parent;radius:BleeckerTokens.radii.ui;color:"transparent";border.width:1;border.color:BleeckerTheme.alpha(control.tone,0.24);antialiasing:true;Accessible.ignored:true}
        }
    }
}
