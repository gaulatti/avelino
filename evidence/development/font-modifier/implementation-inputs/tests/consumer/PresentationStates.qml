import QtQuick
import Avelino
Window {
    id:window
    property string heading:"No editions yet"
    property string message:"Create an edition to get started."
    property bool emptyPresent:true
    property bool loading:false
    property int created:0
    property int destroyed:0
    property int actions:0
    property int underlying:0
    property int outside:0
    width:840;height:560;visible:true
    color:BleeckerTheme.palette.background;title:"Avelino installed presentation states"
    Component.onCompleted:{BleeckerTheme.dark=consumerDark;BleeckerTheme.textScale=consumerTextScale;BleeckerTheme.reducedMotion=true}
    Component {
        id:emptyFactory
        BleeckerEmptyState {
            objectName:"emptyState";width:parent.width
            title:window.heading;message:window.message
            actions:Component {
                BleeckerButton {
                    objectName:"emptyStateAction";property int count:0
                    text:"Create "+count;maximumWidth:parent.availableWidth
                    onClicked:{count++;window.actions++}
                    Component.onCompleted:window.created++
                    Component.onDestruction:window.destroyed++
                }
            }
        }
    }
    BleeckerEyebrow {x:24;y:24;text:"Presentation states"}
    Loader {x:24;y:64;width:360;sourceComponent:emptyFactory;active:window.emptyPresent}
    BleeckerErrorState {
        id:error;objectName:"errorState";x:432;y:64;width:360
        message:"Check the connection and try again."
        actions:Component {
            BleeckerButton {objectName:"errorStateAction";property int count:0;text:"Retry "+count;maximumWidth:parent.availableWidth;onClicked:count++}
        }
    }
    Item {
        x:24;y:340;width:360;height:180
        BleeckerButton {objectName:"underlyingAction";anchors.centerIn:parent;text:"Underlying action";onClicked:window.underlying++}
        BleeckerLoadingOverlay {objectName:"loadingOverlay";anchors.fill:parent;visible:window.loading;message:"Preparing editions"}
    }
    BleeckerButton {objectName:"outsideAction";x:432;y:340;text:"Outside action";onClicked:window.outside++}
    BleeckerTextField {objectName:"presentationOutsideField";x:432;y:412;width:330;placeholderText:"Continue editing here"}
}
