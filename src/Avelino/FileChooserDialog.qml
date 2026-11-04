import QtQuick
import QtQuick.Window
import QtQuick.Templates as T

FileChooserDialogBase {
    id:dialog
    required property FileChooserBrowser browser
    readonly property bool dark:BleeckerTheme.dark
    readonly property color ink:dark ? "#eeeeee":"#222222"
    readonly property color surface:dark ? "#303030":"#f5f5f5"
    readonly property color border:dark ? "#575757":"#c6c6c6"
    readonly property Item acceptInput:accept
    readonly property Item cancelInput:cancel
    readonly property Item pathInput:goTo.pathInput
    readonly property Item searchInput:searchControl.input
    readonly property QtObject goToDialog:goTo
    accessibilityDialog:goTo
    readonly property Item columnHost:columns
    readonly property QtObject newFolderDialog:newFolder
    property real columnWidth:220
    readonly property bool compactToolbar:width<640
    readonly property real browserTop:compactToolbar ? 109:77
    visible:browser.active
    modal:true;dim:false;focus:true;popupType:T.Popup.Window
    padding:0;margins:0;header:null;footer:null
    width:Math.min(880,parent ? parent.Screen.desktopAvailableWidth:880)
    height:Math.min(448,parent ? parent.Screen.desktopAvailableHeight:448)
    x:parent ? (parent.width-width)/2:0;y:20
    closePolicy:T.Popup.CloseOnEscape
    enter:null;exit:null
    title:"Open"
    background:Rectangle {color:dialog.surface;radius:10;border.width:0.5;border.color:dialog.border}
    function focusColumn(index:int):void {
        if(browser.search.active){searchResults.focusFiles();return}
        if(browser.viewMode!=="columns"){views.focusFiles();return}
        const column=columnItems.itemAt(index)
        if(column)column.view.forceActiveFocus()
        const left=index*columnWidth,right=(index+2)*columnWidth
        if(left<columns.contentX)columns.contentX=left
        else if(right>columns.contentX+columns.width)columns.contentX=Math.min(Math.max(0,columns.contentWidth-columns.width),right-columns.width)
    }
    function restoreChooserFocus():void {
        if(!visible||!browser.active)return
        const window=contentItem.Window.window
        if(window)window.requestActivate()
        focusColumn(browser.focusedColumn)
    }
    function focusRequestedColumn(index:int):void {
        // Empty queries restore browsing without interrupting the active
        // editor's next keystroke or its native Qt undo/redo sequence.
        if(!searchControl.input.activeFocus)focusColumn(index)
    }
    onOpened:{focusColumn(browser.focusedColumn);Qt.callLater(errorMessage.announceError)}
    onClosed:if(browser.active)browser.cancel()
    Connections {
        target:dialog.browser
        function onFocusRequested(index:int){Qt.callLater(dialog.focusRequestedColumn,index)}
    }
    contentItem:Item {
        Shortcut {
            sequence:"Ctrl+Shift+G";context:Qt.WindowShortcut
            enabled:dialog.visible&&!goTo.visible&&!newFolder.visible
            onActivated:goTo.open()
        }
        Keys.onPressed:event=>{
            if(event.key===Qt.Key_Escape){dialog.browser.cancel();event.accepted=true}
            else if(event.key===Qt.Key_L&&(event.modifiers&Qt.ControlModifier)){
                goTo.open();event.accepted=true
            }
        }
        Shortcut {
            sequence:"Ctrl+Shift+N";context:Qt.WindowShortcut
            enabled:dialog.visible&&dialog.browser.canCreateFolder&&!newFolder.visible&&!goTo.visible
            onActivated:newFolder.open()
        }
        Text {
            x:20;y:12;text:"Open";color:dialog.ink;font.family:Qt.application.font.family;font.pixelSize:13;font.weight:Font.DemiBold
            Accessible.role:Accessible.Heading;Accessible.name:text
        }
        FileChooserButton {
            objectName:"bleeckerFileChooserBack";x:20;y:38;width:24;implicitWidth:24;text:"‹"
            Accessible.name:"Back";enabled:dialog.browser.canGoBack;onClicked:dialog.browser.goBack()
        }
        FileChooserButton {
            objectName:"bleeckerFileChooserForward";x:44;y:38;width:24;implicitWidth:24;text:"›"
            Accessible.name:"Forward";enabled:dialog.browser.canGoForward;onClicked:dialog.browser.goForward()
        }
        FileChooserButton {
            id:up;objectName:"bleeckerFileChooserUp";x:76;y:38;width:32;implicitWidth:32;text:"↑"
            Accessible.name:"Enclosing folder";onClicked:dialog.browser.goUp()
        }
        FileChooserButton {
            id:viewChoice;objectName:"bleeckerFileChooserViewOptions";x:116;y:38;width:94
            text:dialog.browser.viewMode==="icons" ? "Icons ▾":dialog.browser.viewMode==="list" ? "List ▾":"Columns ▾"
            Accessible.role:Accessible.ButtonMenu;Accessible.name:"View Options"
            Accessible.onPressAction:viewChoice.click()
            onClicked:viewMenu.open()
            T.Menu {
                id:viewMenu;objectName:"bleeckerFileChooserViewMenu";parent:viewChoice;y:26;width:142;padding:5
                implicitHeight:contentItem.implicitHeight+topPadding+bottomPadding
                popupType:T.Popup.Item;enter:null;exit:null
                background:Rectangle {radius:7;color:dialog.dark ? "#303030":"white";border.width:0.5;border.color:dialog.border}
                contentItem:ListView {implicitHeight:contentHeight;model:viewMenu.contentModel;interactive:false;clip:true}
                component ViewOption:T.MenuItem {
                        id:option
                        required property string mode
                        objectName:"bleeckerFileChooserView_"+mode
                        width:132;height:26;implicitHeight:26;padding:0
                        text:mode==="icons" ? "Icons":mode==="list" ? "List":"Columns"
                        Accessible.role:Accessible.MenuItem;Accessible.name:text
                        Accessible.checkable:true;Accessible.checked:checked
                        Accessible.onPressAction:option.click()
                        checkable:true;autoExclusive:true;checked:dialog.browser.viewMode===mode
                        onTriggered:dialog.browser.viewMode=mode
                        background:Rectangle {radius:4;color:option.highlighted ? "#0063e1":"transparent"}
                        contentItem:Text {
                            leftPadding:8;text:(option.checked ? "✓  ":"    ")+option.text
                            textFormat:Text.PlainText;verticalAlignment:Text.AlignVCenter
                            color:option.highlighted ? "white":dialog.ink;font.family:Qt.application.font.family;font.pixelSize:13
                            Accessible.ignored:true
                        }
                        indicator:null
                }
                ViewOption {mode:"icons"}
                ViewOption {mode:"list"}
                ViewOption {mode:"columns"}
            }
        }
        FileChooserLocationMenu {
            id:location;browser:dialog.browser;x:218;y:38
            width:Math.min(190,Math.max(76,(parent.width-238)*(dialog.compactToolbar ? 1:0.42)));implicitWidth:190
        }
        FileChooserSearchInput {
            id:searchControl;browser:dialog.browser;resultsView:searchResults.view
            x:dialog.compactToolbar ? 20:parent.width-218;y:dialog.compactToolbar ? 70:38
            width:dialog.compactToolbar ? parent.width-40:198;height:24
            suggestionOffset:dialog.compactToolbar ? dialog.browserTop+38-y:28
        }
        Rectangle {x:0;y:dialog.browserTop-1;width:parent.width;height:1;color:dialog.border;Accessible.ignored:true}
        Flickable {
            id:columns;objectName:"bleeckerFileChooserColumns"
            visible:!dialog.browser.search.active&&dialog.browser.viewMode==="columns"
            x:0;y:dialog.browserTop;width:parent.width;height:Math.max(0,parent.height-dialog.browserTop-62)
            contentWidth:Math.max(width,(dialog.browser.count+1)*dialog.columnWidth);contentHeight:height
            clip:true;boundsBehavior:Flickable.StopAtBounds
            Row {
                Repeater {
                    id:columnItems;model:dialog.browser
                    delegate:Item {
                        id:column
                        required property int index
                        required property FileChooserModel directoryModel
                        required property url navigationUrl
                        readonly property Item view:files
                        width:dialog.columnWidth;height:columns.height
                        Rectangle {anchors.fill:parent;color:dialog.dark ? "#252525":"white";Accessible.ignored:true}
                        Rectangle {x:parent.width-1;width:1;height:parent.height;color:dialog.border;Accessible.ignored:true}
                        ListView {
                            id:files;objectName:"bleeckerFileChooserColumn"+column.index
                            anchors.fill:parent;anchors.rightMargin:1;clip:true
                            model:column.directoryModel;currentIndex:column.directoryModel.currentIndex
                            highlightMoveDuration:0;highlightResizeDuration:0
                            boundsBehavior:Flickable.StopAtBounds
                            Accessible.role:Accessible.List;Accessible.name:"Files in "+column.directoryModel.folderPath
                            Accessible.focusable:true
                            Keys.onDownPressed:dialog.browser.moveFromInput(1)
                            Keys.onUpPressed:dialog.browser.moveFromInput(-1)
                            Keys.onLeftPressed:dialog.browser.focusLeft()
                            Keys.onRightPressed:dialog.browser.focusRight()
                            Keys.onReturnPressed:dialog.browser.acceptSelection()
                            Keys.onEnterPressed:dialog.browser.acceptSelection()
                            Keys.onPressed:event=>{
                                if(event.key===Qt.Key_A&&(event.modifiers&Qt.ControlModifier)){dialog.browser.selectAll();event.accepted=true}
                                else if(event.key===Qt.Key_L&&(event.modifiers&Qt.ControlModifier)){goTo.open();event.accepted=true}
                            }
                            delegate:T.ItemDelegate {
                                id:entry
                                required property int index
                                required property string fileName
                                required property url fileUrl
                                required property bool fileDirectory
                                required property bool fileEligible
                                required property bool fileSelected
                                readonly property bool navigation:fileDirectory&&fileUrl.toString()===column.navigationUrl.toString()
                                objectName:"bleeckerFileChooserRow"+column.index+"_"+index
                                width:files.width;height:22;padding:0;focusPolicy:Qt.NoFocus
                                highlighted:fileSelected||navigation
                                Accessible.role:Accessible.ListItem;Accessible.name:fileName;Accessible.selected:fileSelected||navigation
                                Accessible.focusable:fileDirectory||fileEligible;Accessible.selectable:fileDirectory||fileEligible
                                Accessible.description:fileDirectory ? "Folder":fileEligible ? "Document":"Unavailable for selected file types"
                                Accessible.onPressAction:dialog.browser.chooseFromInput(column.index,index)
                                onClicked:dialog.browser.chooseFromInput(column.index,index)
                                onDoubleClicked:dialog.browser.activate(column.index,index)
                                background:Rectangle {color:entry.highlighted ? dialog.browser.focusedColumn===column.index ? "#0063e1":dialog.dark ? "#555555":"#dddddd":"transparent"}
                                contentItem:Item {
                                    FileChooserGlyph {x:8;y:3;width:16;height:16;directory:entry.fileDirectory;opacity:entry.fileDirectory||entry.fileEligible ? 1:0.4}
                                    Text {
                                        x:29;y:0;width:Math.max(0,parent.width-47);height:parent.height
                                        text:entry.fileName;textFormat:Text.PlainText;elide:Text.ElideRight;verticalAlignment:Text.AlignVCenter
                                        font.family:Qt.application.font.family;font.pixelSize:13
                                        color:entry.highlighted&&dialog.browser.focusedColumn===column.index ? "white":dialog.ink
                                        opacity:entry.fileDirectory||entry.fileEligible ? 1:0.35;Accessible.ignored:true
                                    }
                                    Text {anchors.right:parent.right;anchors.rightMargin:8;height:parent.height;verticalAlignment:Text.AlignVCenter;text:entry.fileDirectory ? "›":"";color:dialog.ink;font.pixelSize:15;Accessible.ignored:true}
                                }
                            }
                            T.ScrollBar.vertical:T.ScrollBar {
                                width:7;policy:T.ScrollBar.AsNeeded;visible:policy===T.ScrollBar.AlwaysOn||(policy===T.ScrollBar.AsNeeded&&size<1)
                                contentItem:Rectangle {radius:3;color:dialog.dark ? "#999999":"#999999";implicitWidth:5;implicitHeight:24}
                                background:null
                            }
                        }
                    }
                }
            }
            T.ScrollBar.horizontal:T.ScrollBar {
                height:7;policy:T.ScrollBar.AsNeeded;visible:policy===T.ScrollBar.AlwaysOn||(policy===T.ScrollBar.AsNeeded&&size<1)
                contentItem:Rectangle {radius:3;color:"#999999";implicitWidth:24;implicitHeight:5}
                background:null
            }
        }
        FileChooserViews {
            id:views;browser:dialog.browser;visible:!dialog.browser.search.active&&dialog.browser.viewMode!=="columns"
            x:0;y:dialog.browserTop;width:parent.width;height:Math.max(0,parent.height-dialog.browserTop-62)
        }
        FileChooserSearchResults {
            id:searchResults;browser:dialog.browser;visible:dialog.browser.search.active
            x:0;y:dialog.browserTop;width:parent.width;height:Math.max(0,parent.height-dialog.browserTop-62)
        }
        Rectangle {x:0;y:parent.height-62;width:parent.width;height:1;color:dialog.border;Accessible.ignored:true}
        Text {
            id:errorMessage;objectName:"bleeckerFileChooserError"
            x:128;y:parent.height-51;width:Math.max(0,parent.width-323);height:42
            readonly property string message:dialog.browser.error.length ? dialog.browser.error:dialog.browser.places.error
            text:message.startsWith("Indexed search is unavailable:") ? "Indexed search is unavailable. Clear the search to browse folders.":message
            textFormat:Text.PlainText;wrapMode:Text.Wrap;color:dialog.ink
            font.family:Qt.application.font.family;font.pixelSize:12
            Accessible.role:Accessible.StaticText;Accessible.name:text
            function announceError():void {
                if(dialog.visible&&text.length)Accessible.announce(text,Accessible.Assertive)
            }
            onTextChanged:()=>{if(dialog.visible&&errorMessage.text.length)Qt.callLater(errorMessage.announceError)}
        }
        FileChooserButton {
            objectName:"bleeckerFileChooserNewFolder";x:20;y:parent.height-42;width:94;text:"New Folder"
            enabled:dialog.browser.canCreateFolder;onClicked:newFolder.open()
        }
        FileChooserButton {
            id:cancel;objectName:"bleeckerFileChooserCancel";x:parent.width-180;y:parent.height-42;width:72;text:"Cancel"
            onClicked:dialog.browser.cancel()
        }
        FileChooserButton {
            id:accept;objectName:"bleeckerFileChooserOpen";x:parent.width-98;y:parent.height-42;width:78;text:"Open"
            accent:true;enabled:dialog.browser.canAccept;onClicked:dialog.browser.acceptSelection()
        }
    }
    FileChooserGoTo {
        id:goTo;browser:dialog.browser;parent:dialog.contentItem
        onClosed:Qt.callLater(dialog.restoreChooserFocus)
    }
    FileChooserNewFolder {
        id:newFolder;browser:dialog.browser;parent:dialog.contentItem
        onClosed:if(dialog.visible&&dialog.browser.active)Qt.callLater(dialog.focusColumn,dialog.browser.focusedColumn)
    }
}
