import QtQuick
import Avelino

Window {
    id:window;width:640;height:400;visible:true;title:"Avelino surface source comparisons"
    color:BleeckerTheme.palette.background
    property var model:({fixture:"default",radius:null,resolvedRadius:12,content:"clear",parentLayout:"zstack",text:"Review edition",offer:null,rtl:false,parentFont:false,parentRed:false,baselineParent:true,disabled:false,guide:null,width:640,height:400})
    property int inputMode:0
    readonly property bool input:consumerSurfaceInput
    readonly property Item primaryFixture:fixture.item
    function configure(values):void {model=values}
    Component.onCompleted:{BleeckerTheme.reducedMotion=true;BleeckerTheme.dark=consumerDark;BleeckerTheme.textScale=consumerTextScale}
    Component {id:baseline;SurfaceModifierCase {definition:window.model;firstBaselineParent:true;firstTextGuide:window.model.guide===null ? NaN:window.model.guide}}
    Component {id:pointer;SurfaceInputCase {definition:window.model;mode:window.inputMode}}
    Loader {id:fixture;sourceComponent:window.input ? pointer:baseline}
}
