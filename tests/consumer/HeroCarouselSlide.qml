import QtQuick
import QtQuick.Templates as T
import Avelino

InheritedControl {
    id:slide
    required property var slideData
    required property int slideIndex
    required property bool slideActive
    required property var fixture
    property int ordinal:0
    property string lifecycleKey:""
    readonly property string kind:fixture.definition.slot
    readonly property color slideColor:[BleeckerTheme.palette.sea,BleeckerTheme.palette.desert,BleeckerTheme.palette.terracotta,BleeckerTheme.palette.accentGold][slideData.color%4]
    FontMetrics {id:captionMetrics;font:slide.presentationFont}
    implicitWidth:kind==="fixed" ? slideData.width:kind==="text" ? label.naturalWidth:10
    implicitHeight:kind==="text" ? label.implicitHeight:slideData.height
    BleeckerLayout.minimumWidth:kind==="fixed" ? slideData.width:0
    BleeckerLayout.idealWidth:implicitWidth
    BleeckerLayout.fillsWidth:kind==="fill" ||kind==="button"
    padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus;Accessible.ignored:true
    MediaTileFill {anchors.fill:parent;color:slide.slideColor;visible:slide.kind==="fill" ||slide.kind==="fixed";Accessible.ignored:true}
    BleeckerText {
        id:label
        text:slide.kind==="text" ? slide.slideData.title:""
        visible:slide.kind==="text"
        font:slide.presentationFont;color:slide.resolvedTextColor
    }
    T.Button {
        objectName:"heroSlideButton"
        anchors.fill:parent;visible:slide.kind==="button";padding:0;background:null
        contentItem:MediaTileFill {
            color:slide.slideColor
            BleeckerText {
                id:caption;text:slide.slideData.title;font:slide.presentationFont;color:"white"
                anchors.centerIn:parent
                maximumLineCount:Math.max(1,Math.floor(slide.height/Math.max(1,captionMetrics.height)))
            }
        }
        Accessible.name:slide.slideData.title
        onClicked:slide.fixture.recordAction(slide.slideData.id)
    }
    BleeckerLayout.onProposalChanged:label.BleeckerLayout.propose(BleeckerLayout.proposedWidth)
    onWidthChanged:caption.BleeckerLayout.propose(width)
    onSlideActiveChanged:{
        if(slideActive){
            if(ordinal===0){lifecycleKey=fixture.keyFor(slideData.id);ordinal=fixture.newInstance(lifecycleKey)}
            fixture.appeared(lifecycleKey,ordinal)
        }else if(ordinal>0)fixture.disappeared(lifecycleKey,ordinal,slideData.id)
    }
}
