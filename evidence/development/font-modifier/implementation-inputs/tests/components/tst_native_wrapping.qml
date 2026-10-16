import QtQuick
import QtTest
import Avelino
Item {
 id:root;width:500;height:260
 PixelAlignment {id:metrics;target:root}
 Component {id:labelFactory;ButtonLabel {font.family:BleeckerFonts.primary;font.pointSize:BleeckerFonts.pointSizeForPixels(12)}}
 TestCase {
  name:"NativeTextWrapping";when:windowShown
  function test_metrics_data(){return nativeWrapping.filter(row=>row.dpr===metrics.devicePixelRatio).map(row=>Object.assign({tag:row.path},row))}
  function test_metrics(data){
   const label=createTemporaryObject(labelFactory,root,{text:data.text,wrapWidth:data.offeredWidth})
   compare(label.implicitWidth,data.width,"source text width")
   compare(label.naturalHeight,data.height,"source text height")
   compare(label.baselineOffset,data.baseline,"source baseline")
  }
 }
}
