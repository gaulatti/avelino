import QtQuick
import QtQuick.Templates as T

T.Control {
    id:control
    required property string label
    required property real value
    required property Component icon
    property string format:"number"
    property var delta:null
    property real maximumWidth:-1
    readonly property bool hasDelta:delta!==null && delta!==undefined
    readonly property real deltaValue:{if(!hasDelta)return 0;if(typeof delta!=="number")throw new Error("Stat-card delta must be a number or null");return delta}
    readonly property string formattedDelta:hasDelta ? BleeckerNumberTools.format(deltaValue,"percent","USD",locale,true):""
    readonly property Item presentationItem:card
    readonly property Item metricItem:metric
    padding:0;background:null
    implicitWidth:card.implicitWidth;implicitHeight:card.implicitHeight
    BleeckerCard {
        id:card;objectName:"bleeckerStatCardPresentation"
        x:(control.width-width)/2;y:(control.height-height)/2
        implicitWidth:row.implicitWidth+48;implicitHeight:row.implicitHeight+48
        ProposalRow {
            id:row;objectName:"bleeckerStatCardRow";spacing:0;verticalAlignment:Qt.AlignTop
            maximumWidth:BleeckerTextTools.proposedWidth(control.maximumWidth,48);mirrored:control.LayoutMirroring.enabled
            BleeckerMetric {
                id:metric;objectName:"bleeckerStatCardMetric";label:control.label;value:control.value;format:control.format
                BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:naturalWidth
            }
            Item {objectName:"bleeckerStatCardSpacer";implicitWidth:8;BleeckerLayout.fillsWidth:true;Accessible.ignored:true}
            Item {
                id:trailing;objectName:"bleeckerStatCardTrailing"
                BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:Math.max(36,change.unwrappedWidth)
                implicitWidth:Math.max(36,change.width);implicitHeight:36+(control.hasDelta ? 8+change.height:0)
                BleeckerIconBadge {
                    id:badge;objectName:"bleeckerStatCardBadge";variant:"subtle";icon:control.icon
                    x:control.LayoutMirroring.enabled ? 0:trailing.width-width
                }
                OwnedText {
                    id:change;objectName:"bleeckerStatCardDelta";visible:control.hasDelta;text:control.formattedDelta;y:44
                    font.pointSize:BleeckerFonts.pointSizeForPixels(11);font.weight:Font.DemiBold
                    color:control.deltaValue>=0 ? BleeckerTokens.colors.light.live:BleeckerTokens.colors.light.destructive
                    wrapWidth:trailing.BleeckerLayout.proposedWidth
                    width:wrapWidth<0 ? implicitWidth:Math.min(implicitWidth,wrapWidth)
                    x:control.LayoutMirroring.enabled ? 0:trailing.width-width;clip:true
                    Accessible.ignored:!visible;Accessible.role:Accessible.StaticText;Accessible.name:text
                }
            }
        }
    }
    Accessible.ignored:true
}
