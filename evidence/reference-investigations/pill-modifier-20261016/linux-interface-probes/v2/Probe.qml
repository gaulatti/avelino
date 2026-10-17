import QtQuick
import Avelino
Window {
 width:640;height:400;visible:true
 BleeckerFont {id:scope;objectName:"scope";family:"mono";size:9;weight:"bold";textScale:1;palette.windowText:"#2c5784"
  Text {objectName:"raw";text:"Ready"}
  BleeckerText {objectName:"mapped";text:"Ready"}
  Text {objectName:"rich";textFormat:Text.RichText;text:"<b>Ready</b> <i>now</i>"}
  Text {objectName:"richBound";font:scope.font;color:scope.palette.windowText;textFormat:Text.RichText;text:"<span style=\"font-family:'Encode Sans';font-size:17px;font-weight:400\">Status </span><b style=\"color:#ff3b30\">Ready</b>"}
  Text {objectName:"owned";text:"Ready";font.family:BleeckerFonts.primary;font.pointSize:BleeckerFonts.pointSizeForPixels(19);font.weight:Font.Normal;color:"red"}
 }
}
