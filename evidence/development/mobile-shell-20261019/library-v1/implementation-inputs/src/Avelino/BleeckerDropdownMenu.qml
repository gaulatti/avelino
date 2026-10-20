import QtQuick
import QtQuick.Window
import QtQml.Models
import QtQuick.Templates as T

T.Control {
    id:control
    required property Component label
    property var items:[]
    property string controlSize:"regular"
    property bool componentReady:false
    readonly property int count:rows.count
    readonly property Item labelRoot:labelLoader.item
    readonly property Item presentationItem:trigger
    readonly property QtObject menu:popup
    readonly property QtObject labelMetadata:metadata
    readonly property real labelFontSize:controlSize==="mini" ? 9:controlSize==="small" ? 11:13
    readonly property color nativeForeground:BleeckerTheme.dark ? "white":"black"
    readonly property real naturalWidth:contentWidth+19
    readonly property real contentWidth:(metadata.hasText ? naturalText.implicitWidth:0)+metadata.imageWidth
        +(metadata.text.length>0&&metadata.imageSource.toString().length>0 ? 3.5:0)
    implicitWidth:naturalWidth
    implicitHeight:Math.max(labelFontSize+1,metadata.hasText ? naturalText.implicitHeight:0,metadata.imageHeight)
    padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus
    BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:naturalWidth
    Accessible.ignored:true
    function open():void {if(enabled&&count>0){popup.hasOpened=true;popup.open()}}
    function close():void {popup.close()}
    function itemAt(index:int):Item {return popup.itemAt(index)}
    function validate():void {
        metadata.controlFontSize(controlSize)
    }
    Component.onCompleted:{componentReady=true;validate()}
    onControlSizeChanged:if(componentReady)validate()
    function syncMenu():void {
        for(let index=0;index<delegates.count;++index){
            const item=delegates.objectAt(index)
            if(!item)continue
            let previous=-1
            for(let offset=0;offset<popup.count;++offset)if(popup.itemAt(offset)===item){previous=offset;break}
            if(previous>=0&&previous!==index)popup.moveItem(previous,index)
        }
    }
    function refreshMenu():void {syncMenu();menuMetrics.refresh()}
    MenuItems {id:rows;items:control.items;onChanged:Qt.callLater(control.refreshMenu)}
    Connections {target:rows;function onRowsMoved(){Qt.callLater(control.syncMenu)}}
    // This is a metadata context. Its descendants never receive pointer/focus
    // input or contribute decorative pixels to the native-style trigger.
    T.Control {
        id:labelContext;width:0;height:0;clip:true;opacity:0;enabled:false
        padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus
        font:metadata.systemFont(control.labelFontSize)
        palette.windowText:control.nativeForeground;palette.disabled.windowText:control.nativeForeground
        Accessible.ignored:true
        Loader {id:labelLoader;sourceComponent:control.label;Accessible.ignored:true}
    }
    DropdownLabel {id:metadata;root:labelLoader.item;defaultFont:labelContext.font}
    DropdownInput {menu:popup}
    Text {
        id:naturalText;visible:false
        text:metadata.text;font:metadata.textFont;textFormat:metadata.textFormat
        wrapMode:Text.NoWrap;renderType:Text.NativeRendering
        Accessible.ignored:true
    }
    T.Button {
        id:trigger;objectName:"bleeckerDropdownTrigger"
        x:(control.width-width)/2;y:(control.height-height)/2
        width:Math.max(0,Math.min(control.width,control.naturalWidth));height:control.implicitHeight
        padding:0;clip:true;focusPolicy:Qt.StrongFocus;autoRepeat:false
        background:Rectangle {
            color:"transparent";radius:3
            border.width:trigger.visualFocus ? 1:0;border.color:BleeckerTheme.palette.ring
        }
        onClicked:control.open()
        Keys.onDownPressed:control.open()
        Accessible.role:Accessible.ButtonMenu
        Accessible.name:control.Accessible.name.length ? control.Accessible.name:metadata.text
        contentItem:Item {
            opacity:control.enabled ? 1:0.35
            Image {
                id:image;objectName:"bleeckerDropdownImage"
                source:metadata.imageSource;width:metadata.imageWidth;height:metadata.imageHeight
                x:control.mirrored ? parent.width-3.5-width:3.5;y:(parent.height-height)/2
                fillMode:Image.PreserveAspectFit;Accessible.ignored:true
            }
            Text {
                objectName:"bleeckerDropdownTitle"
                readonly property real gap:metadata.imageSource.toString().length&&metadata.text.length>0 ? 3.5:0
                x:control.mirrored ? 15.5:3.5+metadata.imageWidth+gap
                width:Math.max(0,parent.width-19-metadata.imageWidth-gap)
                height:naturalText.implicitHeight;y:(parent.height-height)/2
                text:metadata.text;font:metadata.textFont;color:metadata.textColor;textFormat:metadata.textFormat
                wrapMode:Text.NoWrap;elide:Text.ElideRight;renderType:Text.NativeRendering
                horizontalAlignment:control.mirrored ? Text.AlignRight:Text.AlignLeft
                visible:metadata.hasText;Accessible.ignored:true
            }
            Canvas {
                objectName:"bleeckerDropdownIndicator";width:7;height:5
                x:control.mirrored ? 5.5:parent.width-12.5;y:(parent.height-height)/2
                property color ink:control.nativeForeground
                onInkChanged:requestPaint()
                onPaint:{const p=getContext("2d");p.reset();p.strokeStyle=ink;p.lineWidth=1.25;p.lineCap="round";p.lineJoin="round";p.beginPath();p.moveTo(1,1.25);p.lineTo(3.5,3.75);p.lineTo(6,1.25);p.stroke()}
                Accessible.ignored:true
            }
        }
    }
    T.Menu {
        id:popup;objectName:"bleeckerDropdownPopup"
        property bool hasOpened:false
        parent:trigger;popupType:T.Popup.Window;modal:true;dim:false;focus:true
        x:control.mirrored ? trigger.width-width:0;y:trigger.height
        padding:0;topPadding:5;bottomPadding:5;margins:0
        font:metadata.systemFont(13)
        implicitWidth:Math.min(Math.max(90,menuMetrics.width+20),control.Screen.desktopAvailableWidth)
        implicitHeight:list.implicitHeight+10
        height:implicitHeight
        closePolicy:T.Popup.CloseOnEscape|T.Popup.CloseOnPressOutside
        enter:null;exit:null
        background:Rectangle {
            color:BleeckerTheme.dark ? "#292929":"#fafafa";radius:11
            border.width:0.5;border.color:BleeckerTheme.dark ? "#606060":"#c5c5c5"
        }
        contentItem:ListView {
            id:list;implicitHeight:Math.min(contentHeight,Math.max(0,control.Screen.desktopAvailableHeight-10))
            model:popup.contentModel;clip:true;spacing:0;currentIndex:popup.currentIndex
            boundsBehavior:Flickable.StopAtBounds;interactive:contentHeight>height
            highlightMoveDuration:0;highlightResizeDuration:0
            T.ScrollIndicator.vertical:T.ScrollIndicator {
                implicitWidth:4;implicitHeight:24;visible:list.contentHeight>list.height
                contentItem:Rectangle {radius:2;color:BleeckerTheme.dark ? "#aaaaaa":"#666666"}
                background:null
            }
        }
        Instantiator {
            id:delegates;model:rows;active:popup.hasOpened
            delegate:T.MenuItem {
                id:menuRow
                required property int index
                required property string menuItemTitle
                required property BleeckerMenuItem menuItemObject
                required property string menuItemSystemImage
                required property bool menuItemDestructive
                required property string menuItemKey
                readonly property string systemImage:menuItemSystemImage
                readonly property bool destructive:menuItemDestructive
                readonly property string itemIdentity:menuItemKey
                readonly property real naturalWidth:measure.implicitWidth
                objectName:"bleeckerDropdownItem"+index
                text:menuItemTitle;enabled:control.enabled;hoverEnabled:true
                Accessible.name:text
                padding:0;font:popup.font;checkable:false;autoRepeat:false
                implicitWidth:naturalWidth+20;implicitHeight:Math.max(24,measure.implicitHeight+8)
                width:popup.availableWidth
                onIndexChanged:{if(pressed)rows.cancelPointer(menuRow);Qt.callLater(control.syncMenu)}
                onTriggered:{
                    const target=menuItemObject,permitted=control.enabled
                    popup.close()
                    if(permitted&&target)target.trigger()
                }
                Text {id:measure;visible:false;text:menuRow.text;font:menuRow.font;textFormat:Text.PlainText;renderType:Text.NativeRendering;Accessible.ignored:true}
                contentItem:Item {
                    Text {
                        text:menuRow.text;font:menuRow.font;textFormat:Text.PlainText
                        x:control.mirrored ? 6:14;width:Math.max(0,menuRow.width-20);height:measure.implicitHeight
                        y:(menuRow.height-height)/2;elide:Text.ElideRight;wrapMode:Text.NoWrap
                        renderType:Text.NativeRendering;horizontalAlignment:control.mirrored ? Text.AlignRight:Text.AlignLeft
                        color:menuRow.highlighted ? "white":control.nativeForeground
                        opacity:menuRow.enabled ? 1:0.35;Accessible.ignored:true
                    }
                }
                background:Rectangle {
                    x:5;width:Math.max(0,menuRow.width-10);height:menuRow.height;radius:5
                    color:menuRow.highlighted ? "#0063e1":"transparent"
                }
                indicator:null;arrow:null
                onNaturalWidthChanged:menuMetrics.refresh()
            }
            onObjectAdded:(index,object)=>{popup.insertItem(index,object);menuMetrics.refresh();Qt.callLater(control.syncMenu)}
            onObjectRemoved:(index,object)=>{popup.removeItem(object);menuMetrics.refresh();Qt.callLater(control.syncMenu)}
        }
    }
    QtObject {
        id:menuMetrics;property real width:0
        function refresh():void {let next=0;for(let index=0;index<delegates.count;++index){const item=delegates.objectAt(index);if(item)next=Math.max(next,item.naturalWidth)}width=next}
    }
}
