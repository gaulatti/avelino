import QtQuick
import QtTest
import Avelino

Item {
    id: root
    width: 800; height: 600
    property int page: 4
    property int count: 8
    property int requests: 0
    property int requested: -100
    property bool applyRequest: true
    Component {
        id: pagerFactory
        BleeckerPagination {
            page: root.page; pageCount: root.count
            onPageRequested: page => {root.requests++;root.requested=page;if(root.applyRequest) root.page=page}
        }
    }
    Component {
        id: iconFactory
        BleeckerIconButton {
            id: button
            accessibilityLabel: "Continue"
            icon: Rectangle { width: button.iconEdge; height: width; color: button.foregroundColor }
            onClicked: root.requests++
        }
    }
    TestCase {
        name: "PaginationContracts"
        when: windowShown
        function init() {root.page=4;root.count=8;root.requests=0;root.requested=-100;root.applyRequest=true;BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
        function test_icon_variants_data() {
            const rows=[]
            for (const size of ["sm","md","lg"]) for (const variant of ["default","subtle","ghost"]) for (const scale of [1,1.5]) for (const dark of [false,true]) rows.push({tag:[size,variant,scale,dark].join("-"),size,variant,scale,dark})
            return rows
        }
        function test_icon_variants(d) {
            BleeckerTheme.dark=d.dark;BleeckerTheme.textScale=d.scale
            const item=createTemporaryObject(iconFactory,root,{size:d.size,variant:d.variant})
            verify(item)
            compare(item.width,{sm:32,md:44,lg:56}[d.size]);compare(item.height,{sm:28,md:36,lg:40}[d.size])
            compare(item.iconEdge,{sm:12,md:16,lg:20}[d.size]);compare(item.buttonSize,{sm:"xs",md:"sm",lg:"md"}[d.size])
            compare(item.buttonVariant,d.variant === "default" ? "secondary" : d.variant)
            compare(item.inputItem.Accessible.name,"Continue")
            mousePress(item);verify(item.down);mouseRelease(item);compare(root.requests,1)
            item.forceActiveFocus(Qt.TabFocusReason);keyClick(Qt.Key_Space);compare(root.requests,2)
            item.enabled=false;mouseClick(item);compare(root.requests,2);verify(!item.inputItem.enabled)
            item.accessibilityLabel="Updated name";compare(item.inputItem.Accessible.name,"Updated name")
        }
        function test_page_boundaries_data() {
            return [
                {tag:"first",page:1,count:8,previous:false,next:true,nextValue:2},
                {tag:"last",page:8,count:8,previous:true,next:false,previousValue:7},
                {tag:"single",page:1,count:1,previous:false,next:false},
                {tag:"zero",page:1,count:0,previous:false,next:false},
                {tag:"negative",page:1,count:-3,previous:false,next:false},
                {tag:"below",page:0,count:8,previous:false,next:true,nextValue:1},
                {tag:"above",page:12,count:8,previous:true,next:false,previousValue:11},
                {tag:"empty-count",page:2,count:0,previous:true,next:false,previousValue:1}
            ]
        }
        function test_page_boundaries(d) {
            root.page=d.page;root.count=d.count
            const item=createTemporaryObject(pagerFactory,root),previous=findChild(item,"bleeckerPreviousPage"),next=findChild(item,"bleeckerNextPage")
            compare(previous.enabled,d.previous);compare(next.enabled,d.next)
            compare(findChild(item,"bleeckerPaginationLabel").text,"Page "+d.page+" of "+Math.max(1,d.count))
            if (!d.previous) {mouseClick(previous);compare(root.requests,0)}
            if (!d.next) {mouseClick(next);compare(root.requests,0)}
            mouseClick(d.previous ? previous : next)
            if (d.previous || d.next) {compare(root.requests,1);compare(root.page,d.previous ? d.previousValue : d.nextValue)}
        }
        function test_caller_external_keyboard_and_count() {
            const item=createTemporaryObject(pagerFactory,root),previous=findChild(item,"bleeckerPreviousPage"),next=findChild(item,"bleeckerNextPage")
            mouseClick(next);compare(root.page,5);compare(item.page,5);compare(root.requested,5)
            root.page=7;compare(item.page,7)
            previous.forceActiveFocus(Qt.TabFocusReason);keyClick(Qt.Key_Space);compare(root.page,6);compare(root.requests,2)
            root.count=3;compare(item.pageCount,3);compare(item.page,6);verify(!next.enabled);verify(previous.enabled)
            root.applyRequest=false;mouseClick(previous);compare(root.requested,5);compare(root.page,6);compare(item.page,6)
            root.page=2;root.count=8;compare(item.page,2);verify(next.enabled)
            item.enabled=false;mouseClick(next);compare(root.requests,3);compare(root.page,2)
            root.page=4;compare(item.page,4)
        }
        function test_localized_large_page_label() {
            root.page=1000000000;root.count=2000000000
            const item=createTemporaryObject(pagerFactory,root,{locale:Qt.locale("en_US")})
            const label=findChild(item,"bleeckerPaginationLabel")
            compare(label.text,"Page 1,000,000,000 of 2,000,000,000")
            item.locale=Qt.locale("de_DE")
            compare(label.text,"Page 1.000.000.000 of 2.000.000.000")
        }
        function test_narrow_and_wide_data() {return [{tag:"standard",scale:1},{tag:"scaled",scale:1.5}]}
        function test_narrow_and_wide(d) {
            BleeckerTheme.textScale=d.scale
            const item=createTemporaryObject(pagerFactory,root,{width:140})
            const label=findChild(item,"bleeckerPaginationLabel")
            tryCompare(label,"height",30);compare(item.height,36);verify(item.contentSize.width<=140)
            item.width=400;tryCompare(label,"height",15);compare(item.height,36)
        }
        function test_layout_and_scaling() {
            const item=createTemporaryObject(pagerFactory,root)
            const label=findChild(item,"bleeckerPaginationLabel"),previous=findChild(item,"bleeckerPreviousPage"),next=findChild(item,"bleeckerNextPage")
            compare(item.height,36);compare(label.font.pointSize,BleeckerFonts.pointSizeForPixels(12))
            compare(label.x,previous.width+8);compare(next.x,label.x+label.width+8)
            const width=item.width
            BleeckerTheme.textScale=1.5;compare(item.width,width);compare(item.height,36)
            item.LayoutMirroring.enabled=true;item.LayoutMirroring.childrenInherit=true
            tryVerify(() => previous.x>next.x)
        }
    }
}
