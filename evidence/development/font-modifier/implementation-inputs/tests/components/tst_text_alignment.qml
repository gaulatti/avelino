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
        name:"NativeTextAlignment";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
        function cleanup(){BleeckerTheme.textScale=1}
        function make(role,text,rtl,scale,width){
            const button=role==="button"
            BleeckerTheme.textScale=scale
            const item=createTemporaryObject(button ? buttonFactory:fieldFactory,root,button ? {text:text,rtl:rtl,maximumWidth:28+width}:{role:role,sample:text,rtl:rtl,maximumWidth:68+width})
            verify(item)
            const label=findChild(item,button ? "bleeckerButtonLabel":role==="title" ? "bleeckerActivityTitle":role==="detail" ? "bleeckerActivityDetail":"bleeckerActivityTimestamp")
            verify(label)
            return {item:item,label:label,button:button}
        }
        function directionTarget(row){return make(row.style==="primary14" ? "title":row.style==="secondary12" ? "detail":row.style==="secondary10" ? "timestamp":"button",row.text,row.rtl,row.style==="primary20" ? 1.5:1,row.proposalWidth)}
        function offer(target,width){target.item.maximumWidth=(target.button ? 28:68)+width;if(!target.button)waitForPolish(findChild(target.item,"bleeckerActivityRow"));wait(2)}
        function assertFrame(target,rect,message){
            compare(target.label.width,rect.width,message+" width")
            compare(target.label.height,rect.height,message+" height")
            if(target.label.horizontalAlignment!==Qt.AlignLeft)compare(target.label.implicitWidth,rect.width,message+" fitted paint width")
        }
        function test_native_rtl_proposal_histories_data(){
            const groups={}
            for(const row of nativeTextDirectionQueries){
                if(!row.rtl || row.dpr!==metrics.devicePixelRatio)continue
                const key=row.style+"-"+row.text
                if(!groups[key])groups[key]={tag:key,rows:[]}
                groups[key].rows.push(row)
            }
            return Object.values(groups)
        }
        function test_native_rtl_proposal_histories(data){
            compare(data.rows.length,241)
            const target=directionTarget(data.rows[0])
            for(const row of data.rows){offer(target,row.proposalWidth);assertFrame(target,row.rect,row.text+" RTL at "+row.proposalWidth)}
        }
        function test_native_fresh_direction_cases_data(){return nativeTextDirectionFresh.filter(row=>row.dpr===metrics.devicePixelRatio).map((row,index)=>Object.assign({tag:String(index)},row))}
        function test_native_fresh_direction_cases(row){const target=directionTarget(row);offer(target,row.proposalWidth);assertFrame(target,row.rect,row.text+" fresh RTL="+row.rtl+" at "+row.proposalWidth)}
        function test_native_bare_alignment_cases_data(){return nativeTextAlignmentCases.filter(row=>row.dpr===metrics.devicePixelRatio).map((row,index)=>Object.assign({tag:String(index)},row))}
        function test_native_bare_alignment_cases(row){
            const role=row.key==="title" ? "title":row.key==="timestamp" ? "timestamp":row.key==="single-word" ? "button":"detail"
            const target=make(role,row.text,row.rtl,1,row.proposalWidth)
            target.label.horizontalAlignment=row.alignment==="center" ? Qt.AlignHCenter:(row.alignment==="leading")!==row.rtl ? Qt.AlignLeft:Qt.AlignRight
            offer(target,row.proposalWidth)
            assertFrame(target,row.bareRect,row.key+" "+row.alignment+" RTL="+row.rtl+" at "+row.proposalWidth)
        }
    }
}
