import QtQuick
import Avelino

Window {
    id:window
    readonly property bool gallery:typeof consumerDark==="undefined" || (typeof consumerDateGallery!=="undefined" &&consumerDateGallery)
    width:gallery ? 1120:640;height:gallery ? 820:400
    visible:true;title:"Avelino date range";color:BleeckerTheme.palette.background
    readonly property Item primaryFixture:fixture
    readonly property real fixtureTextScale:BleeckerTheme.textScale
    readonly property bool fixtureDark:BleeckerTheme.dark
    function defaults():var {return {id:"default",start:1710000000.625,end:1710864000.125,locale:"en_US",calendar:"gregorian",timeZone:"UTC",controlSize:"regular",pickerStyle:"inherit",owner:"echo",rtl:false,disabled:false,parentFont:false,parentRed:false}}
    function configure(value):void {fixture.configure(value)}
    function update(value):void {fixture.updateConfiguration(value)}
    function environment(dark,scale):void {BleeckerTheme.dark=dark;BleeckerTheme.textScale=scale}
    Component.onCompleted:{BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=gallery ? captureDark:consumerDark;BleeckerTheme.textScale=gallery ? captureTextScale:consumerTextScale}
    ProposalRow {
        x:24;y:24;spacing:8;visible:window.gallery
        BleeckerButton {objectName:"dateOperator-default";text:"Reset";size:"xs";onClicked:window.configure(window.defaults())}
        BleeckerButton {objectName:"dateOperator-bounds";text:"Date limits";size:"xs";onClicked:window.update({lower:fixture.definition.lower===undefined ? 1709251200:undefined,upper:fixture.definition.upper===undefined ? 1711843200:undefined})}
        BleeckerButton {objectName:"dateOperator-crossed";text:"Crossed dates";size:"xs";onClicked:{fixture.externalStart(1711929600.75);fixture.externalEnd(1709164800.25)}}
        Repeater {model:[{value:"inherit",name:"Default"},{value:"field",name:"Field"},{value:"graphical",name:"Calendar"}]
            BleeckerButton {required property var modelData;objectName:"dateOperator-style-"+modelData.value;text:modelData.name;size:"xs";onClicked:window.update({pickerStyle:modelData.value})}
        }
    }
    ProposalRow {
        x:24;y:78;spacing:8;visible:window.gallery
        Repeater {model:[{value:"echo",name:"Apply immediately"},{value:"ignore",name:"Ignore edits"},{value:"delay",name:"Apply later"}]
            BleeckerButton {required property var modelData;objectName:"dateOperator-owner-"+modelData.value;text:modelData.name;size:"xs";onClicked:window.update({owner:modelData.value})}
        }
        BleeckerButton {objectName:"dateOperator-apply";text:"Apply pending";size:"xs";onClicked:fixture.applyPending()}
        BleeckerButton {objectName:"dateOperator-disabled";text:"Disabled";size:"xs";onClicked:window.update({disabled:!fixture.definition.disabled})}
    }
    ProposalRow {
        x:24;y:132;spacing:8;visible:window.gallery
        BleeckerButton {objectName:"dateOperator-locale";text:"Locale";size:"xs";onClicked:window.update({locale:fixture.definition.locale==="en_US" ? "ar_EG":"en_US"})}
        BleeckerButton {objectName:"dateOperator-calendar";text:"Calendar system";size:"xs";onClicked:window.update({calendar:fixture.definition.calendar==="gregorian" ? "hebrew":"gregorian"})}
        BleeckerButton {objectName:"dateOperator-timezone";text:"Time zone";size:"xs";onClicked:window.update({timeZone:fixture.definition.timeZone==="UTC" ? "America/New_York":"UTC"})}
        BleeckerButton {objectName:"dateOperator-size";text:"Control size";size:"xs";onClicked:window.update({controlSize:fixture.definition.controlSize==="regular" ? "small":"regular"})}
        BleeckerButton {objectName:"dateOperator-rtl";text:"RTL";size:"xs";onClicked:window.update({rtl:!fixture.definition.rtl})}
        BleeckerButton {objectName:"dateOperator-narrow";text:"Narrow caller";size:"xs";onClicked:window.update({width:fixture.definition.width===100 ? undefined:100})}
        BleeckerButton {objectName:"dateOperator-theme";text:"Theme";size:"xs";onClicked:BleeckerTheme.dark=!BleeckerTheme.dark}
    }
    ProposalRow {
        x:24;y:186;spacing:8;visible:window.gallery
        Repeater {model:[{value:"en_US",name:"Chinese / English"},{value:"zh_CN",name:"Chinese / 中文"},{value:"ko_KR",name:"Chinese / 한국어"}]
            BleeckerButton {required property var modelData;objectName:"dateOperator-chinese-"+modelData.value;text:modelData.name;size:"xs";onClicked:window.update({locale:modelData.value,calendar:"chinese"})}
        }
        BleeckerButton {objectName:"dateOperator-leap-month";text:"Leap month";size:"xs";onClicked:window.configure(Object.assign(window.defaults(),{id:"chinese-zh-cn-leap-regular",locale:"zh_CN",calendar:"chinese",start:1679832000.625,end:1680696000.125}))}
    }
    DateRangePickerCase {id:fixture;x:window.gallery ? 24:0;y:window.gallery ? 220:0}
    Text {
        x:720;y:250;width:345;visible:window.gallery;wrapMode:Text.WordWrap
        text:"Choose how the owner applies edits. Date fields may show a request before the owner updates its saved value.\n\nFrom: "+DateRangeTools.formatted(fixture.modelStart,fixture.definition.locale,fixture.definition.calendar,fixture.definition.timeZone).text+"\nTo: "+DateRangeTools.formatted(fixture.modelEnd,fixture.definition.locale,fixture.definition.calendar,fixture.definition.timeZone).text
        font.family:BleeckerFonts.secondary;font.pixelSize:16;color:BleeckerTheme.palette.textSecondary
        Accessible.role:Accessible.StaticText;Accessible.name:text
    }
}
