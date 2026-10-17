import QtQuick
import QtQuick.Templates as T
import Avelino

T.Control {
    id:row
    required property var rowData
    required property int rowIndex
    required property bool rowActive
    required property var observer
    property int counter:0
    property bool completed:false
    readonly property string kind:rowData.kind
    readonly property bool rectangle:["fixed","fill","overflow"].includes(kind)
    readonly property Item content:loader.item
    padding:0;background:null;focusPolicy:Qt.NoFocus
    font:rowFont
    implicitWidth:rectangle ? kind==="fill" ? 0:rowData.width:loader.item ? loader.item.implicitWidth:0
    implicitHeight:rectangle||kind==="tall" ? rowData.height:loader.item ? loader.item.implicitHeight:0
    BleeckerLayout.minimumWidth:rectangle&&kind!=="fill" ? rowData.width:0
    BleeckerLayout.idealWidth:implicitWidth
    BleeckerLayout.fillsWidth:kind==="fill"
    onCounterChanged:if(completed)observer.counted(rowData.key,counter)
    onRowActiveChanged:if(completed)observer.activity(rowData.key,rowActive)
    Component.onCompleted:{completed=true;observer.created(rowData.key);observer.counted(rowData.key,counter);if(rowActive)observer.activity(rowData.key,true)}
    function propose(){if(loader.item&&typeof loader.item.propose==="function")loader.item.propose(row.BleeckerLayout.proposedWidth)}
    Connections {target:row.BleeckerLayout;function onProposalChanged(){row.propose()}}
    Loader {
        onLoaded:row.propose()
        id:loader
        width:row.width;height:row.height
        sourceComponent:row.rectangle ? box:row.kind==="button" ? action:row.kind==="detail" ? detail:label
    }
    Component {id:box;Rectangle {color:BleeckerTheme.palette.sea}}
    Component {
        id:label
        BleeckerText {
            text:row.rowData.title;font:rowFont;color:rowForeground
            function propose(value){BleeckerLayout.propose(value)}
            y:(row.height-implicitHeight)/2
        }
    }
    Component {
        id:action
        T.Button {
            id:button;objectName:"spotlightRowAction-"+row.rowData.key
            implicitWidth:title.implicitWidth;implicitHeight:title.implicitHeight
            padding:0;background:null;enabled:!row.rowData.disabled
            font:rowFont
            contentItem:BleeckerText {id:title;text:row.rowData.title+" ("+row.counter+")";font:rowFont;color:rowForeground}
            function propose(value){title.BleeckerLayout.propose(value)}
            onClicked:row.counter++
            Accessible.name:title.text
        }
    }
    Component {
        id:detail
        Item {
            function propose(value){title.BleeckerLayout.propose(value);subtitle.BleeckerLayout.propose(value)}
            implicitWidth:Math.max(title.implicitWidth,subtitle.implicitWidth)
            implicitHeight:title.implicitHeight+3+subtitle.implicitHeight
            BleeckerText {id:title;text:row.rowData.title;font.family:BleeckerTheme.primaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(14);font.weight:Font.DemiBold;color:rowForeground}
            BleeckerText {id:subtitle;y:title.height+3;text:row.rowData.detail;font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(12);color:BleeckerTheme.palette.textSecondary}
        }
    }
}
