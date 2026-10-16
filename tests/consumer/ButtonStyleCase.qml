import QtQuick
import Avelino

Item {
    id:root
    required property var definition
    property bool mounted:true
    property var calls:[]
    property var mountValues:[]
    property int appears:0
    property int destroyedCount:0
    readonly property Item control:zLoader.active ? zLoader.item:hLoader.active ? hLoader.item:vLoader.item
    readonly property Item parentLayout:definition.parentLayout==="hstack" ? horizontal:definition.parentLayout==="vstack" ? vertical:null
    readonly property Item leadingItem:definition.parentLayout==="hstack" ? hLeading:definition.parentLayout==="vstack" ? vLeading:null
    readonly property Item trailingItem:definition.parentLayout==="hstack" ? hTrailing:definition.parentLayout==="vstack" ? vTrailing:null
    readonly property int localValue:control ? control.localValue:0
    readonly property color paint:BleeckerTheme.alpha(BleeckerTokens.colors.light.sea,0.18)
    // Explicit platform sRGB values verified by the color replay and 64 source PNG samples.
    readonly property color parentGreen:BleeckerTheme.dark ? "#30d158":"#34c759"
    readonly property color parentOrange:BleeckerTheme.dark ? "#ff9230":"#ff8d28"
    width:definition.width;height:definition.height
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    function styleComponent(){
        const components={text:textStyle,counter:textStyle,rectangle:rectangleStyle,zero:zeroStyle,empty:emptyStyle,
            hidden:rectangleStyle,wide:rectangleStyle,"own-font":textStyle,"system-font":textStyle,"own-red":textStyle,
            multi:multiStyle,vstack:vstackStyle,hstack:hstackStyle,overflow:overflowStyle}
        const component=components[definition.content]
        if(!component)throw new Error("Unknown ButtonStyle caller content: "+definition.content)
        return component
    }
    component Shell:BleeckerButtonStyle {
        property int localValue:0
        variant:root.definition.variant;size:root.definition.size
        widthOffer:root.definition.offer===null ? -1:root.definition.offer
        maximumWidth:root.definition.parentLayout==="zstack" ? root.width:-1
        onClicked:{localValue++;root.calls=root.calls.concat([localValue])}
        Component.onCompleted:if(labels.length){root.appears++;root.mountValues=root.mountValues.concat([localValue])}
        Component.onDestruction:if(root && labels.length)root.destroyedCount++
    }
    component Label:Item {
        id:label
        required property var buttonStyle
        property alias text:renderer.text
        property font font:buttonStyle.presentationFont
        property color color:buttonStyle.foregroundColor
        readonly property real offeredWidth:BleeckerLayout.proposedWidth
        BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:renderer.unwrappedWidth
        implicitWidth:offeredWidth<0 ? renderer.implicitWidth:Math.ceil(Math.min(renderer.implicitWidth,offeredWidth)*alignment.devicePixelRatio)/alignment.devicePixelRatio
        implicitHeight:Math.ceil(renderer.naturalHeight*alignment.devicePixelRatio)/alignment.devicePixelRatio
        baselineOffset:renderer.baselineOffset
        ButtonLabel {
            id:renderer;font:label.font;color:label.color;wrapWidth:label.offeredWidth
            width:Math.max(label.width,implicitWidth);height:label.height
            PixelAlignment {id:alignment;target:label;origin:Qt.point(0,renderer.baselineOffset)}
            transform:Translate {x:alignment.offset.x;y:alignment.offset.y}
            Accessible.ignored:true
        }
        Accessible.ignored:true
    }
    InheritedControl {
        id:context;anchors.fill:parent
        padding:0;background:null;focusPolicy:Qt.NoFocus;Accessible.ignored:true
        font.pointSize:BleeckerFonts.pointSizeForPixels(root.definition.parentFont>0 ? root.definition.parentFont:13)
        font.weight:root.definition.parentFont>0 ? Font.Bold:Font.Normal
        palette.windowText:root.definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.nativeTextPrimary
        Loader {
            id:zLoader;active:root.mounted && root.definition.parentLayout==="zstack"
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            enabled:!root.definition.disabled;sourceComponent:root.styleComponent()
        }
        ProposalRow {
            id:horizontal;visible:root.definition.parentLayout==="hstack"
            anchors.centerIn:parent;anchors.alignWhenCentered:false;spacing:11;mirrored:context.mirrored
            Rectangle {id:hLeading;objectName:"buttonStyleLeading";implicitWidth:40;implicitHeight:12;color:BleeckerTheme.alpha(root.parentGreen,0.2)}
            Loader {
                id:hLoader;active:root.mounted && root.definition.parentLayout==="hstack"
                BleeckerLayout.flattenChildren:true
                enabled:!root.definition.disabled;sourceComponent:root.styleComponent()
            }
            Rectangle {id:hTrailing;objectName:"buttonStyleTrailing";implicitWidth:30;implicitHeight:20;color:BleeckerTheme.alpha(root.parentOrange,0.2)}
        }
        ProposalColumn {
            id:vertical;visible:root.definition.parentLayout==="vstack"
            anchors.centerIn:parent;anchors.alignWhenCentered:false;spacing:11;padding:0
            Rectangle {id:vLeading;objectName:"buttonStyleLeading";implicitWidth:40;implicitHeight:12;color:BleeckerTheme.alpha(root.parentGreen,0.2)}
            Loader {
                id:vLoader;active:root.mounted && root.definition.parentLayout==="vstack"
                BleeckerLayout.flattenChildren:true
                enabled:!root.definition.disabled;sourceComponent:root.styleComponent()
            }
            Rectangle {id:vTrailing;objectName:"buttonStyleTrailing";implicitWidth:30;implicitHeight:20;color:BleeckerTheme.alpha(root.parentOrange,0.2)}
        }
    }
    Component {
        id:textStyle
        Shell {
            id:style
            Label {
                objectName:"buttonStyleLabel";buttonStyle:style
                text:root.definition.content==="counter" ? "Publish "+style.localValue
                    :["own-font","system-font"].includes(root.definition.content) ? "Caller typography"
                    :root.definition.content==="own-red" ? "Caller foreground":root.definition.text
                font.family:root.definition.content==="own-font" ? BleeckerTheme.secondaryFont:root.definition.content==="system-font" ? Qt.application.font.family:style.presentationFont.family
                font.pointSize:root.definition.content==="own-font" ? BleeckerFonts.pointSizeForPixels(13):root.definition.content==="system-font" ? BleeckerFonts.pointSizeForPixels(32):style.presentationFont.pointSize
                font.weight:["own-font","system-font"].includes(root.definition.content) ? Font.Bold:style.presentationFont.weight
                color:root.definition.content==="own-red" ? BleeckerTheme.nativeRed:style.foregroundColor
            }
        }
    }
    Component {
        id:rectangleStyle
        Shell {
            Rectangle {
                objectName:"buttonStyleLabel";visible:root.definition.content!=="hidden"
                implicitWidth:root.definition.content==="wide" ? 800:200;implicitHeight:80;color:root.paint
            }
        }
    }
    Component {id:zeroStyle;Shell {Item {objectName:"buttonStyleLabel"}}}
    Component {id:emptyStyle;Shell {}}
    Component {
        id:multiStyle
        Shell {
            id:style
            Label {objectName:"buttonStyleFirst";buttonStyle:style;text:"First child"}
            Rectangle {objectName:"buttonStyleSecond";implicitWidth:72;implicitHeight:44;color:root.paint}
        }
    }
    Component {
        id:vstackStyle
        Shell {
            id:style
            ProposalColumn {
                objectName:"buttonStyleLabel";spacing:5;padding:0
                Label {buttonStyle:style;text:"First child"}
                Rectangle {implicitWidth:72;implicitHeight:44;color:root.paint}
            }
        }
    }
    Component {
        id:hstackStyle
        Shell {
            id:style
            ProposalRow {
                objectName:"buttonStyleLabel";spacing:5;mirrored:style.mirrored
                Label {buttonStyle:style;text:"First child"}
                Rectangle {implicitWidth:72;implicitHeight:44;color:root.paint}
            }
        }
    }
    Component {
        id:overflowStyle
        Shell {
            Rectangle {
                objectName:"buttonStyleLabel";implicitWidth:80;implicitHeight:36;color:root.paint
                Rectangle {anchors.centerIn:parent;anchors.alignWhenCentered:false;width:160;height:64;rotation:18;color:BleeckerTheme.alpha(BleeckerTheme.nativeRed,0.7)}
            }
        }
    }
}
