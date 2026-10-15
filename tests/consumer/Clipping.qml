import QtQuick
import QtQuick.Shapes
import Avelino

Window {
    id: root
    width: 840; height: 560; visible: true
    title: "Avelino — generic content clipping"
    color: "#123456"
    property int actions: 0
    property bool sourcePresent: true
    property real maskRadius: 24
    property color liveColor: "red"
    property bool sparseSource: false
    Component.onCompleted: {
        BleeckerTheme.dark=captureDark
        BleeckerTheme.textScale=captureTextScale
        BleeckerTheme.reducedMotion=true
        chipInk.createObject(chip.contentItem.content[0].parent)
    }
    Repeater {
        model: 21
        Rectangle {
            required property int index
            x:index*40; width:20; height:root.height; color:"#234567"
        }
    }
    Text { x:24;y:18;text:"Generic content clipping";font.family:BleeckerTheme.primaryFont;font.pixelSize:18;color:"white" }
    BleeckerCard {
        objectName:"clipCard";x:24;y:60;width:220;height:150;paddingSize:"none";variant:"transparent"
        Rectangle {x:-30;y:-30;width:280;height:210;color:"#c03434"}
        BleeckerButton {objectName:"clipButton";x:30;y:36;text:"Live control";onClicked:root.actions++}
        BleeckerTextField {objectName:"clipField";x:30;y:90;width:160;placeholderText:"Editable content"}
    }
    Component {
        id: alertSlot
        Item {
            implicitWidth:160;implicitHeight:90
            Rectangle {x:-160;y:-160;width:500;height:500;color:"#3445c0"}
        }
    }
    BleeckerAlert {objectName:"clipAlert";x:280;y:60;title:"Circular outline";content:alertSlot}
    Component {id:chipInk;Rectangle {x:-100;y:-100;width:400;height:400;color:"#34c045"}}
    BleeckerFilterChip {id:chip;objectName:"clipChip";x:580;y:60;text:"Capsule overflow"}
    BleeckerCard {
        x:580;y:120;width:180;height:90;paddingSize:"none";variant:"transparent";opacity:0.5
        Rectangle {anchors.fill:parent;color:"red"}
        BleeckerCard {
            x:50;y:20;width:90;height:50;paddingSize:"none";variant:"transparent"
            Rectangle {x:-40;y:-40;width:180;height:130;color:"blue"}
        }
    }
    Item {
        id: raw;objectName:"clipLifecycle";x:24;y:270;width:220;height:150;clip:true
        readonly property bool software:GraphicsInfo.api===GraphicsInfo.Software
        Item {
            id: rawContent;anchors.fill:parent;visible:root.sourcePresent
            Rectangle {
                x:root.sparseSource ? 40:0;y:root.sparseSource ? 40:0
                width:parent.width-x*2;height:parent.height-y*2;color:root.liveColor
            }
            Rectangle {x:12;y:12;width:20;height:20;color:"yellow"}
        }
        ShaderEffectSource {
            id: layer;sourceItem:root.sourcePresent ? rawContent:null
            sourceRect:Qt.rect(0,0,raw.width,raw.height);hideSource:true;visible:false
            textureMirroring:raw.software ? ShaderEffectSource.NoMirroring:ShaderEffectSource.MirrorVertically
        }
        SoftwareContentMask {anchors.fill:parent;visible:raw.software;source:layer;outline:rawPath}
        Shape {
            anchors.fill:parent;preferredRendererType:Shape.CurveRenderer;antialiasing:true
            ShapePath {
                id:rawPath;fillColor:"transparent";strokeColor:"transparent";strokeWidth:-1
                fillItem:raw.software ? null:layer
                PathRectangle {width:raw.width;height:raw.height;radius:root.maskRadius}
            }
        }
    }
    Text {x:280;y:280;width:480;wrapMode:Text.WordWrap;font.family:BleeckerTheme.primaryFont;font.pixelSize:16;color:"white"
        text:"Continuous, circular and capsule outlines; nested translucent content; live source and outline changes; real input controls."}
}
