import QtQuick
import QtQuick.Templates as T
import Avelino

Item {
    id:root;width:600;height:300
    property var configuration:({id:"default",title:"Actions",label:"text",itemMode:"normal"})
    property var actions:[]
    property int labelActions:0
    property bool removeOnAction:false
    property bool ready:false
    property var entries:[]
    readonly property Item control:menu
    component Entry:BleeckerMenuItem {
        required property string callKey
        onTriggered:{root.actions=root.actions.concat(callKey);if(root.removeOnAction)root.entries=[]}
    }
    Component {id:entryFactory;Entry {}}
    function definitions():var {
        if(configuration.empty)return []
        switch(configuration.itemMode){
        case "single":return [{title:"Open",systemImage:"folder",key:"open"}]
        case "many":return Array.from({length:40},(_,i)=>({title:"Command "+String(i).padStart(2,"0"),key:"command-"+i}))
        case "long":return [{title:"A long menu action with enough words to measure native fitting",systemImage:"folder",key:"long"},{title:"Acción 日本語 العربية",destructive:true,key:"unicode"}]
        case "duplicate-titles":return Array.from({length:3},(_,i)=>({title:"Repeated",key:"repeated-"+i}))
        default:{
            const result=[{title:"Open",systemImage:"folder",key:"open"},{title:"Duplicate",key:"duplicate"},{title:"Remove",systemImage:"trash",destructive:true,key:"remove"}]
            if(configuration.itemMode==="destructive")for(const item of result)item.destructive=true
            if(configuration.itemMode==="no-symbols")for(const item of result)delete item.systemImage
            return result
        }
        }
    }
    function rebuild():void {
        const previous=entries,next=[]
        for(const value of definitions())next.push(entryFactory.createObject(root,{title:value.title,systemImage:value.systemImage===undefined ? null:value.systemImage,destructive:value.destructive===true,callKey:value.key}))
        entries=next
        for(const item of previous)item.destroy()
    }
    function labelComponent():Component {
        switch(configuration.label){
        case "icon":return iconLabel
        case "rect":return rectangleLabel
        case "stack":return stackLabel
        case "flat":return flatLabel
        case "empty":return emptyLabel
        case "button":return buttonLabel
        case "explicit-font":return fontLabel
        case "explicit-red":return redLabel
        default:return textLabel
        }
    }
    function frame():var {
        function geometry(item){const point=item.mapToItem(root,0,0);return {x:point.x,y:point.y,width:item.width,height:item.height}}
        return {body:geometry(menu.presentationItem),caller:geometry(menu),label:menu.labelRoot ? geometry(menu.labelRoot):null}
    }
    function state():var {
        const values=[]
        for(let index=0;index<menu.count;++index){const item=menu.items[index];values.push({title:item.title,systemImage:item.systemImage===null||item.systemImage===undefined ? "circle":item.systemImage,destructive:item.destructive})}
        return {title:menu.labelMetadata.text,enabled:menu.enabled,actions:actions,labelActions:labelActions,count:menu.count,
            items:values,distinctIdentities:new Set(menu.items.map(item=>item.id)).size,
            popupVisible:menu.menu.visible,popupBuiltCount:menu.menu.count,
            implicitWidth:menu.implicitWidth,implicitHeight:menu.implicitHeight,
            nativeLabelBuilderAcceptance:"pending",nativeItemIdentityUpdatesAcceptance:"pending",
            nativePopupPresentationAcceptance:"pending",physicalInputAcceptance:"pending",readerAcceptance:"pending"}
    }
    Component.onCompleted:{ready=true;rebuild()}
    onConfigurationChanged:if(ready)rebuild()
    Component {id:textLabel;BleeckerText {text:root.configuration.title===undefined ? "Actions":root.configuration.title}}
    Component {id:fontLabel;BleeckerText {text:root.configuration.title;font.pixelSize:28;font.weight:Font.Bold}}
    Component {id:redLabel;BleeckerText {text:root.configuration.title;color:BleeckerTheme.nativeRed}}
    Component {id:iconLabel;DropdownMenuImage {systemImage:root.configuration.symbol||"ellipsis"}}
    Component {id:rectangleLabel;Rectangle {width:80;height:30;color:"orange"}}
    Component {id:emptyLabel;Item {width:0;height:0}}
    Component {id:buttonLabel;T.Button {text:root.configuration.title;onClicked:root.labelActions++}}
    Component {
        id:stackLabel
        Item {DropdownMenuImage {systemImage:"folder"} BleeckerText {text:root.configuration.title;x:25}}
    }
    Component {
        id:flatLabel
        Item {BleeckerText {text:root.configuration.title} Rectangle {width:24;height:12;color:"orange"}}
    }
    BleeckerDropdownMenu {
        id:menu;objectName:"caseDropdownMenu"
        x:(root.width-width)/2;y:(root.height-height)/2
        width:root.configuration.width===undefined||root.configuration.width===null ? implicitWidth:root.configuration.width
        height:root.configuration.height===undefined||root.configuration.height===null ? implicitHeight:root.configuration.height
        items:root.entries;label:root.labelComponent()
        enabled:root.configuration.disabled!==true
        controlSize:root.configuration.controlSize||"regular"
        LayoutMirroring.enabled:root.configuration.rtl===true;LayoutMirroring.childrenInherit:true
        font:Qt.font({family:Qt.application.font.family,pixelSize:root.configuration.parentFont ? 28:13,weight:root.configuration.parentFont ? Font.Bold:Font.Normal})
        palette.windowText:root.configuration.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.palette.textPrimary
    }
}
