import QtQuick
import Avelino

Window {
    id:window
    readonly property bool gallery:typeof consumerDark==="undefined"
    width:gallery ? 1120:600;height:gallery ? 720:300
    visible:true;title:"Avelino file input";color:BleeckerTheme.palette.background
    property var configuration:({id:"default",types:["public.plain-text"],disabled:false,rtl:false,parentFont:false,parentRed:false,controlSize:"regular"})
    property var linuxContentTypes:["text/plain"]
    property url fixtureFolder:typeof fileInputFolder==="undefined" ? "":fileInputFolder
    readonly property Item primaryFixture:fixture
    function configure(value,types):void {
        configuration=Object.assign({},value);linuxContentTypes=types
        fixture.mounted=true;fixture.results=[];fixture.visibleAtCallback=false
    }
    function update(value):void {configuration=Object.assign({},configuration,value)}
    function environment(dark,scale):void {BleeckerTheme.dark=dark;BleeckerTheme.textScale=scale}
    Component.onCompleted:{BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=gallery ? captureDark:consumerDark;BleeckerTheme.textScale=gallery ? captureTextScale:consumerTextScale}
    ProposalRow {
        x:24;y:24;visible:window.gallery;spacing:8
        Repeater {
            model:[{title:"Text",types:["text/plain"],sourceTypes:["public.plain-text"]},
                {title:"Images",types:["image/*"],sourceTypes:["public.image"]},
                {title:"Folders",types:["inode/directory"],sourceTypes:["public.folder"]},
                {title:"Text + images",types:["text/plain","image/*"],sourceTypes:["public.plain-text","public.image"]},
                {title:"Folders + text",types:["inode/directory","text/plain"],sourceTypes:["public.folder","public.plain-text"]},
                {title:"All files",types:["*/*"],sourceTypes:["public.item"]},{title:"Empty types",types:[],sourceTypes:[]},
                {title:"Undeclared",types:[{identifier:"org.avelino.fixture",filenameExtensions:[]}],sourceTypes:["org.avelino.fixture"]}]
            BleeckerButton {
                required property var modelData;required property int index
                text:modelData.title;size:"xs";objectName:"fileInputOperator-"+index
                onClicked:{window.update({types:modelData.sourceTypes});window.linuxContentTypes=modelData.types}
            }
        }
    }
    ProposalRow {
        x:24;y:80;visible:window.gallery;spacing:8
        BleeckerButton {text:"Change title";size:"xs";objectName:"fileInputOperator-title";onClicked:window.update({title:window.configuration.title===undefined ? "Import documents":undefined})}
        BleeckerButton {text:"Disabled";size:"xs";objectName:"fileInputOperator-disabled";onClicked:window.update({disabled:!window.configuration.disabled})}
        BleeckerButton {text:"RTL";size:"xs";objectName:"fileInputOperator-rtl";onClicked:window.update({rtl:!window.configuration.rtl})}
        BleeckerButton {text:"Remove in callback";size:"xs";objectName:"fileInputOperator-remove";onClicked:fixture.removeOnResult=!fixture.removeOnResult}
        BleeckerButton {text:"Remount";size:"xs";objectName:"fileInputOperator-remount";onClicked:fixture.mounted=true}
        BleeckerButton {text:"Theme";size:"xs";objectName:"fileInputOperator-theme";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
        BleeckerButton {text:"Text scale";size:"xs";objectName:"fileInputOperator-scale";onClicked:BleeckerTheme.textScale=BleeckerTheme.textScale===1 ? 1.5:1}
    }
    FileInputCase {
        id:fixture;y:window.gallery ? 180:0
        configuration:window.configuration;linuxContentTypes:window.linuxContentTypes;fixtureFolder:window.fixtureFolder
    }
    BleeckerText {
        x:650;y:230;width:430;visible:window.gallery
        text:fixture.results.length ? "Selected URLs: "+fixture.results.map(value=>value.urls.join(", ")).join(" → ")
            :"Choose files to deliver their URLs to the owner. Cancel leaves the result unchanged."
        color:BleeckerTheme.palette.textSecondary;font.pixelSize:16
    }
}
