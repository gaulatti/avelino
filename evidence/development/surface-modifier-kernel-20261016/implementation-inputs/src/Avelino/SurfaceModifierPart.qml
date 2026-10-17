import QtQuick

SurfacePartBase {
    id:part
    required property Item callerItem
    property real radius:12
    readonly property Item contentHost:measure
    readonly property bool containsTextBaseline:measure.containsTextBaseline
    implicitWidth:measure.implicitWidth
    implicitHeight:measure.implicitHeight
    baselineOffset:measure.baselineOffset
    BleeckerLayout.minimumWidth:measure.minimumWidth
    BleeckerLayout.idealWidth:measure.naturalWidth
    BleeckerLayout.firstBaseline:containsTextBaseline ? baselineOffset:NaN
    BleeckerSurface {
        anchors.fill:parent;radius:part.radius
        ProposalOverlay {
            id:measure;anchors.fill:parent
            maximumWidth:part.BleeckerLayout.proposedWidth
        }
    }
}
