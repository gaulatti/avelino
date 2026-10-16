import QtQuick
import Avelino

Item {
    id:fixture
    required property var definition
    property var value:definition.stepperValue
    property int requests:0
    property string requested:""
    readonly property Item control:stepper
    readonly property Item presentationItem:stepper.presentationItem
    implicitWidth:stepper.implicitWidth;implicitHeight:stepper.implicitHeight
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    BleeckerStepper {
        id:stepper
        label:definition.label;value:fixture.value;lowerBound:definition.lowerBound;upperBound:definition.upperBound
        step:definition.step;displayOffset:definition.displayOffset
        maximumWidth:definition.intrinsic ? -1:definition.proposalWidth
        enabled:!definition.disabled;locale:Qt.locale(definition.environmentLocale)
        font.pointSize:BleeckerFonts.pointSizeForPixels(definition.parentFont>0 ? definition.parentFont:13)
        onValueRequested:value => {fixture.requests++;fixture.requested=value;if(!definition.observeOnly)fixture.value=value}
    }
}
