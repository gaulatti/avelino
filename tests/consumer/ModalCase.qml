import QtQuick
import QtQuick.Templates as T
import Avelino

T.Control {
    id:fixture
    required property var definition
    property bool mounted:true
    property string edition:"Draft edition"
    property var calls:[]
    property int appears:0
    property var mountValues:[]
    property int disappears:0
    property int localValue:-1
    property int dismissals:0
    signal dismissalRequested()
    readonly property Item control:modalLoader.item
    readonly property Item presentationItem:control ? control.presentationItem:null
    readonly property color callerColor:BleeckerTheme.alpha(BleeckerTokens.colors.light.sea,0.18)
    implicitWidth:definition.width;implicitHeight:definition.height
    padding:0;background:null;focusPolicy:Qt.NoFocus
    font.family:BleeckerTheme.primaryFont
    font.pointSize:BleeckerFonts.pointSizeForPixels(definition.parentFont>0 ? definition.parentFont:13)
    font.weight:definition.parentFont>0 ? Font.Bold:Font.Normal
    palette.windowText:definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.nativeTextPrimary
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    function contentFactory(){
        switch(definition.content){
        case "empty":return null
        case "zero":case "hidden":case "tall":case "wide":case "rectangle":return rectangle
        case "fills":return fills
        case "text":case "text-empty":case "text-lines":return label
        case "inherited":return inherited
        case "multi":return multiple
        case "vstack":return vertical
        case "hstack":return horizontal
        case "counter":return counter
        case "editor":return editor
        case "wide-button":return wideButton
        default:throw new Error("Unknown Modal content fixture: "+definition.content)
        }
    }
    Loader {
        id:modalLoader;active:fixture.mounted;sourceComponent:modalFactory
        x:(fixture.width-width)/2;y:(fixture.height-height)/2
    }
    Component {
        id:modalFactory
        BleeckerModal {
            objectName:"fixtureModal";title:fixture.definition.title;modalWidth:fixture.definition.modalWidth
            width:fixture.definition.outerOffer===null ? modalWidth:fixture.definition.outerOffer
            enabled:!fixture.definition.disabled
            dismissAction:function(){fixture.dismissals++;fixture.dismissalRequested()}
            Loader {
                sourceComponent:fixture.contentFactory()
                BleeckerLayout.flattenChildren:true
                BleeckerLayout.participates:item!==null
            }
        }
    }
    Component {
        id:rectangle
        Rectangle {
            objectName:"modalContent-"+fixture.definition.content
            implicitWidth:fixture.definition.content==="zero" ? 0:fixture.definition.content==="wide" ? 800:fixture.definition.content==="tall" ? 72:200
            implicitHeight:fixture.definition.content==="zero" ? 0:fixture.definition.content==="tall" ? 320:80
            visible:fixture.definition.content!=="hidden"
            color:fixture.definition.content==="zero" ? "transparent":fixture.callerColor
        }
    }
    Component {id:fills;Rectangle {objectName:"modalContent-fills";implicitHeight:80;color:fixture.callerColor;BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:0;BleeckerLayout.fillsWidth:true}}
    Component {
        id:label
        ButtonLabel {
            objectName:"modalContent-text"
            text:fixture.definition.content==="text-empty" ? "":fixture.definition.content==="text-lines" ? "First line\nSecond line":"Review the selected edition before publishing."
            font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13);font.weight:Font.Normal
            color:fixture.control.foreground;wrapWidth:BleeckerLayout.proposedWidth
            horizontalAlignment:fixture.control.mirrored ? Qt.AlignRight:Qt.AlignLeft
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:unwrappedWidth
        }
    }
    Component {
        id:inherited
        ButtonLabel {
            objectName:"modalContent-text";text:"Inherited content";font:fixture.control.presentationFont;color:fixture.control.foreground
            wrapWidth:BleeckerLayout.proposedWidth;BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:unwrappedWidth
            horizontalAlignment:fixture.control.mirrored ? Qt.AlignRight:Qt.AlignLeft
        }
    }
    Component {
        id:multiple
        Item {
            BleeckerLayout.flattenChildren:true
            ButtonLabel {
                objectName:"modalContent-first";text:"First child";wrapWidth:BleeckerLayout.proposedWidth
                font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13);font.weight:Font.Normal;color:fixture.control.foreground
                BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:unwrappedWidth
            }
            Rectangle {objectName:"modalContent-second";implicitWidth:72;implicitHeight:44;color:fixture.callerColor}
        }
    }
    Component {
        id:vertical
        ProposalColumn {
            objectName:"modalContent-vstack";maximumWidth:BleeckerLayout.proposedWidth;spacing:5
            BleeckerLayout.minimumWidth:minimumWidth;BleeckerLayout.idealWidth:naturalWidth
            ButtonLabel {
                text:"First child";wrapWidth:BleeckerLayout.proposedWidth
                font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13);font.weight:Font.Normal;color:fixture.control.foreground
                BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:unwrappedWidth
            }
            Rectangle {implicitWidth:72;implicitHeight:44;color:fixture.callerColor}
        }
    }
    Component {
        id:horizontal
        ProposalRow {
            objectName:"modalContent-hstack";maximumWidth:BleeckerLayout.proposedWidth;spacing:5;mirrored:fixture.control.mirrored
            BleeckerLayout.minimumWidth:minimumWidth;BleeckerLayout.idealWidth:naturalWidth
            ButtonLabel {
                text:"First child";wrapWidth:BleeckerLayout.proposedWidth
                font.family:BleeckerTheme.secondaryFont;font.pointSize:BleeckerFonts.pointSizeForPixels(13);font.weight:Font.Normal;color:fixture.control.foreground
                BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:unwrappedWidth
            }
            Rectangle {implicitWidth:72;implicitHeight:44;color:fixture.callerColor}
        }
    }
    Component {
        id:counter
        BleeckerButton {
            objectName:"modalContent-counter";property int value:0;text:"Count "+value;variant:"secondary";size:"sm"
            onClicked:{value++;fixture.localValue=value;fixture.calls=fixture.calls.concat(["counter:"+value])}
            Component.onCompleted:{fixture.appears++;fixture.localValue=value;fixture.mountValues=fixture.mountValues.concat([value])}
            Component.onDestruction:if(fixture){fixture.disappears++;fixture.localValue=-1}
        }
    }
    Component {
        id:editor
        BleeckerTextField {
            objectName:"modalContent-editor";placeholderText:"Edition name";text:fixture.edition
            onTextEdited:fixture.edition=text
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:implicitWidth;BleeckerLayout.fillsWidth:true
        }
    }
    Component {
        id:wideButton
        BleeckerButton {
            objectName:"modalContent-wide-button";variant:"secondary";size:"sm"
            onClicked:fixture.calls=fixture.calls.concat(["wide"])
            contentItem:Item {implicitWidth:800;implicitHeight:80;Rectangle {anchors.fill:parent;color:fixture.callerColor}}
        }
    }
}
