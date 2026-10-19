import QtQuick
import Avelino
Window {
 id:window
 width:320;height:180;visible:true
 color:BleeckerTheme.palette.background
 readonly property int preference:Number(argument("--hint"))
 function argument(name){const at=Qt.application.arguments.indexOf(name);if(at<0)throw new Error("Missing "+name);return Qt.application.arguments[at+1]}
 Rectangle {anchors.fill:parent;color:window.color}
 BleeckerButtonGroup {
  id:group;x:(parent.width-width)/2;y:(parent.height-height)/2
  BleeckerButton {objectName:"first";text:"Short";size:"xs";font.hintingPreference:window.preference}
  BleeckerButton {objectName:"second";text:"Tall";size:"lg";font.hintingPreference:window.preference}
 }
 function find(item,name){if(item.objectName===name)return item;for(const child of item.children){const f=find(child,name);if(f)return f}return null}
 function frame(item){const p=item.mapToItem(window.contentItem,0,0);return {x:p.x,y:p.y,width:item.width,height:item.height}}
 function records(){const result={component:frame(group.presentationItem),labels:[]};for(const name of ["first","second"]){const item=find(group,name),label=find(item,"bleeckerButtonLabel");result[name]=frame(item);result.labels.push({name:name,text:label.text,family:label.resolvedFamily,style:label.resolvedStyle,weight:label.font.weight,hint:label.font.hintingPreference,logicalSize:label.logicalPixelSize,resolvedSize:label.resolvedPixelSize,glyphAdvance:label.glyphAdvance,frame:frame(label)})}return result}
 Component.onCompleted:{BleeckerTheme.dark=Qt.application.arguments.indexOf("--dark")>=0;BleeckerTheme.textScale=Number(argument("--scale"));BleeckerTheme.reducedMotion=true}
 Timer {interval:700;running:true;onTriggered:{console.log("GLYPH_HINT "+JSON.stringify(window.records()));window.contentItem.grabToImage(function(result){Qt.exit(result.saveToFile(window.argument("--output"))?0:1)})}}
}