import QtQuick
import Avelino
Window {
    id:window
    property string heading:"Edition details"
    property bool initial:false
    property string bodyCopy:"Body copy"
    property int created:0
    property int destroyed:0
    property int actions:0
    width:840;height:560;visible:true
    title:"Avelino installed accordion";color:BleeckerTheme.palette.background
    Component.onCompleted:{BleeckerTheme.dark=consumerDark;BleeckerTheme.textScale=consumerTextScale;BleeckerTheme.reducedMotion=true}
    Component {id:copy;AccordionText {text:"Body copy";wrapWidth:parent.availableWidth}}
    Component {
        id:formBody
        Column {
            id:form
            property int applied:0
            width:parent.availableWidth;spacing:10
            AccordionText {objectName:"accordionBodyCopy";text:window.bodyCopy}
            BleeckerTextField {objectName:"accordionBodyField";width:parent.width;placeholderText:"Edition name"}
            BleeckerButton {objectName:"accordionApply";text:"Apply";onClicked:{form.applied++;window.actions++}}
            Component.onCompleted:window.created++
            Component.onDestruction:window.destroyed++
        }
    }
    BleeckerEyebrow {x:24;y:24;text:"Details and forms"}
    Row {
        x:24;y:64;spacing:36
        Column {
            spacing:20
            BleeckerAccordion {objectName:"accordion";width:380;title:window.heading;initiallyExpanded:window.initial;content:formBody}
            BleeckerAccordion {objectName:"disabledAccordion";width:380;title:"Unavailable";initiallyExpanded:true;content:copy;enabled:false}
            BleeckerTextField {objectName:"accordionNextField";width:300;placeholderText:"Continue here"}
        }
        Column {
            spacing:24
            BleeckerAccordion {objectName:"narrowAccordion";width:180;title:"Keep selected editions available for review";content:copy}
            BleeckerAccordion {objectName:"initialAccordion";width:340;title:"Initially open";initiallyExpanded:true;content:copy}
            BleeckerAccordion {objectName:"mirroredAccordion";width:340;title:"Details";content:copy;LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true}
        }
    }
}
