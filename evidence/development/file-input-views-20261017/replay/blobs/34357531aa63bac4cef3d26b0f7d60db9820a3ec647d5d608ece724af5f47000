import QtQuick
import QtQuick.Templates as T

FocusScope {
    id:host
    required property FileChooserBrowser browser
    readonly property bool icons:browser.viewMode==="icons"
    readonly property bool dark:BleeckerTheme.dark
    readonly property color ink:dark ? "#eeeeee":"#222222"
    clip:true
    property real nameWidth:Math.max(180,width*0.43)
    property real sizeWidth:96
    property real kindWidth:116
    readonly property real columnsWidth:Math.max(width,nameWidth+sizeWidth+kindWidth+110)
    readonly property Item view:loader.item
    function focusFiles():void {if(view)view.forceActiveFocus()}
    function select(index:int):void {browser.listing.selectFromInput(index);focusFiles()}
    function toggleExpanded(index:int):void {focusFiles();browser.listing.toggleExpanded(index)}
    Rectangle {anchors.fill:parent;color:host.dark ? "#252525":"white";Accessible.ignored:true}
    Keys.onPressed:event=>{
        const model=host.browser.listing
        if(event.key===Qt.Key_A&&(event.modifiers&Qt.ControlModifier)){model.selectAll();event.accepted=true}
        else if(event.key===Qt.Key_Return||event.key===Qt.Key_Enter){host.browser.acceptSelection();event.accepted=true}
        else if(event.key===Qt.Key_Down){model.move(host.icons ? Math.max(1,Math.floor(host.width/112)):1,event.modifiers);event.accepted=true}
        else if(event.key===Qt.Key_Up){model.move(host.icons ? -Math.max(1,Math.floor(host.width/112)):-1,event.modifiers);event.accepted=true}
        else if(event.key===Qt.Key_Right){if(host.icons)model.move(1,event.modifiers);else model.right();event.accepted=true}
        else if(event.key===Qt.Key_Left){if(host.icons)model.move(-1,event.modifiers);else model.left();event.accepted=true}
    }
    Loader {
        id:loader;anchors.fill:parent;sourceComponent:host.icons ? gridComponent:listComponent
        onLoaded:if(host.activeFocus)host.focusFiles()
    }
    Component {
        id:listComponent
        FocusScope {
            Row {
                id:head;x:-rows.contentX;height:29;width:host.columnsWidth
                Repeater {
                    model:[{key:"name",label:"Name",size:host.nameWidth},{key:"size",label:"Size",size:host.sizeWidth},
                        {key:"kind",label:"Kind",size:host.kindWidth},{key:"added",label:"Date Added",size:Math.max(110,host.width-host.nameWidth-host.sizeWidth-host.kindWidth)}]
                    delegate:T.Button {
                        id:heading
                        required property var modelData
                        objectName:"bleeckerFileChooserSort_"+modelData.key
                        width:modelData.size;height:29;padding:0
                        enabled:modelData.key!=="added"
                        Accessible.name:modelData.label
                        Accessible.description:modelData.key==="added" ? "Date Added is unavailable":host.browser.listing.sortKey===modelData.key ? host.browser.listing.ascending ? "Ascending":"Descending":"Sort by "+modelData.label
                        onClicked:{host.browser.listing.sortBy(modelData.key);host.focusFiles()}
                        background:Rectangle {color:host.dark ? "#303030":"white";border.width:heading.visualFocus ? 2:0;border.color:"#80baff"}
                        contentItem:Item {
                            Text {x:14;width:parent.width-30;height:parent.height;verticalAlignment:Text.AlignVCenter;text:heading.modelData.label;color:host.ink;font.pixelSize:12;font.family:Qt.application.font.family;Accessible.ignored:true}
                            Text {anchors.right:parent.right;anchors.rightMargin:8;height:parent.height;verticalAlignment:Text.AlignVCenter;text:host.browser.listing.sortKey===heading.modelData.key ? host.browser.listing.ascending ? "⌃":"⌄":"";color:host.ink;Accessible.ignored:true}
                        }
                        Rectangle {x:parent.width-1;y:7;width:1;height:15;color:host.dark ? "#575757":"#dddddd";Accessible.ignored:true}
                    }
                }
            }
            Rectangle {y:28;width:parent.width;height:1;color:host.dark ? "#575757":"#dddddd";Accessible.ignored:true}
            Item {
                y:29;width:parent.width;height:Math.max(0,parent.height-29);clip:true;Accessible.ignored:true
                Repeater {
                    model:Math.ceil(parent.height/20)+2
                    delegate:Rectangle {
                        required property int index
                        x:10;y:index*20-(rows.contentY%40);width:parent.width-20;height:20;radius:6
                        color:index%2 ? host.dark ? "#303030":"#f5f5f5":"transparent";Accessible.ignored:true
                    }
                }
            }
            FileChooserTree {
                id:rows;objectName:"bleeckerFileChooserList";y:29;width:parent.width;height:Math.max(0,parent.height-29)
                directoryModel:host.browser.listing
                columnWidths:[host.nameWidth,host.sizeWidth,host.kindWidth,Math.max(110,host.width-host.nameWidth-host.sizeWidth-host.kindWidth)]
                focus:true
                clip:true;model:host.browser.listing;currentIndex:host.browser.listing.currentIndex
                keyNavigationEnabled:false
                contentWidth:host.columnsWidth;flickableDirection:Flickable.AutoFlickIfNeeded
                boundsBehavior:Flickable.StopAtBounds;highlightMoveDuration:0;highlightResizeDuration:0
                Accessible.role:Accessible.Tree;Accessible.name:"Files in "+host.browser.folderPath
                Accessible.focusable:true
                onCurrentIndexChanged:if(currentIndex>=0)positionViewAtIndex(currentIndex,ListView.Contain)
                delegate:FileChooserRow {
                    id:row
                    required property int index
                    required property string fileName
                    required property url fileUrl
                    required property bool fileDirectory
                    required property bool fileEligible
                    required property bool fileSelected
                    required property int fileDepth
                    required property bool fileExpanded
                    required property string fileSize
                    required property string fileKind
                    required property string fileError
                    objectName:"bleeckerFileChooserListRow_"+index
                    width:rows.contentWidth;height:fileError.length ? 40:20;padding:0;focusPolicy:Qt.NoFocus
                    enabled:fileDirectory||fileEligible
                    hierarchical:true;folder:fileDirectory;expanded:fileExpanded;view:rows;listingIndex:index
                    Accessible.name:fileName;Accessible.selected:fileSelected;Accessible.selectable:fileDirectory||fileEligible
                    Accessible.focusable:fileDirectory||fileEligible
                    Accessible.focused:rows.activeFocus&&rows.currentIndex===index
                    Accessible.description:fileError
                    Accessible.onPressAction:host.select(index)
                    onClicked:host.select(index)
                    onDoubleClicked:host.browser.listing.activate(index)
                    onDisclosureRequested:host.toggleExpanded(index)
                    background:Rectangle {x:10;width:parent.width-20;radius:6;color:row.fileSelected ? "#0063e1":"transparent"}
                    contentItem:Item {
                        FileChooserButton {
                            objectName:"bleeckerFileChooserDisclosure_"+row.index
                            x:10+row.fileDepth*16;y:0;width:18;height:20;implicitWidth:18
                            visible:row.fileDirectory;text:row.fileExpanded ? "⌄":"›"
                            fillColor:"transparent";borderColor:"transparent"
                            Accessible.name:(row.fileExpanded ? "Collapse ":"Expand ")+row.fileName
                            Accessible.ignored:true
                            onClicked:host.toggleExpanded(row.index)
                        }
                        FileChooserGlyph {x:30+row.fileDepth*16;y:2;directory:row.fileDirectory;opacity:row.fileEligible||row.fileDirectory ? 1:0.35}
                        Text {
                            x:51+row.fileDepth*16;width:Math.max(0,host.nameWidth-x-6);height:20
                            text:row.fileName;textFormat:Text.PlainText;elide:Text.ElideRight;verticalAlignment:Text.AlignVCenter
                            font.family:Qt.application.font.family;font.pixelSize:13
                            color:row.fileSelected ? "white":host.ink;opacity:row.fileDirectory||row.fileEligible ? 1:0.35;Accessible.ignored:true
                        }
                        Repeater {
                            model:[{x:host.nameWidth,w:host.sizeWidth,text:row.fileSize},{x:host.nameWidth+host.sizeWidth,w:host.kindWidth,text:row.fileKind},
                                {x:host.nameWidth+host.sizeWidth+host.kindWidth,w:Math.max(110,host.width-host.nameWidth-host.sizeWidth-host.kindWidth),text:"--"}]
                            delegate:Text {
                                required property var modelData
                                x:modelData.x+10;width:modelData.w-18;height:20;text:modelData.text
                                textFormat:Text.PlainText;elide:Text.ElideRight;verticalAlignment:Text.AlignVCenter
                                font.family:Qt.application.font.family;font.pixelSize:12;color:row.fileSelected ? "white":host.ink
                                opacity:row.fileDirectory||row.fileEligible ? 0.7:0.35;Accessible.ignored:true
                            }
                        }
                        Text {x:51+row.fileDepth*16;y:20;width:parent.width-x-12;height:20;text:row.fileError;textFormat:Text.PlainText;elide:Text.ElideRight;visible:text.length>0;color:host.ink;font.pixelSize:11;Accessible.name:text}
                    }
                }
                T.ScrollBar.vertical:T.ScrollBar {
                    width:7;policy:T.ScrollBar.AsNeeded
                    contentItem:Rectangle {radius:3;color:"#999999";implicitWidth:5;implicitHeight:24}
                    background:null
                }
                T.ScrollBar.horizontal:T.ScrollBar {
                    height:7;policy:T.ScrollBar.AsNeeded
                    contentItem:Rectangle {radius:3;color:"#999999";implicitWidth:24;implicitHeight:5}
                    background:null
                }
            }
        }
    }
    Component {
        id:gridComponent
        FileChooserGrid {
            id:grid;objectName:"bleeckerFileChooserIcons"
            directoryModel:host.browser.listing
            clip:true;model:host.browser.listing;currentIndex:host.browser.listing.currentIndex
            keyNavigationEnabled:false
            cellWidth:112;cellHeight:116;boundsBehavior:Flickable.StopAtBounds;highlightMoveDuration:0
            Accessible.role:Accessible.List;Accessible.name:"Files in "+host.browser.folderPath
            Accessible.focusable:true
            onCurrentIndexChanged:if(currentIndex>=0)positionViewAtIndex(currentIndex,GridView.Contain)
            delegate:FileChooserRow {
                id:tile
                required property int index
                required property string fileName
                required property bool fileDirectory
                required property bool fileEligible
                required property bool fileSelected
                required property string fileKind
                objectName:"bleeckerFileChooserIcon_"+index
                width:grid.cellWidth;height:grid.cellHeight;padding:0;focusPolicy:Qt.NoFocus
                enabled:fileDirectory||fileEligible
                hierarchical:false;folder:fileDirectory;view:grid;listingIndex:index
                Accessible.name:fileName;Accessible.selected:fileSelected;Accessible.selectable:fileDirectory||fileEligible
                Accessible.focusable:fileDirectory||fileEligible
                Accessible.focused:grid.activeFocus&&grid.currentIndex===index;Accessible.description:fileKind
                Accessible.onPressAction:host.select(index)
                onClicked:host.select(index)
                onDoubleClicked:host.browser.listing.activate(index)
                background:null
                contentItem:Item {
                    Rectangle {x:16;y:12;width:80;height:80;radius:8;color:host.dark ? "#444444":"#eeeeee";visible:tile.fileSelected;Accessible.ignored:true}
                    FileChooserGlyph {x:24;y:18;width:64;height:64;directory:tile.fileDirectory;opacity:tile.fileDirectory||tile.fileEligible ? 1:0.35}
                    Rectangle {x:label.x-4;y:label.y;width:label.width+8;height:label.height;radius:4;color:"#0063e1";visible:tile.fileSelected;Accessible.ignored:true}
                    Text {
                        id:label;x:8;y:94;width:96;height:18;text:tile.fileName;textFormat:Text.PlainText;elide:Text.ElideMiddle
                        horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter
                        font.family:Qt.application.font.family;font.pixelSize:13;color:tile.fileSelected ? "white":host.ink
                        opacity:tile.fileDirectory||tile.fileEligible ? 1:0.35;Accessible.ignored:true
                    }
                }
            }
            T.ScrollBar.vertical:T.ScrollBar {
                width:7;policy:T.ScrollBar.AsNeeded
                contentItem:Rectangle {radius:3;color:"#999999";implicitWidth:5;implicitHeight:24}
                background:null
            }
        }
    }
}
