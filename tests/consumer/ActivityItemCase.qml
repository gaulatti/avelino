import QtQuick
import QtQuick.Templates as T
import Avelino

T.Control {
    id:fixture
    required property var definition
    readonly property Item control:activity
    readonly property Item presentationItem:activity.presentationItem
    readonly property string actionMode:definition.actions
    property var calls:[]
    property int appears:0
    property int disappears:0
    property int localValue:-1
    property int reportedCount:0
    readonly property real offer:definition.intrinsic ? definition.width:definition.proposalWidth
    implicitWidth:offer;implicitHeight:activity.implicitHeight
    padding:0;background:null;focusPolicy:Qt.NoFocus
    font.family:BleeckerTheme.primaryFont
    font.pointSize:BleeckerFonts.pointSizeForPixels(definition.parentFont>0 ? definition.parentFont:13)
    font.weight:definition.parentFont>0 ? Font.Bold:Font.Normal
    palette.windowText:definition.parentForeground==="red" ? BleeckerTheme.nativeRed:BleeckerTheme.nativeTextPrimary
    LayoutMirroring.enabled:definition.rtl;LayoutMirroring.childrenInherit:true
    function invoke(name:string){if(name==="counter")reportedCount=localValue;calls=calls.concat([name])}
    BleeckerActivityItem {
        id:activity;objectName:"fixtureActivityItem"
        x:(fixture.width-width)/2;y:(fixture.height-height)/2
        title:fixture.definition.title;detail:fixture.definition.detail;timestamp:fixture.definition.timestamp
        maximumWidth:fixture.offer;enabled:!fixture.definition.disabled
        locale:Qt.locale(fixture.definition.environmentLocale)
        Binding {target:activity;property:"icon";when:fixture.definition.symbol!=="clock";value:fixture.definition.symbol==="" ? null:alternateIcon}
        Loader {
            active:["button","multi","multi-direct","hidden"].includes(fixture.actionMode)
            visible:fixture.actionMode!=="hidden"
            BleeckerLayout.flattenChildren:true
            BleeckerLayout.participates:active && item!==null
            sourceComponent:review
        }
        Loader {
            active:["multi","multi-direct"].includes(fixture.actionMode)
            BleeckerLayout.flattenChildren:true
            BleeckerLayout.participates:active && item!==null
            sourceComponent:archive
        }
        Loader {
            active:fixture.actionMode==="nested"
            BleeckerLayout.flattenChildren:true
            BleeckerLayout.participates:active && item!==null
            sourceComponent:nested
        }
        Loader {
            active:fixture.actionMode==="plain"
            BleeckerLayout.flattenChildren:true
            BleeckerLayout.participates:active && item!==null
            sourceComponent:plain
        }
        Loader {
            active:["rect","tall","zero"].includes(fixture.actionMode)
            BleeckerLayout.flattenChildren:true
            BleeckerLayout.participates:active && item!==null
            sourceComponent:rectangle
        }
        Loader {
            active:fixture.actionMode==="counter"
            BleeckerLayout.flattenChildren:true
            BleeckerLayout.participates:active && item!==null
            sourceComponent:counter
        }
    }
    Component {id:review;BleeckerButton {objectName:"activityActionReview";text:"Review";variant:"secondary";size:"sm";onClicked:fixture.invoke("review")}}
    Component {id:archive;BleeckerButton {objectName:"activityActionArchive";text:"Archive";variant:"ghost";size:"sm";onClicked:fixture.invoke("archive")}}
    Component {
        id:nested
        ProposalRow {
            objectName:"activityActionNested";spacing:5;mirrored:activity.mirrored
            maximumWidth:BleeckerLayout.proposedWidth
            BleeckerLayout.minimumWidth:minimumWidth;BleeckerLayout.idealWidth:naturalWidth
            BleeckerButton {objectName:"activityActionReview";text:"Review";variant:"secondary";size:"sm";onClicked:fixture.invoke("review")}
            BleeckerButton {objectName:"activityActionArchive";text:"Archive";variant:"ghost";size:"sm";onClicked:fixture.invoke("archive")}
        }
    }
    Component {
        id:plain
        Item {
            id:plainRoot;objectName:"activityActionPlain"
            readonly property real logicalPixelSize:plainLabel.logicalPixelSize
            readonly property real offer:BleeckerLayout.proposedWidth
            BleeckerLayout.minimumWidth:0;BleeckerLayout.idealWidth:plainLabel.unwrappedWidth
            implicitWidth:offer<0 ? plainLabel.unwrappedWidth:Math.ceil(Math.min(plainLabel.implicitWidth,offer)*plainMetrics.devicePixelRatio)/plainMetrics.devicePixelRatio
            implicitHeight:Math.ceil(plainLabel.naturalHeight*plainMetrics.devicePixelRatio)/plainMetrics.devicePixelRatio
            PixelAlignment {id:plainMetrics;target:plainRoot}
            ButtonLabel {
                id:plainLabel;objectName:"activityActionPlainText";text:"Review";font:activity.presentationFont;color:activity.foreground
                wrapWidth:plainRoot.offer;width:plainRoot.width
                clip:true;Accessible.ignored:false;Accessible.role:Accessible.StaticText;Accessible.name:text
            }
        }
    }
    Component {
        id:rectangle
        Rectangle {
            objectName:fixture.actionMode==="zero" ? "activityActionZero":fixture.actionMode==="tall" ? "activityActionTall":"activityActionRect"
            implicitWidth:fixture.actionMode==="zero" ? 0:32
            implicitHeight:fixture.actionMode==="zero" ? 0:fixture.actionMode==="tall" ? 90:20
            color:fixture.actionMode==="zero" ? "transparent":BleeckerTheme.nativeBlue
        }
    }
    Component {
        id:counter
        BleeckerButton {
            objectName:"activityActionCounter";property int value:0
            text:"Count "+value;variant:"secondary";size:"sm"
            onClicked:{value++;fixture.localValue=value;fixture.invoke("counter")}
            Component.onCompleted:{fixture.appears++;fixture.localValue=value}
            Component.onDestruction:if(fixture){fixture.disappears++;fixture.localValue=-1}
        }
    }
    Component {id:alternateIcon;ActivityCaseGlyph {symbol:fixture.definition.symbol;pixelSize:parent.pixelSize;color:parent.foregroundColor}}
}
