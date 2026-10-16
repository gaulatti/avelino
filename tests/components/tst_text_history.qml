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
            title:role==="title" ? sample:""
            detail:role==="detail" ? sample:""
            timestamp:role==="timestamp" ? sample:""
            maximumWidth:68
        }
    }
    Component {id:buttonFactory;BleeckerButton {text:"Review";size:"sm";variant:"secondary";maximumWidth:28}}
    TestCase {
        name:"TextProposalHistory";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
        function cleanup(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
        function create(key,text,width){
            const button=["review","archive"].includes(key)
            const item=createTemporaryObject(button ? buttonFactory:fieldFactory,root,button ? {text:text,maximumWidth:28+width}:{role:key.startsWith("title") ? "title":key,sample:text,maximumWidth:68+width})
            verify(item)
            return {item:item,button:button,label:findChild(item,button ? "bleeckerButtonLabel":key.startsWith("title") ? "bleeckerActivityTitle":key==="detail" ? "bleeckerActivityDetail":"bleeckerActivityTimestamp")}
        }
        function offer(target,width){target.item.maximumWidth=(target.button ? 28:68)+width;if(!target.button)waitForPolish(findChild(target.item,"bleeckerActivityRow"));wait(2)}
        function test_original_public_text_queries_data(){
            const groups={}
            for(const row of nativeTextLayoutQueries){
                if(row.dpr!==metrics.devicePixelRatio)continue
                const key=row.style+"-"+row.text
                if(!groups[key])groups[key]={tag:key,rows:[]}
                groups[key].rows.push(row)
            }
            return Object.values(groups)
        }
        function test_original_public_text_queries(data){
            compare(data.rows.length,241)
            const first=data.rows[0],key=first.style==="primary14" ? "title":first.style==="secondary12" ? "detail":first.style==="secondary10" ? "timestamp":first.text.toLowerCase()
            BleeckerTheme.textScale=first.style==="primary20" ? 1.5:1
            const target=create(key,first.text,0)
            for(const row of data.rows){
                offer(target,row.proposalWidth)
                compare(target.label.width,row.native.width,key+" width at "+row.proposalWidth)
                compare(target.label.height,row.native.height,key+" height at "+row.proposalWidth)
            }
        }
        function test_fresh_growing_shrinking_and_revisited_widths_data(){return nativeTextLayoutHistory.filter(t=>t.dpr===metrics.devicePixelRatio).map(t=>({tag:t.key+"-"+t.sequence,trace:t}))}
        function test_fresh_growing_shrinking_and_revisited_widths(data){
            const trace=data.trace,target=create(trace.key,trace.text,trace.events[0].proposalWidth)
            for(const event of trace.events){
                offer(target,event.proposalWidth)
                compare(target.label.width,event.rect.width,trace.key+" history width "+event.proposalWidth)
                compare(target.label.height,event.rect.height,trace.key+" history height "+event.proposalWidth)
            }
        }
        function test_new_text_and_font_invalidate_previous_measurements(){
            const target=create("review","Review",9.5);offer(target,10);compare(target.label.height,metrics.devicePixelRatio===1 ? 96:80)
            target.item.text="Archive";offer(target,10);target.item.text="Review";offer(target,10);compare(target.label.height,80)
            BleeckerTheme.textScale=1.5;offer(target,10);BleeckerTheme.textScale=1;offer(target,10);compare(target.label.height,80)
        }
    }
}
