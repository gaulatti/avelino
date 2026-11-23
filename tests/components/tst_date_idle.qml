import QtQuick
import QtTest
import Avelino

Item {
    id:root;width:640;height:400
    property real savedStart:1710000000.625
    property real savedEnd:1710864000.125
    property string ownerPolicy:"echo"
    property string style:"field"
    property var requests:[]
    property var pending:({})
    property bool mounted:true
    property bool controlEnabled:true
    property bool removeOnRequest:false
    readonly property Item picker:loader.item
    readonly property int requestCount:requests.length
    function receive(endpoint,value){
        requests=requests.concat([{endpoint:endpoint,value:value}])
        if(ownerPolicy==="echo"){if(endpoint==="start")savedStart=value;else savedEnd=value}
        else if(ownerPolicy==="delay")pending=Object.assign({},pending,{[endpoint]:value})
        if(removeOnRequest)mounted=false
    }
    Loader {
        id:loader;anchors.centerIn:parent;active:root.mounted
        sourceComponent:Component {BleeckerDateRangePicker {
            start:root.savedStart;end:root.savedEnd;pickerStyle:root.style;enabled:root.controlEnabled
            locale:Qt.locale("en_US");calendar:"gregorian";timeZone:"UTC"
            onStartRequested:value=>root.receive("start",value)
            onEndRequested:value=>root.receive("end",value)
        }}
    }
    TestCase {
        name:"DateIdleCommit";when:windowShown
        function init(){
            root.mounted=false;root.savedStart=1710000000.625;root.savedEnd=1710864000.125
            root.ownerPolicy="echo";root.style="field";root.requests=[];root.pending={}
            root.controlEnabled=true;root.removeOnRequest=false;root.mounted=true
            verify(root.picker!==null)
        }
        function cleanup(){root.mounted=false}
        function beginYear(endpoint){
            const input=root.picker[endpoint+"Input"]
            input.forceActiveFocus();tryCompare(input,"activeFocus",true)
            keyClick(Qt.Key_Right);keyClick(Qt.Key_Right);keyClick(Qt.Key_2)
            verify(root.picker[endpoint+"Field"].isTyping);compare(root.requestCount,0)
        }
        function test_idleRequests_data(){
            const rows=[]
            for(const style of ["field","stepperField"])for(const policy of ["echo","ignore","delay"])for(const endpoint of ["start","end"])
                rows.push({tag:style+"-"+policy+"-"+endpoint,style:style,policy:policy,endpoint:endpoint})
            return rows
        }
        function test_idleRequests(data){
            root.style=data.style;root.ownerPolicy=data.policy;beginYear(data.endpoint)
            wait(500);compare(root.requestCount,0)
            tryCompare(root,"requestCount",1,3000)
            const expected=data.endpoint==="start" ? -62098387199.375:-62097523199.875
            const original=data.endpoint==="start" ? 1710000000.625:1710864000.125
            compare(root.requests[0].endpoint,data.endpoint);compare(root.requests[0].value,expected)
            compare(root.picker[data.endpoint+"Field"].bufferValue,expected)
            compare(data.endpoint==="start" ? root.savedStart:root.savedEnd,data.policy==="echo" ? expected:original)
            compare(data.endpoint==="start" ? root.savedEnd:root.savedStart,data.endpoint==="start" ? 1710864000.125:1710000000.625)
            if(data.policy==="delay")compare(root.pending[data.endpoint],expected)
            keyClick(Qt.Key_Z,Qt.ControlModifier);keyClick(Qt.Key_Z,Qt.ControlModifier|Qt.ShiftModifier)
            compare(root.requestCount,1)
        }
        function test_newCharacterRestartsDeadline(){
            beginYear("start");wait(650);keyClick(Qt.Key_0);wait(650);compare(root.requestCount,0)
            tryCompare(root,"requestCount",1,3000)
        }
        function test_fieldEscapeKeepsIdleEdit(){
            beginYear("start");keyClick(Qt.Key_Escape);verify(root.picker.startField.isTyping)
            tryCompare(root,"requestCount",1,3000);compare(root.savedStart,-62098387199.375)
        }
        function test_externalValueCancelsPendingEdit(){
            beginYear("start");root.savedStart=1741536000.625;wait(1150)
            compare(root.requestCount,0);compare(root.picker.startField.bufferValue,1741536000.625)
        }
        function test_disabledFieldDoesNotPublish(){
            beginYear("start");root.controlEnabled=false;wait(1150);compare(root.requestCount,0)
            verify(!root.picker.startField.isTyping)
            root.controlEnabled=true;wait(1150);compare(root.requestCount,0)
        }
        function test_teardownCancelsPendingEdit(){
            beginYear("start");root.mounted=false;wait(1150);compare(root.requestCount,0)
        }
        function test_ownerCanRemovePickerDuringIdleRequest(){
            root.removeOnRequest=true;beginYear("start");tryCompare(root,"requestCount",1,3000)
            compare(root.picker,null)
        }
    }
}
