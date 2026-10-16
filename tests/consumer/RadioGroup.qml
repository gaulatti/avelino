import QtQuick
import Avelino

Window {
    id:window;width:840;height:600;visible:true;title:"Avelino RadioGroup"
    color:BleeckerTheme.palette.background
    property var model:({selection:"daily",options:[{value:"daily",label:"Daily"},{value:"weekly",label:"Weekly"},{value:"monthly",label:"Monthly"}],orientation:"vertical",proposalWidth:300,intrinsic:false,disabled:false,rtl:false,observeOnly:false,parentFont:0,parentFontKind:"primary",parentFontWeight:"regular",parentForeground:"inherit",environmentLocale:"en_US"})
    function nativeStringsEqual(left:string,right:string):bool{return BleeckerSelectionTools.stringsEqual(left,right)}
    property int calls:0
    property var requests:[]
    property var requested:null
    readonly property Item control:mainCase.control
    readonly property real fixtureTextScale:typeof consumerTextScale!=="undefined" ? consumerTextScale:captureTextScale
    Component.onCompleted:{BleeckerTheme.dark=typeof consumerDark!=="undefined" ? consumerDark:captureDark;BleeckerTheme.textScale=fixtureTextScale;BleeckerTheme.reducedMotion=true}
    RadioGroupCase {
        id:mainCase;objectName:"consumerRadioCase";x:24;y:30
        definition:window.model
        onSelectionRequested:value=>{
            window.calls++;window.requested=value;window.requests=window.requests.concat([value])
            if(!window.model.observeOnly)window.model=Object.assign({},window.model,{selection:value})
        }
    }
    BleeckerRadioGroup {
        objectName:"radioHorizontal";x:420;y:30;orientation:Qt.Horizontal
        selection:"monthly";options:window.model.options
    }
    BleeckerRadioGroup {
        objectName:"radioDisabled";x:420;y:120;enabled:false
        selection:"daily";options:[{value:"daily",label:"Daily"},{value:"weekly",label:"Weekly"}]
    }
    BleeckerRadioGroup {
        objectName:"radioNarrow";x:420;y:420;orientation:Qt.Horizontal;maximumWidth:100
        selection:"daily";options:[{value:"daily",label:"Daily"},{value:"weekly",label:"Weekly"},{value:"monthly",label:"Monthly"}]
    }
    BleeckerRadioGroup {
        objectName:"radioCanonical";x:420;y:230
        selection:"e\u0301";options:[{value:"é",label:"Canonical value"},{value:"",label:"Empty value"}]
    }
    BleeckerRadioGroup {
        objectName:"radioCustom";x:420;y:340
        selection:({key:"daily"});valueIdentity:value=>value.key
        options:[{value:{key:"daily",edition:1},label:"Object value"},{value:{key:"weekly",edition:7},label:"Weekly",disabled:true}]
    }
    BleeckerRadioGroup {
        objectName:"radioRtl";x:24;y:430;orientation:Qt.Horizontal
        selection:"daily";options:[{value:"daily",label:"Daily"},{value:"weekly",label:"Weekly"}]
        LayoutMirroring.enabled:true;LayoutMirroring.childrenInherit:true
    }
    BleeckerTextField {objectName:"radioOutsideField";x:24;y:540;width:320;placeholderText:"Continue editing"}
}
