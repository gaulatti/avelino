import QtQuick
import QtTest
import Avelino
import "../../../tests/consumer" as Fixtures
Item {
    id:root;width:900;height:820
    PixelAlignment {id:metrics;target:root}
    Component {id:labelFactory;ButtonLabel {text:"Ag09 é.—"}}
    Component {id:factory;Fixtures.NavigationCase {}}
    TestCase {
        name:"NavigationMetricMatrix";when:windowShown
        function test_owned_faces(){
            let changed=[],count=0
            for(const family of ["Encode Sans","Libre Franklin"])for(const weight of [100,200,300,400,500,600,700,800,900])for(const pixels of [0.1,0.5,1,9,13,25,48.5,101]){
                const item=createTemporaryObject(labelFactory,root)
                item.font.family=family;item.font.weight=weight;item.font.pointSize=BleeckerFonts.pointSizeForPixels(pixels)
                const before=[item.unwrappedWidth,item.naturalHeight,item.baselineOffset]
                item.font.preferTypoLineMetrics=true
                const after=[item.unwrappedWidth,item.naturalHeight,item.baselineOffset]
                if(JSON.stringify(before)!==JSON.stringify(after))changed.push({family:family,weight:weight,pixels:pixels,before:before,after:after})
                count++;item.destroy()
            }
            console.info("OWNED_FONT_METRICS",JSON.stringify({count:count,changes:changed,dpr:metrics.devicePixelRatio}))
        }
        function preferSourceMetrics(item){
            if(item.font!==undefined &&item.naturalHeight!==undefined &&["Encode Sans","Libre Franklin"].indexOf(item.font.family)>=0)item.font.preferTypoLineMetrics=true
            for(const child of item.children)preferSourceMetrics(child)
        }
        function test_native_navigation(){
            const rows=nativeNavigationCaptures.filter(c=>c.api!=="BleeckerButton"&&c.dpr===metrics.devicePixelRatio)
            for(const row of rows){
                BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
                const item=createTemporaryObject(factory,root,{definition:row});wait(30)
                preferSourceMetrics(item);wait(30)
                compare(item.presentationItem.implicitWidth,row.componentSize.width,"Source width "+row.path)
                compare(item.presentationItem.implicitHeight,row.componentSize.height,"Source height "+row.path)
                item.destroy()
            }
            console.info("NATIVE_NAVIGATION_METRICS",JSON.stringify({count:rows.length,dpr:metrics.devicePixelRatio}))
        }
    }
}
