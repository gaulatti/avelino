import QtQuick
import QtQuick.Templates as T

T.Control {
    id: control
    required property string title
    property bool initiallyExpanded: false
    property Component content: null
    readonly property bool expanded: state.expanded
    readonly property Item inputItem: header
    readonly property Item loadedContent: slot.item
    readonly property bool roundedContentClipping: clipHost.roundedClipping
    readonly property real transitionProgress: state.progress
    padding: 14
    implicitWidth: padding*2 + Math.max(header.implicitWidth,slot.implicitWidth)
    implicitHeight: padding*2 + header.height + (content ? transitionProgress*(10+slot.height) : 0)
    contentItem: null
    Accessible.ignored: true
    QtObject {
        id:state
        property bool expanded:false
        property bool complete:false
        property real progress:expanded ? 1 : 0
        Behavior on progress {
            enabled:state.complete
            NumberAnimation {id:revealAnimation;duration:BleeckerTheme.reducedMotion ? 0 : BleeckerTokens.durations.standard;easing.type:Easing.BezierSpline;easing.bezierCurve:[0,0,0.58,1,1,1]}
        }
    }
    Component.onCompleted:{state.expanded=initiallyExpanded;state.complete=true}
    Connections {target:BleeckerTheme;function onReducedMotionChanged(){if(BleeckerTheme.reducedMotion) revealAnimation.complete()}}
    PixelAlignment {id: metrics;target:control}
    function contentHasFocus() {
        const window=control.Window.window
        let item=window ? window.activeFocusItem : null
        while(item){if(item===slot)return true;item=item.parent}
        return false
    }
    background: ContinuousSurface {
        objectName: "bleeckerAccordionSurface"
        radius:BleeckerTokens.radii.ui;color:BleeckerTheme.palette.card;borderColor:BleeckerTheme.palette.border
    }
    RoundedContent {
        id:clipHost
        objectName:"bleeckerAccordionClip"
        anchors.fill:parent;radius:BleeckerTokens.radii.ui
        Item {
            x:control.leftPadding;y:control.topPadding
            width:control.availableWidth;height:Math.max(0,control.height-control.padding*2)
            T.Button {
                id:header
                objectName:"bleeckerAccordionHeader"
                width:parent.width;height:implicitHeight
                implicitWidth:label.unwrappedWidth+8+glyph.width
                implicitHeight:Math.max(label.height,glyph.height)
                padding:0;focusPolicy:Qt.StrongFocus
                text:control.title
                opacity:!enabled ? 0.5 : down ? 0.75 : 1
                Accessible.name:control.title
                Accessible.description:control.expanded ? qsTr("Expanded") : qsTr("Collapsed")
                containmentMask:QtObject {
                    function contains(point: point): bool {
                        const inTitle=point.x>=label.x && point.x<label.x+label.width && point.y>=label.y && point.y<label.y+label.height
                        const inGlyph=point.x>=glyph.x && point.x<glyph.x+glyph.width && point.y>=glyph.y && point.y<glyph.y+glyph.height
                        return inTitle || inGlyph
                    }
                }
                onClicked: {
                    if(control.expanded && control.contentHasFocus()) header.forceActiveFocus(Qt.OtherFocusReason)
                    state.expanded=!state.expanded
                }
                background:null
                contentItem:Item {
                    OwnedText {
                        id:label
                        objectName:"bleeckerAccordionTitle"
                        text:control.title
                        font.pointSize:BleeckerFonts.pointSizeForPixels(14);font.weight:Font.DemiBold
                        color:BleeckerTheme.nativeTextPrimary
                        wrapWidth:Math.max(0,header.width-glyph.width-8)
                        x:control.mirrored ? header.width-width : 0;y:(header.height-height)/2
                    }
                    Item {
                        id:glyph
                        objectName:"bleeckerAccordionChevron"
                        // The source NSImage representation changes at its 2x bucket.
                        width:metrics.devicePixelRatio<2 ? 16 : 14.5
                        height:metrics.devicePixelRatio<2 ? 9 : 8.5
                        x:control.mirrored ? 0 : header.width-width;y:(header.height-height)/2
                        Accessible.ignored:true
                        NavigationGlyph {
                            anchors.centerIn:parent;direction:"right";pixelSize:13
                            color:BleeckerTheme.nativeTextPrimary
                            rotation:90+control.transitionProgress*180
                        }
                    }
                    Rectangle {
                        anchors.fill:parent;anchors.margins:-2
                        visible:header.visualFocus;color:"transparent";radius:BleeckerTokens.radii.ui
                        border.width:1;border.color:BleeckerTheme.palette.ring
                    }
                }
            }
            Loader {
                id:slot
                objectName:"bleeckerAccordionContent"
                readonly property real availableWidth:control.availableWidth
                sourceComponent:control.content
                active:control.content!==null && (control.expanded || control.transitionProgress>0)
                enabled:control.expanded;visible:control.transitionProgress>0
                opacity:control.transitionProgress
                x:control.mirrored ? parent.width-width : 0
                y:header.height+10-(1-control.transitionProgress)*height
            }
        }
    }
}
