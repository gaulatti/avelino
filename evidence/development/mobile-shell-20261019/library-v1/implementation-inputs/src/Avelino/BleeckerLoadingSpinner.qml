import QtQuick
import QtQuick.Templates as T
import "spinnerpresentation.js" as Presentation

T.BusyIndicator {
    id: spinner
    property string size: "md"
    property color color: BleeckerTheme.nativeSpinnerForeground
    readonly property int edge: BleeckerValueTools.spinnerEdge(size)
    readonly property int animationPhase: Math.min(23,Math.floor(clock.progress))
    readonly property Item visualItem: visual
    readonly property bool animating: animation.running
    implicitWidth: edge
    implicitHeight: implicitWidth
    padding: 0; background: null; focusPolicy: Qt.NoFocus
    Accessible.role: Accessible.ProgressBar
    Accessible.name: qsTr("Loading")
    QtObject {id:clock;objectName:"bleeckerSpinnerAnimation";property real progress:0}
    NumberAnimation {
        id:animation;target:clock;property:"progress";from:0;to:24
        duration:BleeckerTheme.nativeSpinnerDuration;loops:Animation.Infinite;easing.type:Easing.Linear
        running:spinner.running && spinner.visible && !BleeckerTheme.reducedMotion
        onRunningChanged:if(!running)clock.progress=0
    }
    contentItem:Item {
        visible:spinner.running
        Item {
            id:visual;objectName:"bleeckerSpinnerVisual"
            width:spinner.edge;height:width;anchors.centerIn:parent
            Repeater {
                model:8
                Item {
                    required property int index
                    width:visual.width;height:visual.height
                    rotation:index*45
                    Rectangle {
                        objectName:"bleeckerSpinnerSpoke"+parent.index
                        width:visual.width/8;height:visual.height*5/16;radius:width/2
                        x:(visual.width-width)/2;y:0
                        color:spinner.color
                        opacity:Presentation.levels[spinner.animationPhase][parent.index]/255
                        antialiasing:true
                        Accessible.ignored:true
                    }
                }
            }
        }
    }
}
