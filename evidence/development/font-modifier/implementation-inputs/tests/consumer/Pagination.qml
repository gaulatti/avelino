import QtQuick
import Avelino

Window {
    id: window
    property int page: 4
    property int count: 8
    property int requests: 0
    property int requested: -100
    property int iconCalls: 0
    property bool applyRequest: true
    width: 800; height: 560; visible: true
    title: "Avelino installed pagination"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {BleeckerTheme.dark=consumerDark;BleeckerTheme.textScale=consumerTextScale;BleeckerTheme.reducedMotion=true}
    Column {
        x: 24; y: 24; spacing: 28
        BleeckerEyebrow {text:"Caller-owned pagination"}
        BleeckerPagination {
            objectName: "pager";page:window.page;pageCount:window.count
            onPageRequested: page => {window.requests++;window.requested=page;if(window.applyRequest) window.page=page}
        }
        BleeckerIconButton {
            id: icon
            objectName: "iconButton";accessibilityLabel:"Continue"
            icon: NavigationIcon {direction:"right";color:icon.foregroundColor;pixelSize:icon.glyphPixelSize}
            onClicked: window.iconCalls++
        }
        BleeckerTextField {objectName:"paginationNext";width:300;placeholderText:"Continue here"}
    }
    Column {
        x: 410; y: 24; spacing: 28
        BleeckerEyebrow {text:"Bounds and layout"}
        BleeckerPagination {objectName:"narrowPager";width:140;page:4;pageCount:8}
        BleeckerPagination {objectName:"rtlPager";page:4;pageCount:8;LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true}
        BleeckerPagination {objectName:"emptyPager";page:1;pageCount:0}
        BleeckerPagination {objectName:"longPager";page:1000000000;pageCount:2000000000;locale:Qt.locale("en_US")}
        BleeckerPagination {objectName:"disabledPager";page:4;pageCount:8;enabled:false}
    }
}
