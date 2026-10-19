import QtQuick
import QtTest
import Avelino
import "../../../tests/consumer" as Fixtures
Item {
    id:root;width:900;height:820
    Component {id:factory;Fixtures.NavigationCase {}}
    TestCase {
        name:"NavigationFontMetricProbe";when:windowShown
        function test_typographic_metrics(){
            BleeckerTheme.dark=false;BleeckerTheme.textScale=1
            const row=nativeNavigationCaptures.find(c=>c.path==="page-header-unicode-light-text1.0-offscreen-dpr1.0.png")
            verify(row)
            const item=createTemporaryObject(factory,root,{definition:row});wait(30)
            function metrics(){return ["Eyebrow","Title","Description"].map(name=>{const label=findChild(item,"bleeckerPageHeader"+name);return {name:name,text:label.text,family:label.font.family,pixels:label.font.pixelSize,preferTypo:label.font.preferTypoLineMetrics,height:label.naturalHeight,baseline:label.baselineOffset}})}
            console.info("FONT_METRIC_BEFORE",JSON.stringify({body:item.presentationItem.implicitHeight,labels:metrics()}))
            const title=findChild(item,"bleeckerPageHeaderTitle");title.font.preferTypoLineMetrics=true;wait(30)
            console.info("FONT_METRIC_AFTER",JSON.stringify({body:item.presentationItem.implicitHeight,labels:metrics()}))
        }
    }
}
