import QtQuick
Rectangle {
    width:120;height:120;color:"#123456"
    Item {
        id:content;width:100;height:100
        Rectangle {objectName:"ink";x:20;y:20;width:60;height:60;color:"red"}
    }
    ShaderEffectSource {
        x:10;y:10;width:100;height:100
        sourceItem:content;sourceRect:Qt.rect(0,0,100,100);hideSource:true
        textureMirroring:ShaderEffectSource.NoMirroring
    }
}
