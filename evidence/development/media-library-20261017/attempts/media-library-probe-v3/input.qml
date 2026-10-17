import QtQuick
import QtQuick.Window
import QtTest
import Avelino
TestCase {
 id:t;name:"MediaProbe";when:windowShown;width:700;height:450
 Item{id:scene;anchors.fill:parent}
 Component{id:library;BleeckerMediaLibrary{width:460;items:[{id:"a",height:20}];tile:Component{Rectangle{implicitWidth:10;implicitHeight:20;BleeckerLayout.fillsWidth:true}}}}
 function test_probe(){
  const a=createTemporaryObject(library,scene)
  wait(40)
  console.log("LITERAL",a.itemCount,a.instantiatedCount,a.activeCount,a.width,a.height,a.visible,scene.visible,t.visible,scene.Window.window.width,scene.Window.window.height,JSON.stringify(a.layoutSnapshot()))
  a.items=[{id:"a",height:20},{id:"b",height:40}];a.layout();wait(40)
  console.log("ARRAY",a.itemCount,a.instantiatedCount,a.activeCount,JSON.stringify(a.layoutSnapshot()))
  t.visible=true;wait(40);a.layout()
  console.log("VISIBLE",a.itemCount,a.instantiatedCount,a.activeCount,JSON.stringify(a.layoutSnapshot()))
 }
}