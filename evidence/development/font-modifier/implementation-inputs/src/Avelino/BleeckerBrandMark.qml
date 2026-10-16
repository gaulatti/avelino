import QtQuick

Item {
    id:control
    property real size:64
    readonly property real edge:BleeckerValueTools.brandSize(size)
    readonly property Item presentationItem:image
    implicitWidth:edge;implicitHeight:edge
    BrandImage {
        id:image;objectName:"bleeckerBrandMarkImage"
        width:control.edge;height:control.edge
        x:(control.width-width)/2;y:(control.height-height)/2
        color:BleeckerTheme.alpha(BleeckerTheme.palette.textPrimary,0.9)
        Accessible.ignored:true
    }
    Accessible.ignored:true
}
