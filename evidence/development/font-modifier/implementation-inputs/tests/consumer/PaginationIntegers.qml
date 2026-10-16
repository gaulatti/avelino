import QtQuick
import Avelino

Window {
    id: window
    property var page: "9223372036854775806"
    property var count: "9223372036854775807"
    property string requested: ""
    property int requests: 0
    width:840;height:560;visible:true
    title:"Avelino installed exact pagination"
    color:BleeckerTheme.palette.background
    Component.onCompleted: {BleeckerTheme.dark=consumerDark;BleeckerTheme.textScale=consumerTextScale;BleeckerTheme.reducedMotion=true}
    Column {
        x:24;y:24;spacing:28
        BleeckerEyebrow {text:"Exact signed integers and caller state"}
        BleeckerPagination {
            objectName:"exactPager";page:window.page;pageCount:window.count;locale:Qt.locale("en_US")
            onPageRequested: page => {window.requested=page;window.page=page;window.requests++}
        }
        BleeckerPagination {objectName:"minimumPager";page:"-9223372036854775808";pageCount:"9223372036854775807";locale:Qt.locale("en_US")}
        BleeckerPagination {objectName:"safePager";page:"9007199254740993";pageCount:"9007199254740995";locale:Qt.locale("en_US")}
        BleeckerPagination {objectName:"narrowExactPager";width:260;page:"9223372036854775806";pageCount:"9223372036854775807";locale:Qt.locale("en_US")}
        BleeckerTextField {objectName:"exactNextField";width:300;placeholderText:"Continue here"}
    }
}
