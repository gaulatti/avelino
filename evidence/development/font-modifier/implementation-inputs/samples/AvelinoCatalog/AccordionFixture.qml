import QtQuick
import Avelino

Window {
    width:900;height:640;visible:true
    title:"Avelino — accordions";color:BleeckerTheme.palette.background
    Component.onCompleted:{BleeckerTheme.dark=captureDark;BleeckerTheme.textScale=captureTextScale;BleeckerTheme.reducedMotion=true}
    Component {id:copy;AccordionText {text:"Body copy";wrapWidth:parent.availableWidth}}
    Component {id:empty;Item {implicitWidth:0;implicitHeight:0}}
    Component {
        id:form
        Column {
            width:parent.availableWidth;spacing:10
            AccordionText {text:"Reopening clears this form"}
            BleeckerTextField {width:parent.width;placeholderText:"Edition name"}
        }
    }
    BleeckerEyebrow {x:24;y:24;text:"Details on demand"}
    Row {
        x:24;y:72;spacing:40
        Column {
            spacing:24
            BleeckerAccordion {width:390;title:"Closed details";content:copy}
            BleeckerAccordion {width:390;title:"Open details";initiallyExpanded:true;content:copy}
            BleeckerAccordion {width:390;title:"Edition settings";initiallyExpanded:true;content:form}
            BleeckerAccordion {width:390;title:"Unavailable";initiallyExpanded:true;content:copy;enabled:false}
        }
        Column {
            spacing:24
            BleeckerAccordion {width:180;title:"Keep selected editions available for review";initiallyExpanded:true;content:copy}
            BleeckerAccordion {width:390;title:"Empty content";initiallyExpanded:true}
            BleeckerAccordion {width:390;title:"An explicit zero-size view";initiallyExpanded:true;content:empty}
            BleeckerAccordion {width:390;title:"Right-to-left";initiallyExpanded:true;content:copy;LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true}
        }
    }
}
