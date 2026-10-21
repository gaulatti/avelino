pragma FunctionSignatureBehavior: Enforced
import QtQuick
import QtQuick.Window

InheritedControl {
    id:control
    property string title:"Choose file…"
    required property list<var> allowedContentTypes
    property url initialFolder:browser.defaultFolder()
    property real widthOffer:-1
    property real maximumWidth:-1
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
        if(!Number.isFinite(maximumWidth)||(maximumWidth<0&&maximumWidth!==-1))throw new Error("FileInput maximum width must be nonnegative or -1")
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
    onMaximumWidthChanged:if(componentReady)validate()
    FileChooserHost {owner:control;browser:control.browser}
    BleeckerButtonStyle {
        id:trigger;objectName:"bleeckerFileInputTrigger"
        width:control.width;height:control.height;variant:"secondary";size:"md"
        widthOffer:control.widthOffer
        maximumWidth:control.maximumWidth
        onClicked:control.open()
        BleeckerText {text:control.title;Accessible.ignored:true}
    }
    FileChooserDialog {
        id:sheet;objectName:"bleeckerFileInputChooser";browser:control.browser
        parent:control.Window.window ? control.Window.window.contentItem:null
        onClosed:control.restoreTriggerFocus()
    }
}
