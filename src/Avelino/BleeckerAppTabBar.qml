import QtQuick
import QtQuick.Templates as T

T.Control {
    id:control
    required property var selection
    property var tabs:[]
    property var valueIdentity:null
    required property Component icon
    signal selectionRequested(var requestedValue)
    Component.onCompleted:row.validateComponent(icon,count)
    onIconChanged:if(row)row.validateComponent(icon,count)
    onCountChanged:if(row)row.validateComponent(icon,count)
    readonly property int count:buttons.count
    readonly property Item presentationItem:body
    readonly property real naturalWidth:row.naturalWidth
    readonly property real minimumWidth:row.minimumWidth
    function tabAt(index:int):Item{return buttons.itemAt(index)}
    implicitWidth:naturalWidth;implicitHeight:row.implicitHeight+5
    padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus
    BleeckerLayout.minimumWidth:minimumWidth
    BleeckerLayout.idealWidth:naturalWidth
    Accessible.ignored:true
    AppTabOptions {id:rows;tabs:control.tabs;selection:control.selection;valueIdentity:control.valueIdentity}
    Connections {target:rows;function onRowsMoved(){Qt.callLater(function(){row.layout()})}}
    Item {
        id:body;objectName:"bleeckerAppTabPresentation"
        width:row.width;height:row.height+5
        x:(control.width-width)/2;y:(control.height-height)/2
        Rectangle {anchors.fill:parent;color:BleeckerTheme.palette.card;Accessible.ignored:true}
        AppTabRow {
            id:row;y:5;proposalOwner:control
            proposedWidth:control.BleeckerLayout.proposedWidth>=0 ? control.BleeckerLayout.proposedWidth:control.availableWidth
            mirrored:control.mirrored
            Repeater {
                id:buttons;model:rows
                AppTabButton {
                    id:button
                    required property int index
                    required property var tabValue
                    required property string tabLabel
                    required property string tabSystemImage
                    required property string tabAccessibilityLabel
                    required property bool tabDisabled
                    required property bool tabSelected
                    required property string tabKey
                    required property string tabBadgeText
                    required property string tabBadgeValue
                    required property bool tabBadgeVisible
                    readonly property bool selected:tabSelected
                    readonly property real minimumWidth:glyph.implicitWidth
                    readonly property real naturalWidth:Math.max(minimumWidth,naturalLabel.unwrappedWidth)
                    readonly property Item iconItem:glyph
                    readonly property Item titleItem:label
                    readonly property Item badgeItem:badge
                    readonly property color foregroundColor:selected ? BleeckerTheme.palette.sea:BleeckerTheme.palette.textSecondary
                    objectName:"bleeckerAppTab"+index
                    enabled:!tabDisabled;text:tabLabel
                    accessibleTitle:tabAccessibilityLabel;notificationValue:tabBadgeValue
                    padding:0;background:null;focusPolicy:Qt.StrongFocus;autoRepeat:false;checkable:false
                    font.family:BleeckerTheme.primaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(10)
                    font.weight:selected ? Font.DemiBold:Font.Medium
                    implicitWidth:naturalWidth;implicitHeight:Math.max(54,glyph.height+3+label.height)
                    onIndexChanged:if(pressed)ungrabPointer()
                    function ungrabPointer():void {row.cancelPress(button)}
                    onClicked:if(control.enabled &&enabled)control.selectionRequested(tabValue)
                    Accessible.role:Accessible.Button
                    Accessible.name:tabAccessibilityLabel
                    Accessible.selected:selected
                    Accessible.selectable:true
                    ContinuousSurface {
                        anchors.fill:parent;radius:BleeckerTokens.radii.button
                        color:"transparent";borderColor:BleeckerTheme.alpha(BleeckerTheme.palette.ring,0.75)
                        visible:button.visualFocus;Accessible.ignored:true
                    }
                    contentItem:Item {
                        opacity:button.enabled ? 1:0.5
                        Loader {
                            id:glyph;objectName:"bleeckerAppTabIcon"
                            readonly property string systemImage:button.tabSystemImage
                            readonly property var tabValue:button.tabValue
                            readonly property bool selected:button.selected
                            readonly property real pixelSize:18
                            readonly property font font:Qt.font({family:Qt.application.font.family,pointSize:BleeckerFonts.pointSizeForPixels(18),weight:button.selected ? Font.DemiBold:Font.Normal})
                            readonly property color foregroundColor:button.foregroundColor
                            sourceComponent:control.icon
                            onLoaded:row.validateIcon(item)
                            x:(parent.width-width)/2;y:(parent.height-height-3-label.height)/2
                            Accessible.ignored:true

                        }
                        Rectangle {
                            id:badge;objectName:"bleeckerAppTabBadge"
                            visible:button.tabBadgeVisible
                            width:Math.max(15,badgeLabel.unwrappedWidth+8);height:Math.max(15,badgeLabel.height)
                            x:glyph.x+(control.mirrored ? 0:glyph.width-width);y:glyph.y
                            transform:Translate{x:control.mirrored ? -10:10;y:-7}
                            radius:height/2;color:BleeckerTheme.palette.sunset
                            Accessible.ignored:true
                            OwnedText {
                                id:badgeLabel;anchors.centerIn:parent
                                text:button.tabBadgeText;color:"white"
                                font.family:BleeckerTheme.primaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(8);font.weight:Font.Bold
                            }
                        }
                        OwnedText {id:naturalLabel;visible:false;text:button.tabLabel;font:button.font}
                        Item {
                            id:label;objectName:"bleeckerAppTabLabel"
                            readonly property bool naturalFits:naturalLabel.unwrappedWidth<=button.width &&naturalLabel.linePositions.length<=2
                            width:naturalFits ? naturalLabel.unwrappedWidth:Math.ceil(Math.min(fitted.contentWidth,button.width)*pixel.devicePixelRatio)/pixel.devicePixelRatio
                            height:naturalFits ? naturalLabel.height:fitted.implicitHeight
                            x:(parent.width-width)/2;y:glyph.y+glyph.height+3
                            PixelAlignment {id:pixel;target:label}
                            OwnedText {
                                visible:label.naturalFits
                                text:button.tabLabel;font:button.font;color:button.foregroundColor
                            }
                            Text {
                                id:fitted;visible:!label.naturalFits
                                text:button.tabLabel;font:button.font;color:button.foregroundColor
                                x:(label.width-width)/2;width:button.width
                                horizontalAlignment:Text.AlignHCenter
                                wrapMode:Text.Wrap;maximumLineCount:2;elide:Text.ElideRight
                                fontSizeMode:Text.Fit;minimumPointSize:BleeckerFonts.pointSizeForPixels(8)
                                onWidthChanged:forceLayout()
                                Accessible.ignored:true
                            }
                            Accessible.ignored:true
                        }
                    }
                }
            }
        }
        BleeckerSeparator {width:parent.width;anchors.top:parent.top}
    }
}
