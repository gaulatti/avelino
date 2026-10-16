import QtQuick
import Avelino

Item {
    id:fixture
    required property var definition
    readonly property Item control:loader.item
    readonly property Item presentationItem:control ? control.presentationItem:null
    implicitWidth:control ? control.width:0;implicitHeight:control ? control.height:0
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    Loader {id:loader;sourceComponent:definition.api==="BleeckerPageHeader" ? header:breadcrumb}
    Component {
        id:header
        BleeckerPageHeader {
            eyebrow:definition.eyebrow;title:definition.title;description:definition.text;enabled:!definition.flag
            width:definition.intrinsic ? implicitWidth:Number(definition.size)
            Loader {
                id:action
                sourceComponent:definition.actionMode==="empty" ? null:definition.actionMode==="zero" ? zero:definition.actionMode==="rect" ? rectangle:definition.actionMode==="two" ? two:definition.actionMode==="tall" ? tall:definition.actionMode==="overflow" ? overflow:definition.actionMode==="button" ? button:definition.actionMode==="buttons" ? buttons:actionText
                BleeckerLayout.minimumWidth:!item ? 0:item.BleeckerLayout.minimumWidth>=0 ? item.BleeckerLayout.minimumWidth:item.implicitWidth
                BleeckerLayout.idealWidth:!item ? 0:item.BleeckerLayout.idealWidth>=0 ? item.BleeckerLayout.idealWidth:item.implicitWidth
                readonly property real availableWidth:BleeckerLayout.proposedWidth
            }
        }
    }
    Component {id:zero;Item {implicitWidth:0;implicitHeight:0}}
    Component {id:rectangle;Rectangle {implicitWidth:24;implicitHeight:20;color:BleeckerTheme.nativeRed}}
    Component {id:two;ProposalRow {spacing:12;Rectangle {implicitWidth:24;implicitHeight:20;color:BleeckerTheme.nativeRed} Rectangle {implicitWidth:40;implicitHeight:30;color:BleeckerTheme.nativeBlue}}}
    Component {id:tall;Rectangle {implicitWidth:72;implicitHeight:120;color:BleeckerTheme.nativeRed}}
    Component {id:overflow;Item {implicitWidth:72;implicitHeight:90;Rectangle {x:35;y:-35;width:72;height:90;color:BleeckerTheme.nativeRed}}}
    Component {id:button;BleeckerButton {text:"Create 0";maximumWidth:parent.availableWidth}}
    Component {
        id:buttons
        ProposalRow {
            id:buttonsRow;spacing:12;maximumWidth:parent.availableWidth
            BleeckerLayout.minimumWidth:buttonsRow.minimumWidth;BleeckerLayout.idealWidth:buttonsRow.naturalWidth
            BleeckerButton {text:"Cancel";variant:"secondary"}
            BleeckerButton {text:"Create 0"}
        }
    }
    Component {
        id:actionText
        ButtonLabel {
            readonly property bool custom:definition.actionMode==="custom-font"
            text:"Actions";font.family:custom ? BleeckerTheme.secondaryFont:definition.value>0 ? BleeckerTheme.primaryFont:Qt.application.font.family
            font.pointSize:BleeckerFonts.pointSizeForPixels(custom ? 18:definition.value>0 ? definition.value:13)
            font.weight:custom ? Font.DemiBold:Font.Normal
            color:custom ? BleeckerTheme.nativeRed:BleeckerTheme.nativeTextPrimary
            wrapWidth:parent.availableWidth
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:unwrappedWidth
        }
    }
    Component {id:house;BreadcrumbHouse {}}
    Component {
        id:breadcrumb
        BleeckerBreadcrumb {
            maximumWidth:definition.intrinsic ? -1:Number(definition.size);enabled:!definition.flag
            items:definition.titles.map((title,index)=>({title:title,icon:definition.icons[index] ? house:null}))
        }
    }
}
