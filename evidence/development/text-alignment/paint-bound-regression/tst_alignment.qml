import QtQuick
import QtTest
import Avelino
import "rows.js" as Native

Item {
    id:root;width:800;height:1200
    PixelAlignment {id:metrics;target:root}
    Component {
        id:fields
        BleeckerActivityItem {
            property string role:"detail"
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
        id:button
        BleeckerButton {
            property bool rtl:false
            text:"Review";size:"sm";variant:"secondary";maximumWidth:28
            LayoutMirroring.enabled:rtl;LayoutMirroring.childrenInherit:true
        }
    }
    TestCase {
        name:"PublicTextPaintBounds";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;failOnWarning(/Binding loop/)}
        function test_bare_native_text_data(){return Native.rows.filter(row=>row.dpr===metrics.devicePixelRatio)}
        function test_bare_native_text(row){
            const isButton=row.key==="single-word"
            const role=row.key==="title" ? "title":row.key==="timestamp" ? "timestamp":"detail"
            const item=createTemporaryObject(isButton ? button:fields,root,isButton ? {text:row.text,maximumWidth:28+row.proposalWidth,rtl:row.rtl}:{role:role,sample:row.text,maximumWidth:68+row.proposalWidth,rtl:row.rtl})
            verify(item)
            const label=findChild(item,isButton ? "bleeckerButtonLabel":role==="title" ? "bleeckerActivityTitle":role==="timestamp" ? "bleeckerActivityTimestamp":"bleeckerActivityDetail")
            verify(label)
            label.horizontalAlignment=row.alignment==="center" ? Qt.AlignHCenter:(row.alignment==="leading")!==row.rtl ? Qt.AlignLeft:Qt.AlignRight
            if(!isButton)waitForPolish(findChild(item,"bleeckerActivityRow"))
            wait(2)
            compare(label.width,row.bareRect.width,row.key+" "+row.alignment+" width "+row.proposalWidth)
            if(label.horizontalAlignment!==Qt.AlignLeft)compare(label.implicitWidth,row.bareRect.width,row.key+" fitted paint width "+row.proposalWidth)
            compare(label.height,row.bareRect.height,row.key+" "+row.alignment+" height "+row.proposalWidth)
        }
    }
}
