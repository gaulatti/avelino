import QtQuick

InheritedControl {
    id:control
    required property string title
    required property string detail
    required property string timestamp
    default property alias actions:actionHost.data
    property Component icon:Component {ActivityGlyph {pixelSize:parent.pixelSize;color:parent.foregroundColor}}
    property color foreground:resolvedTextColor
    property real maximumWidth:-1
    readonly property real effectiveMaximumWidth:BleeckerLayout.proposedWidth<0 ? maximumWidth
        :maximumWidth<0 ? BleeckerLayout.proposedWidth:Math.min(maximumWidth,BleeckerLayout.proposedWidth)
    readonly property real proposal:BleeckerTextTools.proposedWidth(effectiveMaximumWidth,0)
    readonly property real naturalWidth:row.naturalWidth
    readonly property real minimumWidth:row.minimumWidth
    readonly property Item presentationItem:body
    implicitWidth:proposal<0 ? naturalWidth:body.implicitWidth
    implicitHeight:body.implicitHeight
    padding:0;background:null;focusPolicy:Qt.NoFocus
    defaultTextColor:BleeckerTheme.nativeTextPrimary
    BleeckerLayout.minimumWidth:minimumWidth
    BleeckerLayout.idealWidth:naturalWidth
    Accessible.ignored:true
    Item {
        id:body;objectName:"bleeckerActivityPresentation"
        implicitWidth:row.implicitWidth;implicitHeight:row.implicitHeight+16
        x:(control.width-width)/2;y:(control.height-height)/2
    ProposalRow {
        id:row;objectName:"bleeckerActivityRow";y:8
        maximumWidth:control.proposal<0 ? control.availableWidth:control.proposal
        spacing:12;verticalAlignment:Qt.AlignTop;mirrored:control.mirrored;cancelPointerOnReflow:true
        BleeckerIconBadge {objectName:"bleeckerActivityBadge";variant:"subtle";icon:control.icon}
        Item {
            id:labels;objectName:"bleeckerActivityLabels"
            BleeckerLayout.minimumWidth:0
            BleeckerLayout.idealWidth:Math.max(titleLabel.unwrappedWidth,detailLabel.unwrappedWidth,timestampLabel.unwrappedWidth)
            implicitWidth:Math.max(titleLabel.width,detailLabel.width,timestampLabel.width)
            implicitHeight:titleLabel.height+detailLabel.height+timestampLabel.height+6
            OwnedText {
                id:titleLabel;objectName:"bleeckerActivityTitle"
                text:control.title;wrapWidth:labels.BleeckerLayout.proposedWidth
                width:fittedWidth
                x:control.mirrored ? labels.width-width:0
                horizontalAlignment:control.mirrored ? Qt.AlignRight:Qt.AlignLeft
                font.family:BleeckerTheme.primaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(14);font.weight:Font.DemiBold
                color:control.foreground;clip:true
                Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
            }
            OwnedText {
                id:detailLabel;objectName:"bleeckerActivityDetail"
                text:control.detail;y:titleLabel.height+3;wrapWidth:labels.BleeckerLayout.proposedWidth
                width:fittedWidth
                x:control.mirrored ? labels.width-width:0
                horizontalAlignment:control.mirrored ? Qt.AlignRight:Qt.AlignLeft
                font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(12);font.weight:Font.Normal
                color:BleeckerTheme.palette.textSecondary;clip:true
                Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
            }
            OwnedText {
                id:timestampLabel;objectName:"bleeckerActivityTimestamp"
                text:control.timestamp;y:detailLabel.y+detailLabel.height+3;wrapWidth:labels.BleeckerLayout.proposedWidth
                width:fittedWidth
                x:control.mirrored ? labels.width-width:0
                horizontalAlignment:control.mirrored ? Qt.AlignRight:Qt.AlignLeft
                font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(10);font.weight:Font.Normal
                color:BleeckerTheme.palette.textSecondary;clip:true
                Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
            }
        }
        Item {objectName:"bleeckerActivitySpacer";implicitWidth:8;BleeckerLayout.fillsWidth:true;Accessible.ignored:true}
        Item {
            id:actionHost;objectName:"bleeckerActivityActions"
            BleeckerLayout.flattenChildren:true
            readonly property font font:control.presentationFont
            readonly property color foregroundColor:control.foreground
        }
    }
    }
}
