import QtQuick

Item {
    id:control
    required property Component icon
    property string size:"md"
    property string variant:"primary"
    readonly property real edge:size==="md" ? 36:size==="lg" ? 48:failSize()
    readonly property int variantIndex:{switch(variant){case "primary":return 0;case "subtle":return 1;case "outlined":return 2;default:throw new Error("Unknown icon-badge variant: "+variant)}}
    readonly property color foregroundColor:variantIndex===0 ? BleeckerTheme.palette.primaryForeground:BleeckerTheme.palette.sea
    readonly property Item presentationItem:body
    implicitWidth:edge;implicitHeight:edge
    function failSize(){throw new Error("Unknown icon-badge size: "+size)}
    Item {
        id:body;objectName:"bleeckerIconBadgePresentation";width:control.edge;height:control.edge
        x:(control.width-width)/2;y:(control.height-height)/2
        CircularContent {
            anchors.fill:parent
            Rectangle {anchors.fill:parent;radius:BleeckerTokens.radii.ui;color:control.variantIndex===0 ? BleeckerTheme.palette.primary:BleeckerTheme.palette.muted;antialiasing:true}
            Loader {
                id:slot;objectName:"bleeckerIconBadgeIcon";anchors.centerIn:parent;sourceComponent:control.icon
                readonly property color foregroundColor:control.foregroundColor
                readonly property real pixelSize:control.edge*0.4
                readonly property font font:Qt.font({family:Qt.application.font.family,pointSize:BleeckerFonts.pointSizeForPixels(pixelSize),weight:Font.Medium})
            }
        }
        Rectangle {anchors.fill:parent;radius:BleeckerTokens.radii.ui;color:"transparent";border.width:control.variantIndex===2 ? 1:0;border.color:BleeckerTheme.alpha(BleeckerTheme.palette.sea,0.4);antialiasing:true}
    }
    Accessible.ignored:true
}
