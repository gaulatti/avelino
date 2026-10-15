import QtQuick

Item {
    id:control
    required property string title
    required property string message
    property Component icon:StateGlyph {}
    property Component actions:null
    readonly property Item loadedActions:slot.item
    readonly property Item presentationItem:body
    readonly property real contentWidth:Math.max(0,width-64)
    implicitWidth:64+Math.max(glyph.implicitWidth,heading.unwrappedWidth,copy.unwrappedWidth,slot.implicitWidth)
    implicitHeight:body.height
    Accessible.ignored:true
    Item {
        id:body;objectName:"bleeckerEmptyStatePresentation"
        x:(control.width-width)/2;y:(control.height-height)/2
        width:64+Math.max(glyph.width,heading.width,copy.width,slot.width)
        height:64+glyph.height+heading.height+copy.height+24+(control.actions ? 12+slot.height : 0)
        Loader {
            id:glyph;objectName:"bleeckerEmptyStateIcon"
            sourceComponent:control.icon
            x:(body.width-width)/2;y:32
            Accessible.ignored:true
        }
        OwnedText {
            id:heading;objectName:"bleeckerEmptyStateTitle"
            text:control.title;wrapWidth:control.contentWidth
            x:(body.width-width)/2;y:glyph.y+glyph.height+12
            font.pointSize:BleeckerFonts.pointSizeForPixels(17);font.weight:Font.DemiBold
            color:BleeckerTheme.nativeTextPrimary
            Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
        }
        OwnedText {
            id:copy;objectName:"bleeckerEmptyStateMessage"
            text:control.message;wrapWidth:control.contentWidth;horizontalAlignment:Qt.AlignHCenter
            x:(body.width-width)/2;y:heading.y+heading.height+12
            font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13)
            color:BleeckerTheme.palette.textSecondary
            Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
        }
        Loader {
            id:slot;objectName:"bleeckerEmptyStateActions"
            readonly property real availableWidth:control.contentWidth
            sourceComponent:control.actions
            x:(body.width-width)/2;y:copy.y+copy.height+12
        }
    }
}
