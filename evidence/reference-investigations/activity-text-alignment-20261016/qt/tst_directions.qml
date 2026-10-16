import QtQuick
import QtTest
import Avelino

Item {
    id:root;width:800;height:1200
    PixelAlignment {id:metrics;target:root}
    Component {
        id:fieldFactory
        BleeckerActivityItem {
            property string role:"title"
            property string sample:""
            property bool rtl:false
            title:role==="title" ? sample:""
            detail:role==="detail" ? sample:""
            timestamp:role==="timestamp" ? sample:""
            maximumWidth:68
            LayoutMirroring.enabled:rtl;LayoutMirroring.childrenInherit:true
        }
    }
    Component {
        id:buttonFactory
        BleeckerButton {
            property bool rtl:false
            text:"Review";size:"sm";variant:"secondary";maximumWidth:28
            LayoutMirroring.enabled:rtl;LayoutMirroring.childrenInherit:true
        }
    }
    TestCase {
        name:"DirectionMeasurements";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
        function cleanup(){BleeckerTheme.textScale=1}
        function profiles(){
            const rows=[]
            for(const rtl of [false,true])for(const p of [
                {style:"primary14",text:"Edition updated",key:"title"},
                {style:"secondary12",text:"Ready for review",key:"detail"},
                {style:"secondary10",text:"2 min ago",key:"timestamp"},
                {style:"primary13",text:"Review",key:"review"},
                {style:"primary13",text:"Archive",key:"archive"},
                {style:"primary20",text:"Review",key:"review"},
                {style:"primary20",text:"Archive",key:"archive"}])rows.push(Object.assign({tag:p.style+"-"+p.text+"-rtl"+rtl,rtl:rtl},p))
            return rows
        }
        function make(p,width){
            const button=["review","archive"].includes(p.key)
            BleeckerTheme.textScale=p.style==="primary20" ? 1.5:1
            const item=createTemporaryObject(button ? buttonFactory:fieldFactory,root,button ? {text:p.text,maximumWidth:28+width,rtl:p.rtl}:{role:p.key,sample:p.text,maximumWidth:68+width,rtl:p.rtl})
            verify(item)
            const label=findChild(item,button ? "bleeckerButtonLabel":p.key==="title" ? "bleeckerActivityTitle":p.key==="detail" ? "bleeckerActivityDetail":"bleeckerActivityTimestamp")
            verify(label)
            return {item:item,label:label,button:button}
        }
        function offer(target,width){target.item.maximumWidth=(target.button ? 28:68)+width;if(!target.button)waitForPolish(findChild(target.item,"bleeckerActivityRow"));wait(2)}
        function record(kind,p,target,width){console.log("RTL_MEASUREMENT "+JSON.stringify({kind:kind,style:p.style,text:p.text,rtl:p.rtl,dpr:metrics.devicePixelRatio,proposalWidth:width,width:target.label.width,height:target.label.height,wrapWidth:target.label.wrapWidth,horizontalAlignment:target.label.horizontalAlignment}))}
        function test_ascending_data(){return profiles()}
        function test_ascending(p){
            const target=make(p,0)
            for(let step=0;step<=240;step++){const width=step/2;offer(target,width);record("ascending",p,target,width)}
        }
        function test_fresh_data(){return profiles()}
        function test_fresh(p){
            for(const width of [12,26,38,39,39.5,40,40.5,54,160]){const target=make(p,width);offer(target,width);record("fresh",p,target,width);target.item.destroy()}
        }
    }
}
