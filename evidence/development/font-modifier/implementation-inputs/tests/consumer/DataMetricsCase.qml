import QtQuick
import QtQuick.Templates as T
import Avelino

T.Control {
    id:fixture
    required property var definition
    readonly property Item control:loader.item
    readonly property Item presentationItem:control ? control.presentationItem:null
    implicitWidth:control ? control.width:0;implicitHeight:control ? control.height:0
    font.family:BleeckerTheme.primaryFont;font.pointSize:definition.parentFont>0 ? BleeckerFonts.pointSizeForPixels(definition.parentFont):Qt.application.font.pointSize
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    Loader {id:loader;sourceComponent:definition.api==="BleeckerMetric" ? metric:definition.api==="BleeckerStatCard" ? stat:definition.api==="BleeckerKbd" ? kbd:badge}
    Component {id:metric;BleeckerMetric {label:definition.text;value:definition.value;format:definition.format;currencyCode:definition.currencyCode;maximumWidth:definition.proposalWidth;enabled:!definition.disabled}}
    Component {id:stat;BleeckerStatCard {label:definition.text;value:definition.value;format:definition.format;delta:definition.delta;maximumWidth:definition.proposalWidth;locale:Qt.locale(definition.environmentLocale);enabled:!definition.disabled;icon:DataMetricGlyph {symbol:definition.symbol}}}
    Component {id:kbd;BleeckerKbd {key:definition.text;maximumWidth:definition.proposalWidth;enabled:!definition.disabled}}
    Component {id:badge;BleeckerIconBadge {size:definition.size;variant:definition.variant;enabled:!definition.disabled;icon:DataMetricGlyph {symbol:definition.symbol}}}
}
