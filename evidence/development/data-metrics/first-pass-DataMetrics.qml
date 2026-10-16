import QtQuick
import QtQuick.Window
import Avelino

Window {
    id:window;width:840;height:620;visible:true;title:"Avelino data metrics"
    color:BleeckerTheme.palette.background
    property string metricLabel:"Readers"
    property real metricValue:12345.6789
    property string metricFormat:"number"
    property var cardDelta:0.123456789
    property string keyName:"Ctrl + K"
    property string cardLocale:"en_US"
    property int updates:0
    property bool showDelta:true
    Component.onCompleted:{BleeckerTheme.dark=typeof consumerDark!=="undefined" ? consumerDark:captureDark;BleeckerTheme.textScale=typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale}
    BleeckerMetric {objectName:"consumerMetric";x:24;y:30;label:window.metricLabel;value:window.metricValue;format:window.metricFormat;maximumWidth:320}
    BleeckerMetric {objectName:"consumerNarrowMetric";x:24;y:150;label:"Readers";value:12345.6789;maximumWidth:80}
    BleeckerStatCard {objectName:"consumerStatCard";x:420;y:30;label:window.metricLabel;value:window.metricValue;format:window.metricFormat;delta:window.showDelta ? window.cardDelta:null;maximumWidth:320;locale:Qt.locale(window.cardLocale);icon:DataMetricGlyph {}}
    BleeckerStatCard {objectName:"consumerRtlStatCard";x:420;y:210;label:"RTL readers";value:1234;delta:-0.12;maximumWidth:320;locale:Qt.locale("en_US");LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true;icon:DataMetricGlyph {}}
    BleeckerKbd {objectName:"consumerKeyLabel";x:24;y:330;key:window.keyName}
    BleeckerIconBadge {objectName:"consumerPrimaryBadge";x:24;y:410;icon:DataMetricGlyph {symbol:"house"}}
    BleeckerIconBadge {objectName:"consumerOutlinedBadge";x:90;y:410;size:"lg";variant:"outlined";icon:DataMetricGlyph {symbol:"minus"}}
    BleeckerTextField {objectName:"metricsOutsideField";x:24;y:510;width:320;placeholderText:"Continue editing"}
    BleeckerButton {objectName:"metricsUpdateButton";x:420;y:510;text:"Update metrics";onClicked:{window.updates++;window.metricLabel="Updated readers";window.metricValue=0.123456789;window.metricFormat="percent";window.cardDelta=-0.05;window.keyName="Enter"}}
}
