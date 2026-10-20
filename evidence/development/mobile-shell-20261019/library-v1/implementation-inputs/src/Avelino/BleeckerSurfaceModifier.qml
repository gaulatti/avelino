pragma FunctionSignatureBehavior: Enforced
import QtQuick

ProposalOverlay {
    id:modifier
    property real radius:BleeckerTokens.radii.card
    readonly property int partCount:count
    readonly property SurfaceDecorator __surfaceDecorator:decorator
    function partAt(index:int):Item {return itemAt(index)}
    function validate():void {
        if(!Number.isFinite(radius))throw new Error("BleeckerSurfaceModifier radius must be finite")
    }
    BleeckerLayout.flattenChildren:true
    BleeckerLayout.minimumWidth:minimumWidth
    BleeckerLayout.idealWidth:naturalWidth
    BleeckerLayout.firstBaseline:containsTextBaseline ? baselineOffset:NaN
    maximumWidth:BleeckerLayout.proposedWidth
    Component.onCompleted:validate()
    onRadiusChanged:validate()
    SurfaceDecorator {
        id:decorator
        target:modifier
        delegate:Component {SurfaceModifierPart {radius:modifier.radius}}
    }
}
