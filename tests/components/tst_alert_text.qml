import QtQuick
import QtTest
import Avelino
Item {
    id:root;width:500;height:300
    PixelAlignment {id:metrics;target:root}
    Component {id:labelFactory;ButtonLabel {property real sourceSize:13;property int sourceWeight:Font.Normal;property bool primary:false;font.family:primary ? BleeckerTheme.primaryFont:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(sourceSize);font.weight:sourceWeight}}
    TestCase {
        name:"NativeProseWrapping";when:windowShown
        function test_boundaries_data(){return nativeProseBoundaries.filter(c=>c.dpr===metrics.devicePixelRatio).map(c=>({tag:c.sourcePath,row:c}))}
        function test_boundaries(data){
            const row=data.row
            const item=createTemporaryObject(labelFactory,root,{text:row.text,wrapWidth:row.offeredWidth,sourceSize:row.size,sourceWeight:row.weight==="medium" ? Font.Medium:Font.DemiBold,primary:row.primary})
            compare(item.implicitWidth,row.componentWidth);compare(item.implicitHeight,row.componentHeight);compare(item.linePositions.length,row.lines.length)
        }
        function test_source_data(){return nativeAlertTextCases.filter(c=>c.dpr===metrics.devicePixelRatio).map((c,i)=>({tag:c.path,row:c}))}
        function test_source(data){
            const row=data.row
            verify(row.probeByteIdentical)
            const item=createTemporaryObject(labelFactory,root,{text:row.text,wrapWidth:row.offeredWidth,sourceSize:row.size,sourceWeight:row.weight==="semibold" ? Font.DemiBold:Font.Normal})
            compare(item.implicitWidth,row.componentWidth);compare(item.implicitHeight,row.componentHeight)
            compare(item.linePositions.length,row.lines.length)
        }
    }
}
