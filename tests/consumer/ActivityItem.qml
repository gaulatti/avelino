import QtQuick
import Avelino

Window {
    id:window;width:860;height:600;visible:true;title:"Avelino activity items"
    color:BleeckerTheme.palette.background
    readonly property real fixtureTextScale:typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
    property var model:({fixture:"gallery",api:"BleeckerActivityItem",title:"Edition updated",detail:"Ready for review",timestamp:"2 min ago",symbol:"clock",actions:"multi",proposalWidth:600,width:720,height:800,intrinsic:false,disabled:false,rtl:false,parentFont:0,parentForeground:"inherit",environmentLocale:"en_US"})
    readonly property Item primaryFixture:primary
    readonly property Item primaryControl:primary.control
    Component.onCompleted:{BleeckerTheme.dark=typeof consumerDark!=="undefined" ? consumerDark:captureDark;BleeckerTheme.textScale=fixtureTextScale;BleeckerTheme.reducedMotion=true}
    function configure(value){model=Object.assign({},model,value)}
    BleeckerButton {objectName:"activityBefore";x:24;y:16;text:"Previous";size:"xs"}
    ActivityItemCase {id:primary;objectName:"consumerActivity";x:24;y:70;definition:window.model}
    BleeckerButton {objectName:"activityAfter";x:144;y:16;text:"Continue";size:"xs"}
    BleeckerActivityItem {objectName:"activityDisabled";x:24;y:220;maximumWidth:390;title:"Permissions updated";detail:"Editor access was granted";timestamp:"5 min ago";enabled:false;BleeckerButton {text:"Review";size:"sm"}}
    BleeckerActivityItem {objectName:"activityEmpty";x:24;y:365;maximumWidth:390;title:"Delivery complete";detail:"All selected editions are ready";timestamp:"Just now"}
    BleeckerActivityItem {objectName:"activityNarrow";x:470;y:220;maximumWidth:160;title:"Edition updated";detail:"Ready for review";timestamp:"2 min ago";BleeckerButton {text:"Review";variant:"secondary";size:"sm"}}
    BleeckerActivityItem {objectName:"activityRtl";x:24;y:500;maximumWidth:390;title:"Edition updated";detail:"Ready for review";timestamp:"2 min ago";LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true;BleeckerButton {text:"Review";variant:"secondary";size:"sm"}}
    BleeckerActivityItem {objectName:"activityStateful";x:455;y:500;maximumWidth:375;title:"Caller state";detail:"Action content keeps its own value";timestamp:"Just now";BleeckerButton {objectName:"galleryActivityCounter";property int value:0;text:"Count "+value;variant:"secondary";size:"sm";onClicked:value++}}
}
