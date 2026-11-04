import QtQuick
import Avelino

Rectangle {
    id:fixture;width:600;height:300;color:BleeckerTheme.palette.background
    required property url fixtureRoot
    property var types:["text/plain"]
    property var results:[]
    property bool removeOnResult:false
    property bool visibleAtCallback:false
    property bool mounted:true
    property string title:"Choose file…"
    property real widthOffer:-1
    property real allocatedHeight:-1
    property real maximumHeight:-1
    property real textScale:1
    onTextScaleChanged:BleeckerTheme.textScale=textScale
    Component.onCompleted:BleeckerTheme.textScale=textScale
    Loader {
        active:fixture.mounted;anchors.centerIn:parent;anchors.alignWhenCentered:false
        sourceComponent:Component {
            BleeckerFileInput {
                objectName:"fileInput";title:fixture.title;allowedContentTypes:fixture.types;initialFolder:fixture.fixtureRoot
                widthOffer:fixture.widthOffer
                heightOffer:fixture.allocatedHeight
                maximumHeight:fixture.maximumHeight
                width:widthOffer<0 ? implicitWidth:widthOffer
                height:fixture.allocatedHeight<0 ? implicitHeight:fixture.allocatedHeight
                onResult:value=>{
                    fixture.visibleAtCallback=chooser.visible
                    fixture.results=fixture.results.concat([value])
                    if(fixture.removeOnResult)fixture.mounted=false
                }
            }
        }
    }
}
