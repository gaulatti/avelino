import QtQuick
import Avelino

Window {
    id: window
    property var page: "9223372036854775806"
    width: 840; height: 520; visible: true
    title: "Avelino — exact pagination integers"
    color: BleeckerTheme.palette.background
    Component.onCompleted: {BleeckerTheme.dark=captureDark;BleeckerTheme.textScale=captureTextScale;BleeckerTheme.reducedMotion=true}
    Column {
        x:24;y:24;spacing:28
        BleeckerEyebrow {text:"Full signed 64-bit source range"}
        BleeckerPagination {page:window.page;pageCount:"9223372036854775807";locale:Qt.locale("en_US");onPageRequested:page => window.page=page}
        BleeckerPagination {page:"-9223372036854775808";pageCount:"9223372036854775807";locale:Qt.locale("en_US")}
        BleeckerPagination {page:"9007199254740993";pageCount:"9007199254740995";locale:Qt.locale("en_US")}
        BleeckerPagination {page:"2";pageCount:"-9223372036854775808";locale:Qt.locale("en_US")}
        BleeckerPagination {width:260;page:"9223372036854775806";pageCount:"9223372036854775807";locale:Qt.locale("en_US")}
    }
}
