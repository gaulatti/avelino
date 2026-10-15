import QtQuick
import QtTest
import Avelino
Item {
    id:root;width:700;height:600
    property int mounts:0
    property int unmounts:0
    property int counter:0
    PixelAlignment {id:metrics;target:root}
    Component {
        id:factory
        BleeckerAlert {
            id:alert;title:"Edition ready"
            property bool rtl:false
            property bool largeSymbol:false
            LayoutMirroring.enabled:rtl;LayoutMirroring.childrenInherit:true
            icon:AlertGlyph {type:alert.type;color:alert.tone;implicitWidth:alert.largeSymbol ? (metrics.devicePixelRatio<2 ? 24:23):15;implicitHeight:implicitWidth}
            content:textContent
        }
    }
    Component {
        id:errorFactory
        BleeckerAlert {title:"Edition ready";type:"error";content:textContent}
    }
    Component {
        id:textContent
        ButtonLabel {
            property string message:"Create an edition to get started."
            text:message;font:parent.font;color:parent.foregroundColor;wrapWidth:parent.availableWidth
        }
    }
    Component {id:zero;Item {implicitWidth:0;implicitHeight:0}}
    Component {id:tall;Rectangle {implicitWidth:72;implicitHeight:90;color:BleeckerTheme.nativeRed}}
    Component {id:overflow;Item {implicitWidth:72;implicitHeight:90;Rectangle {x:-40;y:-40;width:72;height:90;color:BleeckerTheme.nativeRed}}}
    Component {
        id:action
        BleeckerButton {
            property int count:0
            text:"Create "+count;maximumWidth:parent.availableWidth
            onClicked:count++
            onCountChanged:root.counter=count
            Component.onCompleted:{root.mounts++;root.counter=count}
            Component.onDestruction:root.unmounts++
        }
    }
    TestCase {
        name:"AlertContract";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;BleeckerTheme.reducedMotion=true;root.mounts=0;root.unmounts=0;root.counter=0;failOnWarning(/Binding loop/)}
        function cleanup(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1}
        function test_native_bounds_data(){return nativeAlertCaptures.filter(c=>c.dpr===metrics.devicePixelRatio).map(c=>({tag:c.path,row:c}))}
        function test_native_bounds(data){
            const row=data.row;BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            const item=createTemporaryObject(row.alertType==="error" ? errorFactory:factory,root,{title:row.title,type:row.alertType,maximumWidth:row.variant==="intrinsic" ? -1:Number(row.size),enabled:!row.flag})
            if(row.variant==="rtl")item.rtl=true
            if(row.variant==="symbol-font20")item.largeSymbol=true
            if(row.contentMode==="empty")item.content=null
            if(row.contentMode==="zero")item.content=zero
            if(row.contentMode==="tall")item.content=tall
            if(row.contentMode==="overflow")item.content=overflow
            if(row.contentMode==="button")item.content=action
            if(row.contentMode==="text" || row.contentMode==="custom-font"){
                item.loadedContent.message=row.text
                if(row.contentMode==="custom-font"){
                    item.loadedContent.font.pointSize=BleeckerFonts.pointSizeForPixels(18);item.loadedContent.font.weight=Font.DemiBold;item.loadedContent.color=BleeckerTheme.nativeRed
                }
            }
            compare(item.presentationItem.width,row.componentSize.width);compare(item.presentationItem.height,row.componentSize.height)
            const title=findChild(item,"bleeckerAlertTitle");compare(title.resolvedPixelSize,14)
            if(row.contentMode==="text")compare(item.loadedContent.resolvedPixelSize,13)
        }
        function test_source_lifecycle_data(){return nativeAlertBehavior.map((row,i)=>({tag:"source-"+i,row:row}))}
        function test_source_lifecycle(data){
            const row=data.row;BleeckerTheme.dark=row.appearance==="dark";BleeckerTheme.textScale=row.textScale
            let item=createTemporaryObject(factory,root,{content:action,type:row.alertType,maximumWidth:320,enabled:row.action!=="disabled-click"})
            const first=item.loadedContent
            if(row.action==="outside-release"){mousePress(first);mouseMove(root,690,590);mouseRelease(root,690,590)}else mouseClick(first)
            if(row.action==="producer-update"){item.title="Updated alert title";item.type=row.alertType==="error" ? "success":"error";compare(item.loadedContent,first)}
            if(row.action==="replace"){item.content=textContent;wait(0);item.content=action;wait(0)}
            if(row.action==="reopen"){item.destroy();wait(0);item=createTemporaryObject(factory,root,{content:action,type:row.alertType,maximumWidth:320})}
            compare(root.counter,row.counter);compare(root.mounts,row.mounts);compare(root.unmounts,row.unmounts)
            compare(item.title,row.titleAfterAction);compare(item.type,row.typeAfterAction)
        }
        function test_outer_frame_and_updates(){
            const item=createTemporaryObject(factory,root,{maximumWidth:320,width:400,height:200})
            compare(item.presentationItem.width,246);compare(item.presentationItem.x,77);compare(item.presentationItem.y,67.5)
            const first=item.loadedContent;item.title="Updated title";item.type="success";compare(item.loadedContent,first)
            compare(first.font.family,"Libre Franklin");compare(first.color,BleeckerTheme.palette.textPrimary)
            BleeckerTheme.dark=true;compare(first.color,BleeckerTheme.palette.textPrimary)
            item.maximumWidth=180;verify(item.presentationItem.width<=180);verify(item.presentationItem.height>65)
        }
    }
}
