import QtQuick
import QtQuick.Templates as T
import Avelino

Window {
    id:window;width:1040;height:760;visible:true;title:"Avelino caller button styles"
    color:BleeckerTheme.palette.background
    property var model:({fixture:"gallery",variant:"primary",size:"md",content:"counter",text:"Review",offer:null,
        disabled:false,rtl:false,parentFont:0,parentRed:false,destructiveRole:false,parentLayout:"zstack",width:640,height:400})
    readonly property ButtonStyleCase primaryFixture:primary
    property Item primaryPreview:null
    function configure(values){model=Object.assign({},model,values)}
    Component.onCompleted:{
        BleeckerTheme.reducedMotion=true
        BleeckerTheme.dark=typeof consumerDark!=="undefined" ? consumerDark:captureDark
        BleeckerTheme.textScale=typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
    }
    ProposalRow {
        x:24;y:24;spacing:12
        Repeater {
            model:["primary","secondary","outline","subtle","ghost","link","destructive"]
            onItemAdded:function(index,item){if(index===0)window.primaryPreview=item}
            BleeckerButtonStyle {
                id:preview
                required property string modelData
                objectName:"buttonStyleVariant-"+modelData
                variant:modelData;size:"sm"
                onClicked:window.configure({variant:modelData})
                T.Label {text:preview.modelData;color:palette.windowText}
            }
        }
    }
    Row {
        x:24;y:94;spacing:10
        BleeckerButton {text:"Counter";size:"xs";onClicked:window.configure({content:"counter",parentLayout:"zstack"})}
        BleeckerButton {text:"Flat";size:"xs";onClicked:window.configure({content:"multi",parentLayout:"zstack"})}
        BleeckerButton {text:"Row";size:"xs";onClicked:window.configure({content:"multi",parentLayout:"hstack"})}
        BleeckerButton {text:"Column";size:"xs";onClicked:window.configure({content:"multi",parentLayout:"vstack"})}
        BleeckerButton {text:window.model.disabled ? "Enable":"Disable";size:"xs";onClicked:window.configure({disabled:!window.model.disabled})}
        BleeckerButton {text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
    }
    ButtonStyleCase {id:primary;objectName:"consumerButtonStyle";x:24;y:170;definition:window.model}
    Text {x:24;y:606;text:"Shared action count: "+primary.localValue;font.family:BleeckerTheme.secondaryFont;font.pixelSize:14;color:BleeckerTheme.palette.textPrimary}
    Text {
        x:720;y:200;width:280
        text:"Each flat label is a separate layout participant. Hold either part to press both.\n\nRelease over the original target to activate it."
        wrapMode:Text.WordWrap;font.family:BleeckerTheme.secondaryFont;font.pixelSize:14;color:BleeckerTheme.palette.textSecondary
    }
    BleeckerButtonStyle {
        x:740;y:430;variant:"outline"
        Rectangle {implicitWidth:180;implicitHeight:70;color:BleeckerTheme.alpha(BleeckerTheme.palette.sea,0.18)}
    }
    Text {x:720;y:530;width:280;text:"Caller rectangles, zero-size items and explicit stacks keep their own content.";wrapMode:Text.WordWrap;font.family:BleeckerTheme.secondaryFont;font.pixelSize:13;color:BleeckerTheme.palette.textSecondary}
}
