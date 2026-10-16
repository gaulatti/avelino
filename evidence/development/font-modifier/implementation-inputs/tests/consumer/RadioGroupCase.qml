import QtQuick
import QtQuick.Templates as T
import Avelino

T.Control {
    id:fixture
    required property var definition
    signal selectionRequested(var requestedValue)
    readonly property Item control:radio
    readonly property Item presentationItem:radio.presentationItem
    implicitWidth:radio.implicitWidth;implicitHeight:radio.implicitHeight
    padding:0;background:null
    font.family:definition.parentFontKind==="secondary" ? BleeckerTheme.secondaryFont
        : definition.parentFontKind==="mono" ? BleeckerFonts.monospace
        : definition.parentFontKind==="system" ? Qt.application.font.family:BleeckerTheme.primaryFont
    font.pointSize:BleeckerFonts.pointSizeForPixels(definition.parentFont>0 ? definition.parentFont:13)
    font.weight:definition.parentFontWeight==="bold" ? Font.Bold:Font.Normal
    palette.windowText:definition.parentForeground==="red" ? BleeckerTheme.nativeRed:BleeckerTheme.nativeTextPrimary
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    BleeckerRadioGroup {
        id:radio;objectName:"fixtureRadioGroup"
        selection:fixture.definition.selection;options:fixture.definition.options
        orientation:fixture.definition.orientation==="horizontal" ? Qt.Horizontal:Qt.Vertical
        maximumWidth:fixture.definition.intrinsic ? -1:fixture.definition.proposalWidth
        enabled:!fixture.definition.disabled;locale:Qt.locale(fixture.definition.environmentLocale)
        onSelectionRequested:value=>fixture.selectionRequested(value)
    }
}
