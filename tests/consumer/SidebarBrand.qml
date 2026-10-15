import QtQuick
import Avelino

Window {
    id:window;width:840;height:560;visible:true;color:BleeckerTheme.palette.background
    title:"Avelino sidebar and branding"
    property string page:"home"
    property string editionTitle:"Editions"
    property string brandName:"Bleecker"
    property real logoSize:64
    property int requests:0
    property string lastRequest:""
    readonly property bool dark:typeof consumerDark!=="undefined" ? consumerDark:captureDark
    readonly property real textScale:typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
    Component.onCompleted:{BleeckerTheme.dark=dark;BleeckerTheme.textScale=textScale;BleeckerTheme.reducedMotion=true}
    BleeckerBrandLockup {objectName:"consumerBrandLockup";x:24;y:24;name:window.brandName;maximumWidth:350}
    BleeckerSidebarItem {objectName:"homeSidebarItem";x:24;y:100;maximumWidth:300;title:"Home";selected:window.page==="home";icon:SidebarGlyph {} onClicked:{window.requests++;window.lastRequest="home"}}
    BleeckerSidebarItem {objectName:"editionSidebarItem";x:24;y:150;maximumWidth:300;title:window.editionTitle;selected:window.page==="editions";icon:SidebarGlyph {} onClicked:{window.requests++;window.lastRequest="editions"}}
    BleeckerSidebarItem {objectName:"disabledSidebarItem";x:24;y:200;maximumWidth:300;title:"Unavailable";selected:true;enabled:false;icon:SidebarGlyph {} onClicked:window.requests++}
    BleeckerSidebarItem {objectName:"narrowSidebarItem";x:24;y:265;maximumWidth:120;title:"Editions";selected:false;icon:SidebarGlyph {}}
    BleeckerSidebarItem {objectName:"rtlSidebarItem";x:430;y:100;maximumWidth:300;title:"RTL editions";selected:true;icon:SidebarGlyph {} LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true}
    BleeckerBrandMark {objectName:"consumerBrandMark";x:430;y:200;width:250;height:170;size:window.logoSize}
    BleeckerTextField {objectName:"sidebarOutsideField";x:24;y:420;width:320;placeholderText:"Continue editing"}
}
