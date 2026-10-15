import QtQuick

Item {
    id:control
    required property string eyebrow
    required property string title
    required property string description
    default property alias actions:actionRow.data
    readonly property Item presentationItem:body
    implicitWidth:body.naturalWidth
    implicitHeight:body.implicitHeight
    ProposalRow {
        id:body;objectName:"bleeckerPageHeaderPresentation"
        maximumWidth:control.width;spacing:BleeckerTokens.spacing.group
        mirrored:control.LayoutMirroring.enabled
        y:(control.height-height)/2
        Item {
            id:labels;objectName:"bleeckerPageHeaderLabels"
            BleeckerLayout.minimumWidth:0
            BleeckerLayout.idealWidth:Math.max(eyebrowLabel.unwrappedWidth,titleLabel.unwrappedWidth,descriptionLabel.unwrappedWidth)
            implicitWidth:Math.max(eyebrowLabel.width,titleLabel.width,descriptionLabel.width)
            implicitHeight:eyebrowLabel.height+titleLabel.height+descriptionLabel.height+8
            OwnedText {
                id:eyebrowLabel;objectName:"bleeckerPageHeaderEyebrow"
                text:control.eyebrow.toUpperCase();tracking:1.2
                wrapWidth:labels.BleeckerLayout.proposedWidth
                width:wrapWidth<0 ? implicitWidth:Math.min(implicitWidth,wrapWidth)
                x:control.LayoutMirroring.enabled ? labels.width-width:0
                horizontalAlignment:control.LayoutMirroring.enabled ? Qt.AlignRight:Qt.AlignLeft
                font.pointSize:BleeckerFonts.pointSizeForPixels(10);font.weight:Font.Bold
                color:BleeckerTheme.palette.desert
                Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
            }
            OwnedText {
                id:titleLabel;objectName:"bleeckerPageHeaderTitle"
                text:control.title;tracking:-0.5;y:eyebrowLabel.height+4
                wrapWidth:labels.BleeckerLayout.proposedWidth
                width:wrapWidth<0 ? implicitWidth:Math.min(implicitWidth,wrapWidth)
                x:control.LayoutMirroring.enabled ? labels.width-width:0
                horizontalAlignment:control.LayoutMirroring.enabled ? Qt.AlignRight:Qt.AlignLeft
                font.pointSize:BleeckerFonts.pointSizeForPixels(25);font.weight:Font.DemiBold
                Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
            }
            OwnedText {
                id:descriptionLabel;objectName:"bleeckerPageHeaderDescription"
                text:control.description;y:titleLabel.y+titleLabel.height+4
                wrapWidth:labels.BleeckerLayout.proposedWidth
                width:wrapWidth<0 ? implicitWidth:Math.min(implicitWidth,wrapWidth)
                x:control.LayoutMirroring.enabled ? labels.width-width:0
                horizontalAlignment:control.LayoutMirroring.enabled ? Qt.AlignRight:Qt.AlignLeft
                font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13)
                color:BleeckerTheme.palette.textSecondary
                Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
            }
        }
        Item {implicitWidth:8;BleeckerLayout.fillsWidth:true;Accessible.ignored:true}
        ProposalRow {
            id:actionRow;objectName:"bleeckerPageHeaderActions"
            spacing:BleeckerTokens.spacing.control;mirrored:control.LayoutMirroring.enabled
            maximumWidth:BleeckerLayout.proposedWidth
            BleeckerLayout.minimumWidth:actionRow.minimumWidth
            BleeckerLayout.idealWidth:actionRow.naturalWidth
        }
    }
}
