import QtQuick

InheritedControl {
    id:label
    property alias text:renderer.text
    property color color:resolvedTextColor
    property real tracking:0
    property int horizontalAlignment:mirrored ? Qt.AlignRight:Qt.AlignLeft
    readonly property bool containsTextBaseline:true
    readonly property real offeredWidth:BleeckerLayout.proposedWidth
    readonly property Item textRenderer:renderer
    defaultTextColor:BleeckerTheme.nativeTextPrimary
    BleeckerLayout.minimumWidth:0
    BleeckerLayout.idealWidth:renderer.unwrappedWidth
    BleeckerLayout.firstBaseline:baselineOffset
    implicitWidth:offeredWidth<0 ? renderer.implicitWidth
        :Math.ceil(Math.min(renderer.implicitWidth,offeredWidth)*alignment.devicePixelRatio)/alignment.devicePixelRatio
    implicitHeight:Math.ceil(renderer.naturalHeight*alignment.devicePixelRatio)/alignment.devicePixelRatio
    baselineOffset:renderer.baselineOffset
    padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus;hoverEnabled:false;wheelEnabled:false
    ButtonLabel {
        id:renderer
        font:label.presentationFont;color:label.color;tracking:label.tracking
        wrapWidth:label.offeredWidth;horizontalAlignment:label.horizontalAlignment
        width:Math.max(label.width,implicitWidth);height:label.height
        PixelAlignment {id:alignment;target:label;origin:Qt.point(0,renderer.baselineOffset)}
        transform:Translate {x:alignment.offset.x;y:alignment.offset.y}
        Accessible.ignored:true
    }
    Accessible.role:Accessible.StaticText
    Accessible.name:text
}
