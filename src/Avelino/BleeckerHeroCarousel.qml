import QtQuick

ListView {
    id:control
    property var items:[]
    property var itemIdentity:null
    required property Component slide
    readonly property alias presenter:slides
    readonly property real documentWidth:slides.documentWidth
    readonly property real naturalHeight:slides.naturalHeight
    readonly property int instantiatedCount:slides.instantiatedCount
    readonly property int activeCount:slides.activeCount
    readonly property int itemCount:slides.itemCount
    function slideAt(index){return slides.itemAt(index)}
    function layoutSnapshot(){return slides.layoutSnapshot()}

    orientation:ListView.Horizontal
    spacing:16
    clip:true
    interactive:enabled
    keyNavigationEnabled:false
    snapMode:ListView.SnapOneItem
    highlightRangeMode:ListView.NoHighlightRange
    model:slides.itemCount
    implicitWidth:0
    implicitHeight:slides.naturalHeight
    BleeckerLayout.minimumWidth:0
    BleeckerLayout.idealWidth:slides.documentWidth
    BleeckerLayout.fillsWidth:true
    LayoutMirroring.childrenInherit:true
    Accessible.role:Accessible.List

    // These transparent targets give Qt its input, velocity and snapping model.
    // Caller objects belong to the presenter, including while outside the view.
    delegate:Item {
        width:control.width;height:control.height
        Accessible.ignored:true
    }
    HeroCarouselBase {
        id:slides
        parent:control.contentItem
        x:mirrored ? -documentWidth:0
        width:control.width;height:control.height
        viewport:control
        items:control.items;itemIdentity:control.itemIdentity;slide:control.slide
        mirrored:control.effectiveLayoutDirection===Qt.RightToLeft
        z:1
    }
}
