import QtQuick
import QtQuick.Templates as T

InheritedControl {
    id:control
    required property string query
    property alias items:rows.items
    property alias itemIdentity:rows.itemIdentity
    required property Component row
    signal queryRequested(string requestedQuery)
    property color foreground:resolvedTextColor
    readonly property Item presentationItem:body
    readonly property Item searchField:search
    readonly property Item rowContainer:rows
    readonly property Item viewport:scroll
    readonly property int count:rows.count
    function rowAt(index:int):Item{return rows.itemAt(index)}
    function rowCellAt(index:int):Item{return rows.cellAt(index)}
    function scrollTo(y:real):void{scroll.contentY=Math.max(0,Math.min(y,Math.max(0,rows.contentHeight-scroll.height)))}
    implicitWidth:520;implicitHeight:380
    padding:0;background:null;focusPolicy:Qt.NoFocus
    defaultTextColor:BleeckerTheme.nativeTextPrimary
    BleeckerLayout.minimumWidth:520;BleeckerLayout.idealWidth:520
    Accessible.ignored:true
    BleeckerSurface {
        id:body;objectName:"bleeckerCommandSpotlightPresentation"
        width:520;height:380;radius:BleeckerTokens.radii.dialog
        x:(control.width-width)/2;y:(control.height-height)/2
        BleeckerSearchField {
            id:search;objectName:"bleeckerCommandSpotlightSearch"
            x:12;y:12;width:496;height:implicitHeight
            placeholderText:"Search commands"
            text:control.query
            color:control.foreground
            trailing:length>0 ? clearAction:null
            onTextEdited:control.queryRequested(text)
            onActiveFocusChanged:if(!activeFocus)text=control.query
            Connections {
                target:control
                function onQueryChanged(){if(!search.activeFocus)search.text=control.query}
            }
        }
        Component {
            id:clearAction
            T.Button {
                objectName:"bleeckerSearchClear"
                implicitWidth:18.5;implicitHeight:18.5;padding:4
                focusPolicy:Qt.NoFocus
                enabled:!search.readOnly;opacity:enabled ? 1:0.5
                Accessible.role:Accessible.Button;Accessible.name:"Clear search"
                contentItem:InputGlyph {symbol:"clear"}
                background:Rectangle {radius:4;color:search.p.muted}
                onClicked:{search.clear();search.textEdited();search.text=control.query}
            }
        }
        BleeckerSeparator {objectName:"bleeckerCommandSpotlightSeparator";y:search.height+24;width:520;height:1}
        Flickable {
            id:scroll;objectName:"bleeckerCommandSpotlightViewport"
            x:0;y:search.height+25;width:520;height:355-search.height
            contentWidth:520;contentHeight:rows.contentHeight
            flickableDirection:Flickable.VerticalFlick;boundsBehavior:Flickable.StopAtBounds
            clip:true
            SpotlightRows {
                id:rows;objectName:"bleeckerCommandSpotlightRows"
                items:[];row:control.row
                width:520;height:implicitHeight;mirrored:control.mirrored
                rowFont:control.presentationFont;rowForeground:control.foreground
            }
        }
    }
}
