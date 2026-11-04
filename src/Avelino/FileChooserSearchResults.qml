import QtQuick
import QtQuick.Templates as T

FocusScope {
    id:host
    required property FileChooserBrowser browser
    readonly property Item view:rows
    readonly property bool dark:BleeckerTheme.dark
    readonly property bool icons:browser.viewMode==="icons"
    readonly property color ink:dark ? "#eeeeee":"#222222"
    clip:true
    function focusFiles():void {rows.forceActiveFocus()}
    Rectangle {anchors.fill:parent;color:host.dark ? "#252525":"white";Accessible.ignored:true}
    Row {
        x:10;y:7;spacing:8;height:24
        Text {height:24;text:"Search:";color:host.ink;font.pixelSize:13;font.weight:Font.DemiBold;verticalAlignment:Text.AlignVCenter}
        FileChooserButton {
            objectName:"bleeckerFileChooserSearchComputer";text:"This Computer";width:118;height:24;implicitHeight:24
            Accessible.role:Accessible.RadioButton;Accessible.name:text;Accessible.checkable:true;Accessible.checked:!host.browser.search.folderOnly
            fillColor:!host.browser.search.folderOnly ? host.dark ? "#555555":"#dddddd":"transparent"
            onClicked:host.browser.search.folderOnly=false
        }
        FileChooserButton {
            objectName:"bleeckerFileChooserSearchFolder";text:"“"+host.browser.folderLabel+"”";width:Math.min(220,Math.max(90,implicitContentWidth+18));height:24;implicitHeight:24
            Accessible.role:Accessible.RadioButton;Accessible.name:text;Accessible.checkable:true;Accessible.checked:host.browser.search.folderOnly
            fillColor:host.browser.search.folderOnly ? host.dark ? "#555555":"#dddddd":"transparent"
            onClicked:host.browser.search.folderOnly=true
        }
    }
    FileChooserGrid {
        id:rows;objectName:"bleeckerFileChooserSearchResults";x:0;y:38;width:parent.width;height:Math.max(0,parent.height-38)
        directoryModel:host.browser.search;model:host.browser.search;currentIndex:host.browser.search.currentIndex
        cellWidth:host.icons ? 112:width;cellHeight:host.icons ? 90:38
        keyNavigationEnabled:false;activeFocusOnTab:true;clip:true
        highlightMoveDuration:0;boundsBehavior:Flickable.StopAtBounds
        Accessible.role:Accessible.List;Accessible.name:"Search results";Accessible.focusable:true
        Keys.onDownPressed:event=>host.browser.search.move(host.icons ? Math.max(1,Math.floor(width/cellWidth)):1,event.modifiers)
        Keys.onUpPressed:event=>host.browser.search.move(host.icons ? -Math.max(1,Math.floor(width/cellWidth)):-1,event.modifiers)
        Keys.onReturnPressed:host.browser.acceptSelection()
        Keys.onEnterPressed:host.browser.acceptSelection()
        Keys.onPressed:event=>{if(event.key===Qt.Key_A&&(event.modifiers&Qt.ControlModifier)){host.browser.search.selectAll();event.accepted=true}}
        Keys.onLeftPressed:event=>{if(host.icons)host.browser.search.move(-1,event.modifiers)}
        Keys.onRightPressed:event=>{if(host.icons)host.browser.search.move(1,event.modifiers)}
        onCurrentIndexChanged:if(currentIndex>=0)positionViewAtIndex(currentIndex,GridView.Contain)
        delegate:FileChooserRow {
            id:row
            required property int index
            required property string fileName
            required property url fileUrl
            required property bool fileDirectory
            required property bool fileEligible
            required property bool fileSelected
            required property string fileKind
            required property string filePath
            view:rows;listingIndex:index;folder:fileDirectory
            objectName:"bleeckerFileChooserSearchRow_"+index
            width:rows.cellWidth;height:rows.cellHeight;padding:0;focusPolicy:Qt.NoFocus
            Accessible.role:Accessible.ListItem;Accessible.name:fileName;Accessible.selected:fileSelected
            Accessible.selectable:fileDirectory||fileEligible;Accessible.focusable:fileDirectory||fileEligible
            Accessible.focused:rows.activeFocus&&rows.currentIndex===index
            Accessible.description:!fileEligible&&!fileDirectory ? "Unavailable for selected file types":fileKind+", "+filePath
            Accessible.onPressAction:{rows.forceActiveFocus();host.browser.search.selectFromInput(index)}
            onClicked:{rows.forceActiveFocus();host.browser.search.selectFromInput(index)}
            onDoubleClicked:host.browser.search.activate(index)
            background:Rectangle {x:10;width:parent.width-20;radius:5;color:row.fileSelected ? "#0063e1":"transparent"}
            contentItem:Item {
                FileChooserGlyph {x:host.icons ? 40:18;y:host.icons ? 9:10;width:host.icons ? 32:16;height:width;directory:row.fileDirectory;opacity:row.fileDirectory||row.fileEligible ? 1:0.35}
                Text {x:host.icons ? 8:44;y:host.icons ? 46:2;width:parent.width-x-(host.icons ? 8:14);height:host.icons ? 36:18;text:row.fileName;textFormat:Text.PlainText;elide:Text.ElideRight;wrapMode:host.icons ? Text.Wrap:Text.NoWrap;horizontalAlignment:host.icons ? Text.AlignHCenter:Text.AlignLeft;font.family:Qt.application.font.family;font.pixelSize:13;color:row.fileSelected ? "white":host.ink;opacity:row.fileDirectory||row.fileEligible ? 1:0.35;Accessible.ignored:true}
                Text {x:44;y:20;width:parent.width-58;height:16;visible:!host.icons;text:row.filePath;textFormat:Text.PlainText;elide:Text.ElideMiddle;font.family:Qt.application.font.family;font.pixelSize:11;color:row.fileSelected ? "white":host.dark ? "#aaaaaa":"#777777";Accessible.ignored:true}
            }
        }
        T.ScrollBar.vertical:T.ScrollBar {
            width:7;policy:T.ScrollBar.AsNeeded;visible:policy===T.ScrollBar.AsNeeded&&size<1
            contentItem:Rectangle {radius:3;color:"#999999";implicitWidth:5;implicitHeight:24}
            background:null
        }
    }
    Text {
        anchors.centerIn:rows;visible:host.browser.search.count===0&&!host.browser.search.error.length
        text:host.browser.search.busy ? "Searching…":"No results";color:host.ink;font.pixelSize:13
        Accessible.role:Accessible.StaticText;Accessible.name:text
    }
}
