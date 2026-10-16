import QtQuick
import QtQuick.Templates as T
import Avelino

T.Control {
    id:fixture
    required property var definition
    readonly property Item control:otp
    readonly property Item presentationItem:otp.presentationItem
    readonly property real proposal:definition.intrinsic ? definition.width:definition.proposalWidth
    width:proposal;height:otp.implicitHeight
    implicitWidth:proposal;implicitHeight:otp.implicitHeight
    padding:0;background:null
    font.pointSize:BleeckerFonts.pointSizeForPixels(definition.parentFont>0 ? definition.parentFont:13)
    palette.windowText:definition.parentForeground==="red" ? BleeckerTheme.nativeRed:BleeckerTheme.nativeTextPrimary
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    BleeckerOTPInput {
        id:otp;anchors.centerIn:parent;anchors.alignWhenCentered:false
        width:Math.max(28,fixture.proposal)
        code:fixture.definition.code;length:fixture.definition.length;enabled:!fixture.definition.disabled
        locale:Qt.locale(fixture.definition.environmentLocale)
    }
}
