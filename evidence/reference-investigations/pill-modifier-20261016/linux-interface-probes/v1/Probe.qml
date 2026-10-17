import QtQuick
import Avelino
Window {
 width:640;height:400;visible:true
 BleeckerFont {objectName:"scope";family:"mono";size:9;weight:"bold";textScale:1;defaultTextColor:"#2c5784"
  Text {objectName:"raw";text:"Ready"}
  BleeckerText {objectName:"mapped";text:"Ready"}
  Text {objectName:"rich";textFormat:Text.RichText;text:"<b>Ready</b> <i>now</i>"}
  Text {objectName:"owned";text:"Ready";font.family:BleeckerFonts.primary;font.pointSize:BleeckerFonts.pointSizeForPixels(19);font.weight:Font.Normal;color:"red"}
 }
}
