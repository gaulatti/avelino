import QtQuick

Item {
    id:control
    property string message:qsTr("Loading…")
    readonly property Item cardItem:card
    readonly property bool roundedContentClipping:clipHost.roundedClipping
    implicitWidth:48+Math.max(32,label.unwrappedWidth)
    implicitHeight:card.height
    Accessible.ignored:true
    Rectangle {anchors.fill:parent;color:BleeckerTheme.alpha(BleeckerTheme.palette.background,0.72)}
    // The pinned source blocks pointer input within the offered rectangle.
    // It does not establish keyboard trapping or modal reader semantics.
    MouseArea {anchors.fill:parent;acceptedButtons:Qt.AllButtons;hoverEnabled:true}
    Item {
        id:card;objectName:"bleeckerLoadingOverlayCard"
        x:(control.width-width)/2;y:(control.height-height)/2
        width:48+Math.max(spinner.width,label.width)
        height:48+spinner.height+12+label.height
        ContinuousSurface {anchors.fill:parent;radius:BleeckerTokens.radii.dialog;color:BleeckerTheme.palette.card;borderWidth:0}
        RoundedContent {
            id:clipHost;anchors.fill:parent;radius:BleeckerTokens.radii.dialog
            BleeckerLoadingSpinner {id:spinner;objectName:"bleeckerLoadingOverlaySpinner";size:"lg";x:(card.width-width)/2;y:24}
            OwnedText {
                id:label;objectName:"bleeckerLoadingOverlayMessage"
                text:control.message;wrapWidth:Math.max(0,control.width-48)
                x:(card.width-width)/2;y:spinner.y+spinner.height+12
                font.pointSize:BleeckerFonts.pointSizeForPixels(14);font.weight:Font.Medium
                color:BleeckerTheme.nativeTextPrimary
                Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
            }
        }
    }
}
