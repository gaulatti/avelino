import QtQuick
import QtTest
import Avelino

Item {
    id: root
    width: 1000; height: 240
    PixelAlignment {id:metrics;target:root}
    property var page: "9223372036854775806"
    property var count: "9223372036854775807"
    property string requested: ""
    property int calls: 0
    Component {
        id: factory
        BleeckerPagination {
            page:root.page;pageCount:root.count;locale:Qt.locale("en_US")
            onPageRequested: page => {root.requested=page;root.page=page;root.calls++}
        }
    }
    TestCase {
        name: "ExactPaginationIntegerContracts"
        when: windowShown
        function init() {root.calls=0;root.requested="";BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
        function test_exact_requests_data() {
            return [
                {tag:"int32",page:"2147483647",count:"2147483648",next:"2147483648",previous:"2147483646",label:"Page 2,147,483,647 of 2,147,483,648"},
                {tag:"safe-limit",page:"9007199254740991",count:"9007199254740993",next:"9007199254740992",previous:"9007199254740990",label:"Page 9,007,199,254,740,991 of 9,007,199,254,740,993"},
                {tag:"above-safe",page:"9007199254740993",count:"9007199254740995",next:"9007199254740994",previous:"9007199254740992",label:"Page 9,007,199,254,740,993 of 9,007,199,254,740,995"},
                {tag:"int64-upper",page:"9223372036854775806",count:"9223372036854775807",next:"9223372036854775807",previous:"9223372036854775805",label:"Page 9,223,372,036,854,775,806 of 9,223,372,036,854,775,807"}
            ]
        }
        function test_exact_requests(d) {
            root.page=d.page;root.count=d.count
            const item=createTemporaryObject(factory,root),next=findChild(item,"bleeckerNextPage"),previous=findChild(item,"bleeckerPreviousPage"),label=findChild(item,"bleeckerPaginationLabel")
            compare(label.text,d.label)
            mouseClick(next);compare(root.requested,d.next);compare(typeof root.requested,"string");compare(item.page,d.next);compare(root.calls,1)
            root.page=d.page;compare(item.page,d.page)
            previous.forceActiveFocus(Qt.TabFocusReason);keyClick(Qt.Key_Space);compare(root.requested,d.previous);compare(root.calls,2)
            root.page="4";root.count="8";compare(label.text,"Page 4 of 8");verify(next.enabled)
        }
        function test_minimum_and_disabled_extremes() {
            root.page="-9223372036854775808";root.count="9223372036854775807"
            const item=createTemporaryObject(factory,root),next=findChild(item,"bleeckerNextPage"),previous=findChild(item,"bleeckerPreviousPage"),label=findChild(item,"bleeckerPaginationLabel")
            verify(!previous.enabled);mouseClick(previous);compare(root.calls,0)
            mouseClick(next);compare(root.requested,"-9223372036854775807");compare(root.calls,1)
            root.page="9223372036854775807";verify(!next.enabled);mouseClick(next);compare(root.calls,1)
            root.page="2";root.count="-9223372036854775808";compare(label.text,"Page 2 of 1");mouseClick(previous);compare(root.requested,"1")
            root.page="-9223372036854775808";verify(!next.enabled);verify(!previous.enabled)
        }
        function test_source_wrapped_body_through_resize() {
            root.page="9223372036854775806";root.count="9223372036854775807"
            const item=createTemporaryObject(factory,root,{width:260})
            const nativeWidth=metrics.devicePixelRatio===1 ? 260 : 259.5
            tryCompare(item,"contentSize",Qt.size(nativeWidth,45))
            item.width=257;tryCompare(item,"contentSize",Qt.size(257,45))
            item.width=264;tryCompare(item,"contentSize",Qt.size(nativeWidth,45))
            root.page="4";root.count="8";tryCompare(item,"contentSize",Qt.size(165,36))
        }
        function test_safe_numeric_inputs_and_locale() {
            root.page=9007199254740991;root.count="9223372036854775807"
            const item=createTemporaryObject(factory,root),label=findChild(item,"bleeckerPaginationLabel")
            item.locale=Qt.locale("de_DE");compare(label.text,"Page 9.007.199.254.740.991 of 9.223.372.036.854.775.807")
            root.page=4;root.count=8;mouseClick(findChild(item,"bleeckerNextPage"));compare(root.requested,"5");compare(item.page,"5")
        }
    }
}
