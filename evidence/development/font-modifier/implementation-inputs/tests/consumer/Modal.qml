import QtQuick
import Avelino

Window {
    id:window;width:1100;height:850;visible:true;title:"Avelino modal content and presentation"
    color:BleeckerTheme.palette.background
    property var model:({fixture:"gallery",title:"Edit edition",modalWidth:480,outerOffer:null,content:"counter",disabled:false,rtl:false,parentFont:0,parentRed:false,width:520,height:260})
    property string edition:"Draft edition"
    property string sheetMode:"counter"
    property var sheetCalls:[]
    property int sheetAppears:0
    property int sheetDestroyed:0
    property int sheetDismissals:0
    property var sheetMountValues:[]
    property bool sheetDisabled:false
    property var sourceWindow:null
    property bool primaryVisible:true
    property bool secondaryVisible:true
    property bool emptyVisible:true
    property bool multipleVisible:true
    readonly property Item primaryFixture:primary
    readonly property Item primaryControl:primary.control
    readonly property var presentedDialog:sheet
    Component.onCompleted:{
        BleeckerTheme.dark=typeof consumerDark!=="undefined" ? consumerDark:captureDark
        BleeckerTheme.textScale=typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
        BleeckerTheme.reducedMotion=true
    }
    function configure(values){model=Object.assign({},model,values)}
    function setTextScale(value){BleeckerTheme.textScale=value}
    function openSheet(mode){if(mode!=="counter" && mode!=="editor")throw new Error("Unknown sheet content");sheetMode=mode;sheet.open()}
    function openSourceWindow(configuration){
        if(sourceWindow)sourceWindow.destroy()
        sourceWindow=sourceWindowFactory.createObject(window,{model:configuration})
        if(!sourceWindow)throw new Error("Source presentation could not be created")
    }
    BleeckerButton {objectName:"modalBefore";x:24;y:16;text:"Previous";size:"xs"}
    BleeckerButton {objectName:"modalOpenCounter";x:120;y:16;text:"Open counter sheet";variant:"secondary";size:"xs";onClicked:window.openSheet("counter")}
    BleeckerButton {objectName:"modalOpenEditor";x:300;y:16;text:"Open edition sheet";variant:"secondary";size:"xs";onClicked:window.openSheet("editor")}
    BleeckerButton {objectName:"modalAfter";x:480;y:16;text:"Continue";size:"xs"}
    Text {x:44;y:80;text:"Caller-owned state";font.family:BleeckerTheme.primaryFont;font.pixelSize:14;color:BleeckerTheme.palette.textSecondary}
    ModalCase {
        id:primary;objectName:"consumerModal";x:24;y:100;definition:window.model;mounted:window.primaryVisible
        onDismissalRequested:window.primaryVisible=false
    }
    BleeckerButton {x:44;y:210;text:"Restore example";variant:"secondary";visible:!window.primaryVisible;onClicked:window.primaryVisible=true}
    Text {x:590;y:80;text:"Controlled edition binding";font.family:BleeckerTheme.primaryFont;font.pixelSize:14;color:BleeckerTheme.palette.textSecondary}
    BleeckerModal {
        objectName:"modalEditorPreview";x:590;y:154;modalWidth:460;title:"Delivery settings";visible:window.secondaryVisible
        dismissAction:function(){window.secondaryVisible=false}
        BleeckerTextField {
            objectName:"modalPreviewField";placeholderText:"Edition name";text:window.edition;onTextEdited:window.edition=text
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:implicitWidth;BleeckerLayout.fillsWidth:true
        }
    }
    BleeckerButton {x:590;y:210;text:"Restore example";variant:"secondary";visible:!window.secondaryVisible;onClicked:window.secondaryVisible=true}
    Text {x:44;y:390;text:"Empty caller content";font.family:BleeckerTheme.primaryFont;font.pixelSize:14;color:BleeckerTheme.palette.textSecondary}
    BleeckerModal {x:44;y:425;modalWidth:480;title:"No additional content";visible:window.emptyVisible;dismissAction:function(){window.emptyVisible=false}}
    BleeckerButton {x:44;y:450;text:"Restore example";variant:"secondary";visible:!window.emptyVisible;onClicked:window.emptyVisible=true}
    Text {x:590;y:390;text:"Each caller child receives padding";font.family:BleeckerTheme.primaryFont;font.pixelSize:14;color:BleeckerTheme.palette.textSecondary}
    BleeckerModal {
        x:590;y:425;modalWidth:460;title:"Two caller children";visible:window.multipleVisible;dismissAction:function(){window.multipleVisible=false}
        ButtonLabel {
            text:"First child";font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13)
            color:BleeckerTheme.nativeTextPrimary;wrapWidth:BleeckerLayout.proposedWidth
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:unwrappedWidth
        }
        Rectangle {implicitWidth:72;implicitHeight:44;color:BleeckerTheme.alpha(BleeckerTokens.colors.light.sea,0.18)}
    }
    BleeckerButton {x:590;y:450;text:"Restore example";variant:"secondary";visible:!window.multipleVisible;onClicked:window.multipleVisible=true}
    Text {
        x:44;y:750;width:1000
        text:"Open a sheet, change its content, close it, and reopen it. Counter state starts fresh; the edition binding stays with this window."
        wrapMode:Text.WordWrap;font.family:BleeckerTheme.secondaryFont;font.pixelSize:13;color:BleeckerTheme.palette.textSecondary
    }
    BleeckerModalDialog {
        id:sheet;objectName:"consumerModalDialog";title:"Edit edition";modalWidth:480
        enabled:!window.sheetDisabled
        x:(window.width-width)/2;y:(window.height-height)/2
        content:window.sheetMode==="counter" ? sheetCounter:sheetEditor
        onClosed:window.sheetDismissals++
    }
    Component {
        id:sheetCounter
        BleeckerButton {
            objectName:"modalSheetCounter";property int value:0;text:"Count "+value;variant:"secondary";size:"sm"
            onClicked:{value++;window.sheetCalls=window.sheetCalls.concat(["counter:"+value])}
            Component.onCompleted:{window.sheetAppears++;window.sheetMountValues=window.sheetMountValues.concat([value])}
            Component.onDestruction:if(window)window.sheetDestroyed++
        }
    }
    Component {
        id:sheetEditor
        BleeckerTextField {
            objectName:"modalSheetEditor";placeholderText:"Edition name";text:window.edition;onTextEdited:window.edition=text
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:implicitWidth;BleeckerLayout.fillsWidth:true
        }
    }
    Component {
        id:sourceWindowFactory
        Window {
            id:source;required property var model
            width:model.width;height:model.height;visible:true;color:BleeckerTheme.palette.background
            title:"Modal source workflow"
            readonly property Item fixture:sourceCase
            readonly property Item control:sourceCase.control
            function configure(values){model=Object.assign({},model,values)}
            ModalCase {
                id:sourceCase;definition:source.model
                onDismissalRequested:source.close()
            }
        }
    }
}
