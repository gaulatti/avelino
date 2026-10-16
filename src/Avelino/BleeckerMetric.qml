import QtQuick

Item {
    id:control
    required property string label
    required property real value
    property string format:"number"
    property string currencyCode:"USD"
    property real maximumWidth:-1
    readonly property string formattedValue:BleeckerNumberTools.format(value,format,currencyCode,BleeckerNumberTools.processLocale)
    readonly property real naturalWidth:Math.max(title.unwrappedWidth,number.unwrappedWidth)
    readonly property Item presentationItem:column
    readonly property real proposal:BleeckerTextTools.proposedWidth(BleeckerLayout.proposedWidth>=0 ? BleeckerLayout.proposedWidth:maximumWidth,0)
    implicitWidth:column.implicitWidth;implicitHeight:column.implicitHeight
    Item {
        id:column;objectName:"bleeckerMetricPresentation"
        x:(control.width-width)/2;y:(control.height-height)/2
        implicitWidth:Math.max(title.width,number.width);implicitHeight:title.height+4+number.height
        OwnedText {
            id:title;objectName:"bleeckerMetricLabel";text:control.label.toUpperCase();tracking:1
            font.pointSize:BleeckerFonts.pointSizeForPixels(10);font.weight:Font.Bold;color:BleeckerTheme.palette.textSecondary
            wrapWidth:control.proposal;width:wrapWidth<0 ? implicitWidth:Math.min(implicitWidth,wrapWidth)
            x:control.LayoutMirroring.enabled ? column.width-width:0;clip:true
            Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
        }
        OwnedText {
            id:number;objectName:"bleeckerMetricValue";text:control.formattedValue;y:title.height+4
            font.pointSize:BleeckerFonts.pointSizeForPixels(24);font.weight:Font.DemiBold;color:BleeckerTheme.palette.textPrimary
            wrapWidth:control.proposal;width:wrapWidth<0 ? implicitWidth:Math.min(implicitWidth,wrapWidth)
            x:control.LayoutMirroring.enabled ? column.width-width:0;clip:true
            Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
        }
    }
}
