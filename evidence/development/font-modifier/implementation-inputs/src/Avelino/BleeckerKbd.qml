import QtQuick
import QtQuick.Templates as T

T.Control {
    id:control
    required property string key
    property real maximumWidth:-1
    readonly property Item presentationItem:body
    readonly property real proposal:BleeckerTextTools.proposedWidth(maximumWidth,12)
    font.family:BleeckerFonts.monospace
    palette.windowText:BleeckerTheme.nativeTextPrimary
    font.pointSize:BleeckerFonts.pointSizeForPixels(10);font.weight:Font.Medium
    padding:0;background:null
    implicitWidth:body.implicitWidth;implicitHeight:body.implicitHeight
    Item {
        id:body;objectName:"bleeckerKbdPresentation"
        x:(control.width-width)/2;y:(control.height-height)/2
        implicitWidth:label.width+12;implicitHeight:Math.max(22,label.height)
        CircularContent {
            anchors.fill:parent;radius:4
            Rectangle {anchors.fill:parent;radius:4;color:BleeckerTheme.palette.muted;antialiasing:true}
            OwnedText {
                id:label;objectName:"bleeckerKbdKey";text:control.key;font:control.font;color:control.palette.windowText
                wrapWidth:control.proposal;width:wrapWidth<0 ? implicitWidth:Math.min(implicitWidth,wrapWidth)
                x:6;y:(body.height-height)/2;clip:true
                Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
            }
        }
        Rectangle {anchors.fill:parent;radius:4;color:"transparent";border.width:1;border.color:BleeckerTheme.palette.border;antialiasing:true}
    }
    Accessible.ignored:true
}
