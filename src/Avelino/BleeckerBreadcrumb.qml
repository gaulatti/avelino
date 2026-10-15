import QtQuick
import QtQuick.Templates as T

Item {
    id:control
    required property var items
    property real maximumWidth:-1
    signal selected(int index)
    readonly property Item presentationItem:row
    readonly property var entries:BleeckerValueTools.breadcrumbItems(items)
    implicitWidth:row.implicitWidth;implicitHeight:row.implicitHeight
    PixelAlignment {id:metrics;target:control}
    ProposalRow {
        id:row;objectName:"bleeckerBreadcrumbPresentation"
        x:(control.width-width)/2;y:(control.height-height)/2
        maximumWidth:BleeckerTextTools.proposedWidth(control.maximumWidth,0)
        spacing:8;mirrored:control.LayoutMirroring.enabled
        Repeater {
            model:Math.max(0,control.entries.length*2-1)
            T.Button {
                id:entry
                required property int index
                readonly property bool separator:index%2===1
                readonly property int logicalIndex:Math.floor(index/2)
                readonly property var record:control.entries[logicalIndex]
                readonly property bool hasIcon:!separator && record.icon!==undefined && record.icon!==null
                readonly property real iconGap:hasIcon ? 5:0
                readonly property color foregroundColor:logicalIndex===control.entries.length-1 ? BleeckerTheme.palette.textPrimary:BleeckerTheme.palette.sea
                objectName:separator ? "bleeckerBreadcrumbSeparator"+(logicalIndex+1):"bleeckerBreadcrumbItem"+logicalIndex
                text:separator ? "":record.title
                font.family:BleeckerTheme.primaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(12)
                focusPolicy:separator ? Qt.NoFocus:Qt.StrongFocus
                padding:0;background:null
                implicitWidth:separator ? (metrics.devicePixelRatio<2 ? 8:7.5):label.width+iconSlot.width+iconGap
                implicitHeight:separator ? 11:Math.max(label.height,iconSlot.height)
                BleeckerLayout.minimumWidth:separator ? implicitWidth:iconSlot.width+iconGap
                BleeckerLayout.idealWidth:separator ? implicitWidth:label.unwrappedWidth+iconSlot.width+iconGap
                Accessible.ignored:separator;Accessible.role:Accessible.Button;Accessible.name:text
                enabled:!separator
                onClicked:control.selected(logicalIndex)
                contentItem:Item {
                    opacity:entry.enabled || entry.separator ? 1:0.5
                    NavigationGlyph {
                        visible:entry.separator;direction:"right";pixelSize:11
                        width:entry.width;height:11;color:BleeckerTheme.palette.textSecondary
                    }
                    Loader {
                        id:iconSlot
                        sourceComponent:entry.hasIcon ? entry.record.icon:null
                        readonly property color foregroundColor:entry.foregroundColor
                        readonly property font font:entry.font
                        x:control.LayoutMirroring.enabled ? parent.width-width:0
                        y:(parent.height-height)/2
                        Accessible.ignored:true
                    }
                    OwnedText {
                        id:label;objectName:"bleeckerBreadcrumbLabel"+entry.logicalIndex
                        visible:!entry.separator;text:entry.text;font:entry.font;color:entry.foregroundColor
                        wrapWidth:entry.BleeckerLayout.proposedWidth<0 ? -1:Math.max(0,entry.BleeckerLayout.proposedWidth-iconSlot.width-entry.iconGap)
                        width:wrapWidth<0 ? implicitWidth:Math.min(implicitWidth,wrapWidth)
                        x:control.LayoutMirroring.enabled ? 0:iconSlot.width+entry.iconGap
                        y:(parent.height-height)/2
                        horizontalAlignment:control.LayoutMirroring.enabled ? Qt.AlignRight:Qt.AlignLeft
                        clip:true
                    }
                }
            }
        }
    }
}
