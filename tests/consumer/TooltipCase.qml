import QtQuick
import QtQuick.Templates as T
import Avelino

Item {
    id:root
    required property var definition
    property bool mounted:true
    property bool helpAttached:definition.helpAttached!==false
    property var calls:[]
    property var mountValues:[]
    property int appears:0
    property int destroyedCount:0
    readonly property Item control:loader.item
    readonly property BleeckerTooltip help:helpAdapter
    readonly property bool mirrored:context.mirrored
    readonly property int localValue:control && definition.content==="button" ? control.value:0
    width:definition.width; height:definition.height
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    InheritedControl {
        id:context;anchors.fill:parent
        padding:0;background:null;focusPolicy:Qt.NoFocus;Accessible.ignored:true
        font.pointSize:BleeckerFonts.pointSizeForPixels(root.definition.parentFont>0 ? root.definition.parentFont:13)
        font.weight:root.definition.parentFont>0 ? Font.Bold:Font.Normal
        palette.windowText:root.definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.nativeTextPrimary
        Loader {
            id:loader;active:root.mounted
            anchors.centerIn:parent;anchors.alignWhenCentered:false
            enabled:!root.definition.disabled
            sourceComponent:{
                const map={button:counter,rectangle:rectangle,zero:zero,empty:zero,hidden:hidden,wide:wide,text:label,inherited:inherited,multi:multi,vstack:vstack,hstack:hstack,"wide-button":wideButton}
                if(!map[root.definition.content])throw new Error("Unknown Tooltip caller content")
                return map[root.definition.content]
            }
        }
    }
    BleeckerTooltip {id:helpAdapter;target:root.helpAttached ? loader.item:null;text:root.definition.hint}
    Component {
        id:counter
        BleeckerButton {
            objectName:"tooltipCallerButton";property int value:0
            text:"Publish "+value;variant:"secondary";size:"sm"
            onClicked:{value++;root.calls=root.calls.concat([value])}
            Component.onCompleted:{root.appears++;root.mountValues=root.mountValues.concat([value])}
            Component.onDestruction:if(root)root.destroyedCount++
        }
    }
    Component {id:rectangle;Rectangle {objectName:"tooltipCallerRectangle";implicitWidth:200;implicitHeight:80;color:BleeckerTheme.alpha(BleeckerTokens.colors.light.sea,0.18)}}
    Component {id:zero;Item {implicitWidth:0;implicitHeight:0}}
    Component {id:hidden;Rectangle {visible:false;implicitWidth:200;implicitHeight:80;color:BleeckerTheme.alpha(BleeckerTokens.colors.light.sea,0.18)}}
    Component {id:wide;Rectangle {implicitWidth:800;implicitHeight:80;color:BleeckerTheme.alpha(BleeckerTokens.colors.light.sea,0.18)}}
    Component {id:label;ButtonLabel {text:"Review the selected edition";font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13);color:context.resolvedTextColor}}
    Component {id:inherited;ButtonLabel {text:"Inherited content";font:context.presentationFont;color:context.resolvedTextColor}}
    Component {
        id:multi
        Item {
            implicitWidth:Math.max(first.width,second.width);implicitHeight:Math.max(first.height,second.height)
            ButtonLabel {id:first;objectName:"tooltipCallerFirst";anchors.centerIn:parent;anchors.alignWhenCentered:false;text:"First child";font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13);color:context.resolvedTextColor}
            Rectangle {id:second;objectName:"tooltipCallerSecond";anchors.centerIn:parent;anchors.alignWhenCentered:false;width:72;height:44;color:BleeckerTheme.alpha(BleeckerTokens.colors.light.sea,0.18)}
        }
    }
    Component {
        id:vstack
        Column {
            spacing:5
            ButtonLabel {text:"First child";x:(parent.width-width)/2;font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13);color:context.resolvedTextColor}
            Rectangle {width:72;height:44;x:(parent.width-width)/2;color:BleeckerTheme.alpha(BleeckerTokens.colors.light.sea,0.18)}
        }
    }
    Component {
        id:hstack
        Row {
            spacing:5
            ButtonLabel {text:"First child";y:(parent.height-height)/2;font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13);color:context.resolvedTextColor}
            Rectangle {width:72;height:44;y:(parent.height-height)/2;color:BleeckerTheme.alpha(BleeckerTokens.colors.light.sea,0.18)}
        }
    }
    Component {
        id:wideButton
        BleeckerButton {
            objectName:"tooltipCallerWideButton";variant:"secondary";size:"sm"
            contentItem:Rectangle {implicitWidth:800;implicitHeight:80;color:BleeckerTheme.alpha(BleeckerTokens.colors.light.sea,0.18)}
            onClicked:root.calls=root.calls.concat([1])
        }
    }
}
