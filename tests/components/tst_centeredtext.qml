import QtQuick
import QtTest
import Avelino
Item {
    id:root;width:640;height:400
    PixelAlignment {id:metrics;target:root}
    Component {id:factory;ButtonLabel {font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13);horizontalAlignment:Qt.AlignHCenter}}
    TestCase {
        name:"SourceCenteredText";when:windowShown
        function test_native_witnesses_data(){
            return nativeCenteredText.filter(row=>row.dpr===metrics.devicePixelRatio && row.probePngByteIdentical).map(row=>({tag:row.id,row:row}))
        }
        function test_native_witnesses(data){
            const row=data.row,item=createTemporaryObject(factory,root,{text:row.text,wrapWidth:row.offeredWidth})
            compare(item.width,row.componentSize.width);compare(item.height,row.componentSize.height)
            compare(item.linePositions.length,row.lines.length)
            for(let i=0;i<row.lines.length;i++)verify(Math.abs(item.linePositions[i].x-row.lines[i].x)<1e-9,"line "+i+" x "+item.linePositions[i].x+" source "+row.lines[i].x)
        }
        function test_alignment_updates_and_default(){
            const item=createTemporaryObject(factory,root,{text:"First line\nShort\nA longer final line",wrapWidth:116})
            const width=item.width,height=item.height
            item.horizontalAlignment=Qt.AlignLeft;compare(item.linePositions[0].x,0)
            item.horizontalAlignment=Qt.AlignHCenter;verify(item.linePositions[0].x>0)
            item.horizontalAlignment=Qt.AlignRight;verify(item.linePositions[0].x>30)
            compare(item.width,width);compare(item.height,height)
        }
    }
}
