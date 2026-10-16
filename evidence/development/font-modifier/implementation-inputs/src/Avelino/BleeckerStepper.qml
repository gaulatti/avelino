import QtQuick
import QtQuick.Templates as T

T.Control {
    id:control
    required property string label
    required property var value
    required property var lowerBound
    required property var upperBound
    property var step:1
    property var displayOffset:0
    property real maximumWidth:-1
    signal valueRequested(string requestedValue)
    readonly property var valueState:BleeckerValueTools.stepper(value,lowerBound,upperBound,step,displayOffset,BleeckerNumberTools.processLocale)
    readonly property Item presentationItem:body
    readonly property Item decrementInput:minus
    readonly property Item incrementInput:plus
    readonly property real glyphPixelSize:font.pixelSize>0 ? font.pixelSize:font.pointSize/BleeckerFonts.pointSizeForPixels(1)
    readonly property real minimumWidth:20+1+minus.implicitWidth+valueFrame.width+plus.implicitWidth
    readonly property real naturalWidth:labelText.unwrappedWidth+minimumWidth
    readonly property real effectiveMaximumWidth:BleeckerLayout.proposedWidth<0 ? maximumWidth
        : maximumWidth<0 ? BleeckerLayout.proposedWidth:Math.min(maximumWidth,BleeckerLayout.proposedWidth)
    readonly property real proposal:BleeckerTextTools.proposedWidth(effectiveMaximumWidth,0)
    implicitWidth:proposal<0 ? naturalWidth:Math.max(minimumWidth,Math.min(naturalWidth,proposal))
    implicitHeight:36
    padding:0;background:null
    font.family:BleeckerTheme.primaryFont
    font.pointSize:BleeckerFonts.pointSizeForPixels(13)
    BleeckerLayout.minimumWidth:minimumWidth
    BleeckerLayout.idealWidth:naturalWidth
    Accessible.ignored:true
    Item {
        id:body;objectName:"bleeckerStepperPresentation"
        x:(control.width-width)/2;y:(control.height-height)/2
        width:labelText.width+control.minimumWidth;height:36
        CircularContent {
            anchors.fill:parent;radius:BleeckerTokens.radii.ui
            Rectangle {anchors.fill:parent;color:BleeckerTheme.palette.card}
            Row {
                id:row;objectName:"bleeckerStepperContent"
                height:36;spacing:0
                Item {
                    width:labelText.width+20;height:labelText.height;y:(row.height-height)/2
                    OwnedText {
                        id:labelText;objectName:"bleeckerStepperLabel";x:10
                        text:control.label
                        font.family:BleeckerTheme.primaryFont
                        font.pointSize:BleeckerFonts.pointSizeForPixels(13)
                        elideWidth:Math.max(0,(control.proposal<0 ? control.availableWidth:Math.min(control.availableWidth,control.proposal))-control.minimumWidth)
                        color:BleeckerTheme.palette.textSecondary
                        Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
                    }
                }
                Rectangle {
                    objectName:"bleeckerStepperDivider";width:1;height:24;y:6
                    color:BleeckerTheme.nativeSeparator
                    Accessible.ignored:true
                }
                T.Button {
                    id:minus;objectName:"bleeckerStepperDecrement"
                    y:(row.height-height)/2
                    implicitWidth:minusGlyph.implicitWidth;implicitHeight:minusGlyph.implicitHeight
                    padding:0;background:null;autoRepeat:false
                    enabled:control.valueState.decrementEnabled
                    focusPolicy:Qt.StrongFocus
                    Accessible.name:qsTr("Decrease %1").arg(control.label)
                    onClicked:if(control.enabled && enabled)control.valueRequested(BleeckerValueTools.stepperRequest(control.value,control.lowerBound,control.upperBound,control.step,false))
                    contentItem:StepperGlyph {
                        id:minusGlyph;pixelSize:control.glyphPixelSize
                        color:minus.enabled ? BleeckerTheme.nativeEditorPlaceholder:BleeckerTheme.nativeEditorDisabledText
                    }
                }
                Item {
                    id:valueFrame;objectName:"bleeckerStepperValueFrame"
                    width:Math.max(34,valueText.implicitWidth);height:valueText.height;y:(row.height-height)/2
                    OwnedText {
                        id:valueText;objectName:"bleeckerStepperValue"
                        text:control.valueState.formattedValue
                        x:(valueFrame.width-width)/2
                        font.family:BleeckerFonts.monospace
                        font.pointSize:BleeckerFonts.pointSizeForPixels(12);font.weight:Font.Bold
                        color:BleeckerTheme.nativeTextPrimary
                        Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
                    }
                }
                T.Button {
                    id:plus;objectName:"bleeckerStepperIncrement"
                    y:(row.height-height)/2
                    implicitWidth:plusGlyph.implicitWidth;implicitHeight:plusGlyph.implicitHeight
                    padding:0;background:null;autoRepeat:false
                    enabled:control.valueState.incrementEnabled
                    focusPolicy:Qt.StrongFocus
                    Accessible.name:qsTr("Increase %1").arg(control.label)
                    onClicked:if(control.enabled && enabled)control.valueRequested(BleeckerValueTools.stepperRequest(control.value,control.lowerBound,control.upperBound,control.step,true))
                    contentItem:StepperGlyph {
                        id:plusGlyph;increment:true;pixelSize:control.glyphPixelSize
                        color:plus.enabled ? BleeckerTheme.nativeEditorPlaceholder:BleeckerTheme.nativeEditorDisabledText
                    }
                }
            }
        }
        Rectangle {anchors.fill:parent;radius:BleeckerTokens.radii.ui;color:"transparent";border.width:1;border.color:BleeckerTheme.palette.border;antialiasing:true;Accessible.ignored:true}
    }
}
