import QtQuick
import QtQuick.Templates as T

FocusScope {
    id:host
    required property FileChooserBrowser browser
    property Item resultsView
    readonly property Item input:editor
    readonly property bool dark:BleeckerTheme.dark
    property int suggestion:-1
    property real suggestionOffset:28
    implicitWidth:198;implicitHeight:24
    FileChooserSearchText {
        id:editor;objectName:"bleeckerFileChooserSearch"
        anchors.fill:parent;focus:true;activeFocusOnTab:true
        text:host.browser.search.query
        tokenMode:host.browser.search.mode
        onTokenModeChanged:if(host.browser.search.mode!==tokenMode)host.browser.search.mode=tokenMode
        leftPadding:host.browser.search.mode==="general" ? 26:94;rightPadding:25
        verticalAlignment:Text.AlignVCenter;selectByMouse:true
        font.family:Qt.application.font.family;font.pixelSize:13
        color:host.dark ? "#eeeeee":"#222222";selectionColor:"#a6cef5";selectedTextColor:"#111111"
        Accessible.name:"Search"
        Accessible.description:host.browser.search.mode==="filename" ? "Search filenames":"Search names and contents"
        KeyNavigation.tab:host.resultsView
        onTextEdited:{host.suggestion=-1;host.browser.search.query=text}
        Keys.onDownPressed:{if(suggestions.visible)host.suggestion=Math.min(1,host.suggestion+1);else if(host.resultsView)host.resultsView.forceActiveFocus()}
        Keys.onUpPressed:if(suggestions.visible)host.suggestion=Math.max(0,host.suggestion-1)
        Keys.onReturnPressed:{
            if(suggestions.visible&&host.suggestion>=0)host.browser.search.mode=host.suggestion===0 ? "filename":"everything"
            else if(host.resultsView)host.resultsView.forceActiveFocus()
        }
        Keys.onEscapePressed:event=>{
            if(text.length){host.browser.search.clear();host.suggestion=-1;event.accepted=true}
            else event.accepted=false
        }
        background:Rectangle {
            radius:6;color:host.dark ? "#252525":"#eeeeee"
            border.width:editor.activeFocus ? 2:0.5;border.color:editor.activeFocus ? "#80baff":host.dark ? "#575757":"#c6c6c6"
        }
        InputGlyph {x:8;y:5;width:14;height:14;symbol:"search";color:host.dark ? "#aaaaaa":"#777777";visible:host.browser.search.mode==="general"}
        FileChooserButton {
            id:mode;objectName:"bleeckerFileChooserSearchToken";x:4;y:3;width:86;height:18;implicitHeight:18
            visible:host.browser.search.mode!=="general"
            text:host.browser.search.mode==="filename" ? "Filename ▾":"Everything ▾"
            Accessible.name:host.browser.search.mode==="filename" ? "Filename: "+editor.text:"Everything: "+editor.text
            Accessible.role:Accessible.ButtonMenu
            accessibilityMenu:modeMenu
            Accessible.onPressAction:mode.click()
            onClicked:modeMenu.open()
            FileChooserMenuBase {
                id:modeMenu;objectName:"bleeckerFileChooserSearchModeMenu";parent:mode;opener:mode
                y:22;width:150;padding:4;popupType:T.Popup.Item;enter:null;exit:null
                implicitHeight:contentItem.implicitHeight+topPadding+bottomPadding
                background:Rectangle {radius:6;color:host.dark ? "#303030":"white";border.width:0.5;border.color:"#888888"}
                contentItem:ListView {implicitHeight:contentHeight;model:modeMenu.contentModel;interactive:false}
                component ModeOption:T.MenuItem {
                    id:option
                    required property string value
                    objectName:"bleeckerFileChooserSearchMode_"+value
                    width:142;height:25;implicitHeight:25;checkable:true;checked:host.browser.search.mode===value
                    text:value==="filename" ? "Filename":"Everything"
                    Accessible.role:Accessible.MenuItem;Accessible.name:text;Accessible.checked:checked;Accessible.checkable:true
                    Accessible.onPressAction:option.click()
                    onTriggered:host.browser.search.mode=value
                    contentItem:Text {text:option.text;color:host.dark ? "white":"#222222";font.pixelSize:13;verticalAlignment:Text.AlignVCenter;leftPadding:8}
                    background:Rectangle {color:option.highlighted ? "#a6cef5":"transparent";radius:4}
                    indicator:null
                }
                ModeOption {value:"filename"}
                ModeOption {value:"everything"}
            }
        }
        T.Button {
            objectName:"bleeckerFileChooserSearchClear";anchors.right:parent.right;anchors.rightMargin:4;y:3;width:18;height:18
            visible:editor.text.length>0;text:"×";focusPolicy:Qt.NoFocus
            Accessible.name:"Clear search";onClicked:{host.browser.search.clear();host.suggestion=-1;editor.forceActiveFocus()}
            background:Rectangle {radius:9;color:host.dark ? "#888888":"#999999"}
            contentItem:Item {InputGlyph {anchors.centerIn:parent;width:9;height:9;symbol:"clear";color:"white"}}
        }
    }
    T.Popup {
        id:suggestions;objectName:"bleeckerFileChooserSearchSuggestions";parent:host
        x:Math.min(0,host.width-width);y:host.suggestionOffset;width:260;padding:5
        implicitHeight:contentItem.implicitHeight+topPadding+bottomPadding
        visible:host.visible&&editor.activeFocus&&editor.text.length>0&&host.browser.search.mode==="general"
        focus:false;modal:false;dim:false;popupType:T.Popup.Item;enter:null;exit:null
        closePolicy:T.Popup.NoAutoClose
        background:Rectangle {radius:7;color:host.dark ? "#303030":"white";border.width:0.5;border.color:host.dark ? "#575757":"#c6c6c6"}
        contentItem:Column {
            Repeater {
                model:[{heading:"Filenames",mode:"filename",prefix:"Name Contains “"},{heading:"Content",mode:"everything",prefix:"Contains “"}]
                delegate:Column {
                    required property var modelData
                    required property int index
                    width:250
                    Text {x:8;height:22;text:parent.modelData.heading;color:host.dark ? "#aaaaaa":"#777777";font.pixelSize:11;verticalAlignment:Text.AlignVCenter}
                    T.ItemDelegate {
                        id:choice;objectName:"bleeckerFileChooserSearchSuggestion_"+parent.index
                        width:250;height:27;focusPolicy:Qt.NoFocus
                        text:parent.modelData.prefix+editor.text+"”";highlighted:host.suggestion===parent.index
                        Accessible.name:text;Accessible.role:Accessible.MenuItem
                        onClicked:host.browser.search.mode=parent.modelData.mode
                        background:Rectangle {radius:4;color:choice.highlighted ? "#0063e1":"transparent"}
                        contentItem:Text {leftPadding:8;rightPadding:8;text:choice.text;textFormat:Text.PlainText;elide:Text.ElideMiddle;font.pixelSize:13;color:choice.highlighted ? "white":host.dark ? "#eeeeee":"#222222";verticalAlignment:Text.AlignVCenter;Accessible.ignored:true}
                    }
                }
            }
        }
    }
}
