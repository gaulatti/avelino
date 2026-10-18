import QtQuick
import Avelino

Window {
    id:window
    width:640;height:400;visible:true
    color:BleeckerTheme.palette.background
    property real sourceStart:1710000000.625
    property real sourceEnd:1710864000.125
    property var bounds:null
    property string ownerPolicy:"echo"
    property string pickerStyle:"field"
    property bool disabled:false
    property bool rtl:false
    property string localeName:"en_US"
    property real callerWidth:-1
    property var requests:[]
    property var pending:({})
    property bool mounted:true
    property bool removeOnRequest:false
    readonly property Item picker:controlLoader.item
    function receive(endpoint:string,value:real):void {
        requests=requests.concat([{endpoint:endpoint,value:value,start:sourceStart,end:sourceEnd}])
        if(ownerPolicy==="echo"){if(endpoint==="start")sourceStart=value;else sourceEnd=value}
        else if(ownerPolicy==="delay")pending=Object.assign({},pending,{[endpoint]:value})
        if(removeOnRequest)mounted=false
    }
    Loader {
        id:controlLoader;anchors.centerIn:parent;active:window.mounted
        sourceComponent:Component {BleeckerDateRangePicker {
        id:control
        start:window.sourceStart;end:window.sourceEnd;range:window.bounds
        width:window.callerWidth<0 ? implicitWidth:window.callerWidth
        locale:Qt.locale(window.localeName);calendar:"gregorian";timeZone:"UTC"
        pickerStyle:window.pickerStyle
        enabled:!window.disabled
        LayoutMirroring.enabled:window.rtl
        onStartRequested:requestedValue=>window.receive("start",requestedValue)
        onEndRequested:requestedValue=>window.receive("end",requestedValue)
    }
    }}
}
