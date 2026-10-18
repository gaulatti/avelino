import QtQuick
import QtQuick.Templates as T

InheritedControl {
    id:control
    required property real start
    required property real end
    property var range:null
    property string calendar:DateRangeTools.calendarForLocale(locale.name)
    property string timeZone:DateRangeTools.systemTimeZone()
    property string pickerStyle:"inherit"
    property string controlSize:"regular"
    signal startRequested(real requestedValue)
    signal endRequested(real requestedValue)
    readonly property var dateStyle:DateRangeTools.presentation(pickerStyle,controlSize)
    readonly property Item startInput:fromField.inputItem
    readonly property Item endInput:toField.inputItem
    readonly property Item startField:fromField
    readonly property Item endField:toField
    readonly property Item presentationItem:body
    property bool componentReady:false
    readonly property real arrowFontPixels:font.pixelSize>0 ? font.pixelSize:font.pointSize/BleeckerFonts.pointSizeForPixels(1)
    implicitWidth:body.width;implicitHeight:body.height
    padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus
    font.family:BleeckerTheme.primaryFont
    font.pointSize:BleeckerFonts.pointSizeForPixels(13)
    defaultTextColor:BleeckerTheme.nativeTextPrimary
    BleeckerLayout.minimumWidth:body.width;BleeckerLayout.idealWidth:body.width
    Accessible.ignored:true
    LayoutMirroring.childrenInherit:true
    function synchronize():void {if(componentReady){fromField.synchronize();toField.synchronize()}}
    Component.onCompleted:{componentReady=true;synchronize()}
    onRangeChanged:synchronize()
    onCalendarChanged:synchronize()
    onTimeZoneChanged:synchronize()
    onLocaleChanged:synchronize()
    onPickerStyleChanged:synchronize()
    onControlSizeChanged:synchronize()
    onFontChanged:synchronize()
    onResolvedTextColorChanged:synchronize()
    Item {
        id:body;objectName:"bleeckerDateRangePresentation"
        x:(control.width-width)/2;y:(control.height-height)/2
        width:fromField.implicitWidth+arrow.width+toField.implicitWidth+16
        height:Math.max(fromField.implicitHeight,arrow.height,toField.implicitHeight)
        DateRangeField {
            id:fromField;objectName:"bleeckerDateFrom";owner:control;endpoint:"start";modelValue:control.start
            x:control.mirrored ? body.width-width:0;y:(body.height-height)/2
        }
        DateRangeArrow {
            id:arrow;objectName:"bleeckerDateArrow"
            x:control.mirrored ? toField.width+8:fromField.width+8;y:(body.height-height)/2
            pixelSize:control.arrowFontPixels;bold:control.font.bold
            color:BleeckerTheme.alpha(control.resolvedTextColor,0.5)
        }
        DateRangeField {
            id:toField;objectName:"bleeckerDateTo";owner:control;endpoint:"end";modelValue:control.end
            x:control.mirrored ? 0:fromField.width+arrow.width+16;y:(body.height-height)/2
        }
    }
}
