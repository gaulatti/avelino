import QtQuick
import QtQuick.Templates as T
import Avelino

InheritedControl {
    id:tile
    required property var tileData
    required property int tileIndex
    required property bool tileActive
    required property var fixture
    property int ordinal:0
    property string lifecycleKey:""
    readonly property string kind:fixture.definition.slot
    readonly property color tileColor:[BleeckerTheme.palette.sea,BleeckerTheme.palette.desert,BleeckerTheme.palette.terracotta,BleeckerTheme.palette.accentGold][tileData.color%4]
    FontMetrics {id:captionMetrics;font:tile.presentationFont}
    implicitWidth:kind==="fixed" ? tileData.width:kind==="text" ? label.naturalWidth:10
    implicitHeight:kind==="text" ? label.implicitHeight:tileData.height
    BleeckerLayout.minimumWidth:kind==="fixed" ? tileData.width:0
    BleeckerLayout.idealWidth:implicitWidth
    BleeckerLayout.fillsWidth:kind==="fill" ||kind==="button"
    padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus;Accessible.ignored:true
    MediaTileFill {anchors.fill:parent;color:tile.tileColor;visible:tile.kind==="fill" ||tile.kind==="fixed";Accessible.ignored:true}
    BleeckerText {
        id:label
        text:tile.kind==="text" ? tile.tileData.title:""
        visible:tile.kind==="text"
        font:tile.presentationFont;color:tile.resolvedTextColor
    }
    T.Button {
        objectName:"mediaTileButton"
        anchors.fill:parent;visible:tile.kind==="button";padding:0;background:null
        contentItem:MediaTileFill {
            color:tile.tileColor
            BleeckerText {
                id:caption;text:tile.tileData.title;font:tile.presentationFont;color:"white"
                anchors.centerIn:parent
                maximumLineCount:Math.max(1,Math.floor(tile.height/Math.max(1,captionMetrics.height)))
            }
        }
        Accessible.name:tile.tileData.title
        onClicked:tile.fixture.recordAction(tile.tileData.id)
    }
    BleeckerLayout.onProposalChanged:label.BleeckerLayout.propose(BleeckerLayout.proposedWidth)
    onWidthChanged:caption.BleeckerLayout.propose(width)
    onTileActiveChanged:{
        if(tileActive){
            if(ordinal===0){lifecycleKey=fixture.keyFor(tileData.id);ordinal=fixture.newInstance(lifecycleKey)}
            fixture.appeared(lifecycleKey,ordinal)
        }else if(ordinal>0)fixture.disappeared(lifecycleKey,ordinal,tileData.id)
    }
}
