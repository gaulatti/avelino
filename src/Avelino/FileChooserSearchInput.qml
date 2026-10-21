import QtQuick
import QtQuick.Templates as T

FocusScope {
    id:host
    objectName:"bleeckerFileChooserSearchHost"
    required property FileChooserBrowser browser
    property Item resultsView
    readonly property Item input:editor
    readonly property bool dark:BleeckerTheme.dark
    property int suggestion:-1
    property bool suggestionsDismissed:false
    property real suggestionOffset:28
    implicitWidth:198;implicitHeight:24
    function commit(mode) { suggestion=-1; editor.commitDraft(mode) }
    Rectangle {
        anchors.fill:parent;radius:6;color:host.dark ? "#252525":"#eeeeee"
        border.width:editor.activeFocus ? 2:0.5;border.color:editor.activeFocus ? "#80baff":host.dark ? "#575757":"#c6c6c6"
    }
    MouseArea {anchors.fill:parent;onPressed:editor.forceActiveFocus()}
    InputGlyph {x:8;y:5;width:14;height:14;symbol:"search";color:host.dark ? "#aaaaaa":"#777777";visible:editor.tokens.count===0}
    Flickable {
        id:viewport;objectName:"bleeckerFileChooserSearchViewport"
        x:editor.tokens.count ? 4:26;y:2
        width:host.width-x-25;height:host.height-4
        clip:true;interactive:false;boundsBehavior:Flickable.StopAtBounds
        contentWidth:editor.width;contentHeight:height
        function ensureCursor() {
            const rectangle=editor.cursorRectangle
            if(rectangle.x<contentX)contentX=rectangle.x
            else if(rectangle.x+rectangle.width>contentX+width)contentX=rectangle.x+rectangle.width-width
            contentX=Math.max(0,Math.min(contentX,contentWidth-width))
        }
        FileChooserSearchText {
            id:editor;objectName:"bleeckerFileChooserSearch"
            width:Math.max(viewport.width,contentWidth+2);height:viewport.height
            focus:true;activeFocusOnTab:true
            expression:host.browser.search.expression
            onExpressionChanged:host.browser.search.expression=expression
            onDraftChanged:{host.suggestion=-1;host.suggestionsDismissed=false}
            onCursorRectangleChanged:viewport.ensureCursor()
            onTokenLayoutChanged:viewport.ensureCursor()
            leftPadding:0;rightPadding:0;topPadding:0;bottomPadding:0
            verticalAlignment:Text.AlignVCenter;selectByMouse:true
            font.family:Qt.application.font.family;font.pixelSize:13
            color:host.dark ? "#eeeeee":"#222222";selectionColor:"#a6cef5";selectedTextColor:"#111111"
            Accessible.name:"Search";Accessible.role:Accessible.EditableText
            Accessible.description:"Search names and contents with independent Filename and Everything tokens"
            KeyNavigation.tab:host.resultsView
            Keys.onDownPressed:{if(suggestions.visible)host.suggestion=Math.min(1,host.suggestion+1);else if(host.resultsView)host.resultsView.forceActiveFocus()}
            Keys.onUpPressed:if(suggestions.visible)host.suggestion=Math.max(0,host.suggestion-1)
            Keys.onReturnPressed:{
                if(suggestions.visible&&host.suggestion>=0)host.commit(host.suggestion===0 ? "filename":"everything")
                else if(host.resultsView)host.resultsView.forceActiveFocus()
            }
            Keys.onEscapePressed:event=>{
                if(suggestions.visible){host.suggestionsDismissed=true;event.accepted=true}
                else if(expression.length){host.browser.search.clear();host.suggestion=-1;event.accepted=true}
                else event.accepted=false
            }
            background:null
            Repeater {
                model:editor.tokens
                delegate:FileChooserButton {
                    id:chip
                    required property var token
                    required property int index
                    objectName:"bleeckerFileChooserSearchToken"+(index ? "_"+index:"")
                    x:token.x;y:token.y;width:token.width;height:token.height;implicitHeight:18
                    focusPolicy:Qt.NoFocus;text:token.label+" ▾"
                    readonly property bool tokenSelected:editor.selectionStart<=token.position&&editor.selectionEnd>token.position
                    fillColor:tokenSelected ? "#a6cef5":host.dark ? "#555555":"#dddddd"
                    contentItem:Text {
                        text:chip.text;font:chip.font;textFormat:Text.PlainText
                        horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter
                        color:chip.tokenSelected ? editor.selectedTextColor:chip.dark ? "white":"#222222"
                        opacity:chip.enabled ? 1:0.35;Accessible.ignored:true
                    }
                    Accessible.name:token.label;Accessible.role:Accessible.ButtonMenu
                    accessibilityMenu:modeMenu
                    Accessible.onPressAction:chip.click()
                    onClicked:modeMenu.open()
                    FileChooserMenuBase {
                        id:modeMenu;parent:chip;opener:chip
                        objectName:"bleeckerFileChooserSearchModeMenu"+(chip.index ? "_"+chip.index:"")
                        y:chip.height+4;width:150;padding:4;popupType:T.Popup.Item;enter:null;exit:null
                        onClosed:editor.forceActiveFocus()
                        implicitHeight:contentItem.implicitHeight+topPadding+bottomPadding
                        background:Rectangle {radius:6;color:host.dark ? "#303030":"white";border.width:0.5;border.color:"#888888"}
                        contentItem:ListView {implicitHeight:contentHeight;model:modeMenu.contentModel;interactive:false}
                        component ModeOption:T.MenuItem {
                            id:option
                            required property string value
                            objectName:"bleeckerFileChooserSearchMode_"+value+(chip.index ? "_"+chip.index:"")
                            width:142;height:25;implicitHeight:25;checkable:true;checked:chip.token.mode===value
                            text:value==="filename" ? "Filename":"Everything"
                            Accessible.role:Accessible.MenuItem;Accessible.name:text;Accessible.checked:checked;Accessible.checkable:true
                            Accessible.onPressAction:option.click()
                            onTriggered:{const position=chip.token.position;modeMenu.close();editor.setTokenModeAt(position,value)}
                            contentItem:Text {text:option.text;color:host.dark ? "white":"#222222";font.pixelSize:13;verticalAlignment:Text.AlignVCenter;leftPadding:8}
                            background:Rectangle {color:option.highlighted ? "#a6cef5":"transparent";radius:4}
                            indicator:null
                        }
                        ModeOption {value:"filename"}
                        ModeOption {value:"everything"}
                    }
                }
            }
        }
    }
    T.Button {
        objectName:"bleeckerFileChooserSearchClear";anchors.right:parent.right;anchors.rightMargin:4;y:3;width:18;height:18
        visible:editor.expression.length>0;text:"×";focusPolicy:Qt.NoFocus
        Accessible.name:"Clear search";onClicked:{host.browser.search.clear();host.suggestion=-1;editor.forceActiveFocus()}
        background:Rectangle {radius:9;color:host.dark ? "#888888":"#999999"}
        contentItem:Item {InputGlyph {anchors.centerIn:parent;width:9;height:9;symbol:"clear";color:"white"}}
    }
    T.Popup {
        id:suggestions;objectName:"bleeckerFileChooserSearchSuggestions";parent:host
        x:Math.min(0,host.width-width);y:host.suggestionOffset;width:260;padding:5
        implicitHeight:contentItem.implicitHeight+topPadding+bottomPadding
        visible:host.visible&&editor.activeFocus&&editor.draft.length>0&&!host.suggestionsDismissed
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
                        text:parent.modelData.prefix+editor.draft+"”";highlighted:host.suggestion===parent.index
                        Accessible.name:text;Accessible.role:Accessible.MenuItem
                        onClicked:host.commit(parent.modelData.mode)
                        background:Rectangle {radius:4;color:choice.highlighted ? "#0063e1":"transparent"}
                        contentItem:Text {leftPadding:8;rightPadding:8;text:choice.text;textFormat:Text.PlainText;elide:Text.ElideMiddle;font.pixelSize:13;color:choice.highlighted ? "white":host.dark ? "#eeeeee":"#222222";verticalAlignment:Text.AlignVCenter;Accessible.ignored:true}
                    }
                }
            }
        }
    }
}
