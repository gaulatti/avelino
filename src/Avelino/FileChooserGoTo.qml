import QtQuick
import QtQuick.Window
import QtQuick.Templates as T

FileChooserDialogBase {
    id:prompt
    required property FileChooserBrowser browser
    readonly property bool dark:BleeckerTheme.dark
    readonly property Item pathInput:path
    readonly property FileChooserPaths suggestions:FileChooserPaths {}
    modal:true;dim:false;focus:true;popupType:T.Popup.Window
    width:Math.min(460,parent ? parent.Screen.desktopAvailableWidth:460)
    height:Math.min(345,parent ? parent.Screen.desktopAvailableHeight:345)
    x:parent ? (parent.width-width)/2:0;y:40
    padding:0;margins:0;header:null;footer:null;title:"Go to Folder"
    closePolicy:T.Popup.CloseOnEscape;enter:null;exit:null
    background:Rectangle {radius:14;color:prompt.dark ? "#303030":"#fafafa";border.width:0.5;border.color:prompt.dark ? "#575757":"#dedede"}
    function submit():void {
        const target=suggestions.selectedUrl
        if(!target.toString().length)return
        const input=suggestions.input
        if(!browser.choosePath(target)){suggestions.refresh();return}
        browser.places.rememberPathNavigation(input,target)
        close()
    }
    onOpened:{
        browser.refreshPlaces()
        suggestions.begin(browser.folderPath,browser.places.hasPathInput ? browser.places.lastPathInput:browser.folderPath,browser.places.pathTargets,browser.places.error)
        path.text=suggestions.input;path.forceActiveFocus();path.selectAll()
    }
    Connections {
        target:prompt.browser
        function onActiveChanged(){if(!prompt.browser.active)prompt.close()}
    }
    contentItem:Item {
        Keys.onEscapePressed:event=>{prompt.close();event.accepted=true}
        T.TextField {
            id:path;objectName:"bleeckerFileChooserGoToPath"
            x:16;y:3;width:Math.max(0,parent.width-60);height:30
            padding:0;selectByMouse:true;clip:true;placeholderText:"Go to Folder"
            font.family:Qt.application.font.family;font.pixelSize:15
            color:prompt.dark ? "#eeeeee":"#222222";placeholderTextColor:prompt.dark ? "#999999":"#b7b7b7"
            selectionColor:"#b9d9ff";selectedTextColor:color;background:null
            Accessible.name:"Go to Folder";Accessible.description:"Folder or file path"
            onTextEdited:prompt.suggestions.input=text
            onAccepted:prompt.submit()
            Keys.onPressed:event=>{
                if(event.key===Qt.Key_Escape){prompt.close();event.accepted=true}
                else if(event.key===Qt.Key_Down||event.key===Qt.Key_Up){prompt.suggestions.move(event.key===Qt.Key_Down ? 1:-1);event.accepted=true}
                else if(event.key===Qt.Key_Tab){text=prompt.suggestions.completion();cursorPosition=text.length;prompt.suggestions.input=text;event.accepted=true}
            }
        }
        FileChooserButton {
            id:clear;objectName:"bleeckerFileChooserGoToClear"
            x:parent.width-34;y:8;width:20;height:20;implicitWidth:20;implicitHeight:20;padding:0
            text:"×";Accessible.name:"Close";Accessible.description:path.text.length ? "Clear the path":"Close Go to Folder"
            background:Rectangle {x:3;y:3;width:14;height:14;radius:7;color:prompt.dark ? "#999999":"#858585"}
            contentItem:Text {text:clear.text;color:"white";font.pixelSize:14;horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter;Accessible.ignored:true}
            onClicked:{if(!path.text.length){prompt.close();return}path.clear();prompt.suggestions.input="";path.forceActiveFocus()}
        }
        Rectangle {x:0;y:35;width:parent.width;height:0.5;color:prompt.dark ? "#575757":"#dedede";Accessible.ignored:true}
        ListView {
            id:targets;objectName:"bleeckerFileChooserGoToTargets"
            x:10;y:46;width:parent.width-20;height:Math.max(0,parent.height-y-12-(error.visible ? 28:0))
            clip:true;model:prompt.suggestions.entries;currentIndex:prompt.suggestions.currentIndex
            boundsBehavior:Flickable.StopAtBounds;highlightMoveDuration:0;highlightResizeDuration:0
            Accessible.role:Accessible.List;Accessible.name:"Folder suggestions"
            delegate:T.ItemDelegate {
                id:entry
                required property int index
                required property var modelData
                objectName:"bleeckerFileChooserGoToTarget_"+index
                width:targets.width;height:22;padding:0;focusPolicy:Qt.NoFocus
                enabled:!modelData.heading&&modelData.available
                highlighted:index===prompt.suggestions.currentIndex
                Accessible.role:modelData.heading ? Accessible.Heading:Accessible.ListItem
                Accessible.name:modelData.heading ? modelData.label:modelData.path
                Accessible.selected:highlighted;Accessible.selectable:enabled
                Accessible.onPressAction:prompt.suggestions.select(index)
                onClicked:prompt.suggestions.select(index)
                onDoubleClicked:{prompt.suggestions.select(index);prompt.submit()}
                background:Rectangle {radius:4;color:entry.highlighted ? "#0063e1":"transparent"}
                contentItem:Text {
                    leftPadding:8;rightPadding:8;verticalAlignment:Text.AlignVCenter
                    text:entry.modelData.heading ? entry.modelData.label:entry.modelData.path==="/" ? "/":entry.modelData.path.split('/').filter(part=>part.length).join("  ›  ")
                    textFormat:Text.PlainText;elide:Text.ElideMiddle
                    font.family:Qt.application.font.family;font.pixelSize:entry.modelData.heading ? 11.5:13
                    font.weight:entry.modelData.heading ? Font.DemiBold:Font.Normal
                    color:entry.highlighted ? "white":entry.modelData.heading ? prompt.dark ? "#aaaaaa":"#999999":prompt.dark ? "#eeeeee":"#222222"
                    opacity:entry.modelData.heading||entry.modelData.available ? 1:0.4;Accessible.ignored:true
                }
            }
            T.ScrollBar.vertical:T.ScrollBar {
                objectName:"bleeckerFileChooserGoToScrollBar"
                width:7;policy:T.ScrollBar.AsNeeded;visible:policy===T.ScrollBar.AlwaysOn||(policy===T.ScrollBar.AsNeeded&&size<1)
                contentItem:Rectangle {radius:3;color:"#999999";implicitWidth:5;implicitHeight:24}
                background:null
            }
        }
        Text {
            id:error;objectName:"bleeckerFileChooserGoToError"
            x:18;y:parent.height-32;width:parent.width-36;height:24;visible:text.length>0
            text:prompt.suggestions.error;textFormat:Text.PlainText;wrapMode:Text.Wrap
            font.family:Qt.application.font.family;font.pixelSize:12;color:prompt.dark ? "#eeeeee":"#222222"
            Accessible.name:text;Accessible.role:Accessible.StaticText
        }
    }
}
