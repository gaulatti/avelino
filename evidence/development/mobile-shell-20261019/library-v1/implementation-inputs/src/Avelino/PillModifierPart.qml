import QtQuick

SurfacePartBase {
    id:part
    required property Item callerItem
    readonly property Item contentHost:measure
    readonly property bool containsTextBaseline:measure.containsTextBaseline
    readonly property real contentProposal:BleeckerLayout.proposedWidth<0 ? -1:Math.max(0,BleeckerLayout.proposedWidth-14)
    implicitWidth:measure.implicitWidth+14
    implicitHeight:measure.implicitHeight+8
    baselineOffset:measure.baselineOffset+4
    BleeckerLayout.minimumWidth:measure.minimumWidth+14
    BleeckerLayout.idealWidth:measure.naturalWidth+14
    BleeckerLayout.firstBaseline:containsTextBaseline ? baselineOffset:NaN
    CapsuleContent {
        anchors.fill:parent
        Rectangle {anchors.fill:parent;color:BleeckerTheme.palette.muted}
        ProposalOverlay {
            id:measure;x:7;y:4
            width:Math.max(0,part.width-14);height:Math.max(0,part.height-8)
            maximumWidth:part.contentProposal
        }
    }
}
