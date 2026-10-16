import QtQuick
import Avelino

Window {
    id: window
    property int page: 4
    width: 800; height: 560; visible: true
    title: "Avelino — pagination and icon buttons"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {BleeckerTheme.dark=captureDark;BleeckerTheme.textScale=captureTextScale;BleeckerTheme.reducedMotion=true}
    Column {
        x: 24; y: 24; spacing: 24
        BleeckerEyebrow {text:"Caller-owned pages"}
        BleeckerPagination {page:window.page;pageCount:8;onPageRequested:page => window.page=page}
        BleeckerPagination {page:1;pageCount:8}
        BleeckerPagination {page:8;pageCount:8}
        BleeckerPagination {page:1;pageCount:0}
        BleeckerPagination {page:4;pageCount:8;enabled:false}
        BleeckerPagination {width:140;page:4;pageCount:8}
    }
    Column {
        x: 380; y: 24; spacing: 24
        BleeckerEyebrow {text:"Icon sizes and variants"}
        Repeater {
            model:["sm","md","lg"]
            Row {
                required property string modelData
                id: row
                spacing: 16
                Repeater {
                    model:["default","subtle","ghost"]
                    BleeckerIconButton {
                        id: icon
                        required property string modelData
                        size:row.modelData;variant:modelData;accessibilityLabel:"Next"
                        icon: NavigationIcon { direction:"right";color:icon.foregroundColor;pixelSize:icon.glyphPixelSize }
                    }
                }
            }
        }
        BleeckerPagination {page:4;pageCount:8;LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true}
    }
}
