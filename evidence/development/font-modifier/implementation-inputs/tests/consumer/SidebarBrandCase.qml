import QtQuick
import Avelino

Item {
    id:fixture
    required property var definition
    readonly property Item control:loader.item
    readonly property Item presentationItem:control ? control.presentationItem:null
    implicitWidth:control ? control.width:0;implicitHeight:control ? control.height:0
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    Loader {id:loader;sourceComponent:definition.api==="BleeckerSidebarItem" ? sidebar:definition.api==="BleeckerBrandMark" ? mark:lockup}
    Component {
        id:sidebar
        BleeckerSidebarItem {
            title:definition.text;selected:definition.flag;enabled:!definition.disabled
            maximumWidth:definition.intrinsic ? -1:definition.value
            icon:SidebarGlyph {symbol:definition.symbol}
        }
    }
    Component {id:mark;BleeckerBrandMark {size:definition.size;enabled:!definition.disabled}}
    Component {id:lockup;BleeckerBrandLockup {name:definition.text;maximumWidth:definition.intrinsic ? -1:definition.value;enabled:!definition.disabled}}
}
