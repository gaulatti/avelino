pragma FunctionSignatureBehavior: Enforced
import QtQuick
import QtQuick.Window

InheritedControl {
    id:control
    property string title:"Choose file…"
    required property list<var> allowedContentTypes
    property url initialFolder:browser.defaultFolder()
    property real widthOffer:-1
    property real heightOffer:-1
    property real maximumWidth:-1
    property real maximumHeight:-1
    readonly property real effectiveHeightOffer:heightOffer>=0 ? heightOffer:maximumHeight
    readonly property QtObject chooser:sheet
    readonly property FileChooserBrowser browser:FileChooserBrowser {
        allowedContentTypes:control.allowedContentTypes
        onResult:value=>control.result(value)
    }
    readonly property Item presentationItem:trigger.partCount>0 ? trigger.partAt(0).presentationItem:null
    readonly property Item inputItem:trigger.partCount>0 ? trigger.partAt(0).inputItem:null
    signal result(var value)
    property bool componentReady:false
    implicitWidth:trigger.implicitWidth;implicitHeight:trigger.implicitHeight
    BleeckerLayout.minimumWidth:36;BleeckerLayout.idealWidth:trigger.implicitWidth
    padding:0;background:null;contentItem:null;focusPolicy:Qt.NoFocus
    Accessible.ignored:true
    function validate():void {
        if(!Number.isFinite(widthOffer)||(widthOffer<0&&widthOffer!==-1))throw new Error("FileInput width offer must be nonnegative or -1")
        if(!Number.isFinite(heightOffer)||(heightOffer<0&&heightOffer!==-1))throw new Error("FileInput height offer must be nonnegative or -1")
        if(!Number.isFinite(maximumWidth)||(maximumWidth<0&&maximumWidth!==-1))throw new Error("FileInput maximum width must be nonnegative or -1")
        if(!Number.isFinite(maximumHeight)||(maximumHeight<0&&maximumHeight!==-1))throw new Error("FileInput maximum height must be nonnegative or -1")
    }
    function open():void {
        if(!enabled)return
        if(!Window.window)throw new Error("FileInput requires a window")
        browser.open(initialFolder)
    }
    function close():void {browser.cancel()}
    function restoreTriggerFocus():void {
        if(browser.active||!enabled||!visible||!inputItem)return
        inputItem.forceActiveFocus(Qt.PopupFocusReason)
        if(Window.window)Window.window.requestActivate()
    }
    Component.onCompleted:{componentReady=true;validate()}
    onAllowedContentTypesChanged:if(componentReady)validate()
    onWidthOfferChanged:if(componentReady)validate()
    onHeightOfferChanged:if(componentReady)validate()
    onMaximumWidthChanged:if(componentReady)validate()
    onMaximumHeightChanged:if(componentReady)validate()
    FileChooserHost {owner:control;browser:control.browser}
    BleeckerButtonStyle {
        id:trigger;objectName:"bleeckerFileInputTrigger"
        width:control.width;height:control.height;variant:"secondary";size:"md"
        widthOffer:control.widthOffer
        maximumWidth:control.maximumWidth
        onClicked:control.open()
        BleeckerText {
            id:label;text:control.title;clip:true;Accessible.ignored:true
            // FileInput's title is plain text. Keep its proposal on that
            // renderer without adding a formatted-text height API.
            Binding {
                target:label.textRenderer;property:"wrapHeight"
                value:control.effectiveHeightOffer<0 ? -1:Math.max(trigger.minimumHeight,control.effectiveHeightOffer)
            }
        }
    }
    FileChooserDialog {
        id:sheet;objectName:"bleeckerFileInputChooser";browser:control.browser
        parent:control.Window.window ? control.Window.window.contentItem:null
        onClosed:control.restoreTriggerFocus()
    }
}
