import QtQuick
import QtQuick.Templates as T

Item {
    id:control
    required property string title
    required property Component icon
    required property bool selected
    property real maximumWidth:-1
    readonly property Item presentationItem:button
    readonly property Item inputItem:button
    readonly property color foregroundColor:selected ? BleeckerTheme.palette.sea:BleeckerTheme.palette.textSecondary
    readonly property bool down:button.down
    signal clicked()
    implicitWidth:button.implicitWidth;implicitHeight:button.implicitHeight
    T.Button {
        id:button;objectName:"bleeckerSidebarButton"
        x:(control.width-width)/2;y:(control.height-height)/2
        text:control.title;padding:0;focusPolicy:Qt.StrongFocus
        font.family:BleeckerTheme.primaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(14);font.weight:Font.Medium
        implicitWidth:row.implicitWidth+24;implicitHeight:Math.max(40,row.implicitHeight)
        background:null
        Accessible.name:text;Accessible.role:Accessible.Button
        Accessible.description:control.selected ? qsTr("Selected"):qsTr("Not selected")
        onClicked:control.clicked()
        contentItem:Item {
            opacity:button.enabled ? 1:0.5
            CircularContent {
                anchors.fill:parent
                Rectangle {anchors.fill:parent;radius:BleeckerTokens.radii.ui;color:control.selected ? BleeckerTheme.alpha(BleeckerTheme.palette.muted,0.8):"transparent";antialiasing:true;Accessible.ignored:true}
                ProposalRow {
                    id:row;objectName:"bleeckerSidebarRow"
                    x:12;y:(parent.height-height)/2
                    maximumWidth:BleeckerTextTools.proposedWidth(control.maximumWidth,24)
                    spacing:BleeckerTokens.spacing.control;mirrored:control.LayoutMirroring.enabled
                    Item {
                        id:glyph;objectName:"bleeckerSidebarIcon"
                        implicitWidth:20;implicitHeight:iconSlot.implicitHeight
                        Loader {
                            id:iconSlot;anchors.centerIn:parent;width:20;sourceComponent:control.icon
                            readonly property font font:Qt.font({family:Qt.application.font.family,pointSize:BleeckerFonts.pointSizeForPixels(15),weight:Font.Medium})
                            readonly property real pixelSize:15
                            readonly property color foregroundColor:control.foregroundColor
                        }
                        Accessible.ignored:true
                    }
                    Item {
                        id:labelBox;objectName:"bleeckerSidebarTitleBox"
                        BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:label.unwrappedWidth
                        implicitWidth:label.width;implicitHeight:label.height
                        OwnedText {
                            id:label;objectName:"bleeckerSidebarTitle";text:control.title;font:button.font;color:control.foregroundColor
                            wrapWidth:labelBox.BleeckerLayout.proposedWidth
                            width:wrapWidth<0 ? implicitWidth:Math.min(implicitWidth,wrapWidth)
                            horizontalAlignment:control.LayoutMirroring.enabled ? Qt.AlignRight:Qt.AlignLeft
                            clip:true
                        }
                    }
                    Item {implicitWidth:8;BleeckerLayout.fillsWidth:true;Accessible.ignored:true}
                }
            }
            Rectangle {
                objectName:"bleeckerSidebarSelectionBar"
                visible:control.selected;width:2;height:24;y:(parent.height-height)/2
                x:control.LayoutMirroring.enabled ? parent.width-width:0
                color:BleeckerTheme.palette.sea;Accessible.ignored:true
            }
        }
    }
    Accessible.ignored:true
}
