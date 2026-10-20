import QtQuick

Item {
    id:control
    required property string name
    property real maximumWidth:-1
    readonly property Item presentationItem:row
    implicitWidth:row.implicitWidth;implicitHeight:row.implicitHeight
    ProposalRow {
        id:row;objectName:"bleeckerBrandLockupPresentation"
        x:(control.width-width)/2;y:(control.height-height)/2
        maximumWidth:BleeckerTextTools.proposedWidth(control.maximumWidth,0)
        spacing:16;mirrored:control.LayoutMirroring.enabled
        BleeckerBrandMark {objectName:"bleeckerBrandLockupMark";size:25;implicitHeight:32}
        Item {
            id:labelBox;objectName:"bleeckerBrandLockupNameBox"
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:label.unwrappedWidth
            implicitWidth:label.width;implicitHeight:label.height
            OwnedText {
                id:label;objectName:"bleeckerBrandLockupName"
                text:control.name;tracking:-0.4
                font.pointSize:BleeckerFonts.pointSizeForPixels(20);font.weight:Font.Bold
                wrapWidth:labelBox.BleeckerLayout.proposedWidth
                width:wrapWidth<0 ? implicitWidth:Math.min(implicitWidth,wrapWidth)
                horizontalAlignment:control.LayoutMirroring.enabled ? Qt.AlignRight:Qt.AlignLeft
                Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
            }
        }
    }
}
