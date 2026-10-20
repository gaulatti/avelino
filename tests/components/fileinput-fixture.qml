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
    Loader {
        active:fixture.mounted;anchors.centerIn:parent
        sourceComponent:Component {
            BleeckerFileInput {
                objectName:"fileInput";title:fixture.title;allowedContentTypes:fixture.types;initialFolder:fixture.fixtureRoot
                onResult:value=>{
                    fixture.visibleAtCallback=chooser.visible
                    fixture.results=fixture.results.concat([value])
                    if(fixture.removeOnResult)fixture.mounted=false
                }
            }
        }
    }
}
