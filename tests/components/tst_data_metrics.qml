import QtQuick
import QtTest
import Avelino
import "../consumer" as Fixtures

Item {
    id:root;width:800;height:1100
    PixelAlignment {id:metrics;target:root}
    Component {id:factory;Fixtures.DataMetricsCase {}}
    Component {id:metric;BleeckerMetric {label:"Readers";value:1234.56789}}
    Component {id:stat;BleeckerStatCard {label:"Readers";value:12345.6789;delta:0;maximumWidth:320;locale:Qt.locale("de_DE");icon:Fixtures.DataMetricGlyph {}}}
    Component {id:rawNumber;ButtonLabel {font.family:BleeckerTheme.primaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(24);font.weight:Font.DemiBold}}
    Component {id:keyLabel;BleeckerKbd {key:"Ctrl + K"}}
    TestCase {
        name:"DataMetricsContract";when:windowShown
        function init(){fixtureSetup.setProcessLocale("en_US");BleeckerTheme.dark=false;BleeckerTheme.textScale=1;failOnWarning(/Binding loop/)}
        function cleanup(){fixtureSetup.setProcessLocale("C");BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
        function test_native_source_geometry_data(){return nativeDataMetricsCaptures.filter(c=>c.api!=="BleeckerButton" && c.api!=="BleeckerKbd" && c.dpr===metrics.devicePixelRatio).map(c=>({tag:c.path,row:c}))}
        function test_native_source_geometry(data){
            const row=data.row;BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            const item=createTemporaryObject(factory,root,{definition:row});verify(item);wait(25)
            compare(item.presentationItem.width,row.componentSize.width,"Source component width");compare(item.presentationItem.height,row.componentSize.height,"Source component height")
            if(row.api==="BleeckerMetric")compare(item.control.formattedValue,row.formattedValue)
            if(row.api==="BleeckerStatCard")compare(item.control.formattedDelta,row.formattedDelta===null ? "":row.formattedDelta)
        }
        function test_numeric_text_context_data(){return nativeNumericText.filter(r=>r.dpr===metrics.devicePixelRatio).map((row,i)=>({tag:"numeric-text-"+i,row:row}))}
        function test_numeric_text_context(data){const r=data.row,item=createTemporaryObject(rawNumber,root,{text:r.text,wrapWidth:r.proposal});wait(10);compare(item.implicitWidth,r.rect.width);compare(item.implicitHeight,r.rect.height)}
        function test_source_english_formatting_data(){return nativeMetricFormatting.map((row,i)=>({tag:"native-format-"+i,row:row}))}
        function test_source_english_formatting(data){const r=data.row,v=r.value==="infinity" ? Infinity:r.value==="-infinity" ? -Infinity:Number(r.value);compare(BleeckerNumberTools.format(v,r.format,r.currencyCode,Qt.locale(r.processLocale)),r.text)}
        function test_producer_updates_and_locale_ownership(){
            const item=createTemporaryObject(metric,root);wait(20);const label=findChild(item,"bleeckerMetricValue")
            compare(item.formattedValue,"1,234.56789");item.label="Edition readers";item.value=0.123456789;item.format="percent";wait(20)
            compare(item.formattedValue,"12.345679%");compare(findChild(item,"bleeckerMetricValue"),label)
            fixtureSetup.setProcessLocale("de_DE");wait(20);compare(item.formattedValue,"12,345679 %")
            fixtureSetup.setProcessLocale("en_US");wait(20);compare(item.formattedValue,"12.345679%")
        }
        function test_measured_locale_profile_updates_existing_metric(){
            const item=createTemporaryObject(metric,root,{format:"currency",currencyCode:"JPY"});wait(20)
            const label=findChild(item,"bleeckerMetricValue")
            fixtureSetup.setProcessLocale("ja_JP");wait(20);compare(item.formattedValue,"¥1,235")
            item.format="number";item.value=NaN;fixtureSetup.setProcessLocale("ar_EG");wait(20)
            compare(item.formattedValue,"ليس رقمًا")
            fixtureSetup.setProcessLocale("es_CL");item.format="compact";item.value=999499999;wait(20)
            compare(item.formattedValue,"999 M")
            item.value=999500000;wait(20);compare(item.formattedValue,"1k M")
            item.value=999499000000;wait(20);compare(item.formattedValue,"999k M")
            item.value=999500000000;wait(20);compare(item.formattedValue,"1 B")
            compare(findChild(item,"bleeckerMetricValue"),label)
        }
        function test_delta_optional_zero_and_locale(){
            const item=createTemporaryObject(stat,root);wait(20);compare(item.formattedDelta,"+0 %");compare(item.presentationItem.height,105)
            item.delta=null;wait(20);compare(item.formattedDelta,"");compare(item.presentationItem.height,94)
            item.delta=-0.12;wait(20);compare(item.formattedDelta,"-12 %");compare(findChild(item,"bleeckerStatCardDelta").color,BleeckerTokens.colors.light.destructive)
            BleeckerTheme.dark=true;compare(findChild(item,"bleeckerStatCardDelta").color,BleeckerTokens.colors.light.destructive)
        }
        function test_platform_monospace_candidate_and_key_updates(){
            const item=createTemporaryObject(keyLabel,root);wait(20);verify(item.font.family.length>0);compare(item.font.family,BleeckerFonts.monospace)
            item.key="";wait(20);compare(item.presentationItem.width,12);compare(item.presentationItem.height,22)
            item.key="Control";item.maximumWidth=12;wait(20);compare(item.presentationItem.width,12);verify(item.presentationItem.height>22)
        }
    }
}
