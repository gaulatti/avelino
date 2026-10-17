import QtQuick

InheritedControl {
    id:scope
    default property alias content:host.data
    readonly property int partCount:host.count
    readonly property bool containsTextBaseline:host.containsTextBaseline
    readonly property SurfaceDecorator __surfaceDecorator:decorator
    function partAt(index:int):Item {return host.itemAt(index)}
    font.family:BleeckerFonts.monospace
    font.pointSize:BleeckerFonts.pointSizeForPixels(9)
    font.weight:Font.Bold
    palette.windowText:BleeckerTheme.palette.sea
    palette.disabled.windowText:BleeckerTheme.palette.sea
    padding:0;background:null;focusPolicy:Qt.NoFocus;hoverEnabled:false;wheelEnabled:false
    implicitWidth:host.implicitWidth;implicitHeight:host.implicitHeight;baselineOffset:host.baselineOffset
    BleeckerLayout.flattenChildren:false
    BleeckerLayout.minimumWidth:host.minimumWidth
    BleeckerLayout.idealWidth:host.naturalWidth
    BleeckerLayout.firstBaseline:containsTextBaseline ? baselineOffset:NaN
    Accessible.ignored:true
    contentItem:ProposalOverlay {
        id:host
        maximumWidth:scope.BleeckerLayout.proposedWidth
        BleeckerLayout.flattenChildren:true
    }
    SurfaceDecorator {
        id:decorator;target:host;textOnly:true
        delegate:Component {PillModifierPart {}}
    }
}
