import QtQuick
import QtQuick.Templates as T

T.Control {
    id:control
    anchors.alignWhenCentered:false
    required property string code
    property real length:6
    signal codeRequested(string requestedCode)
    readonly property Item editor:input
    readonly property Item presentationItem:input
    readonly property string displayText:input.displayText
    readonly property bool editing:input.activeFocus
    readonly property string placeholder:{BleeckerOTPTools.validate(code,length);return "•".repeat(length)}
    property bool _ready:false
    property bool _publishing:false
    property bool _pendingEdit:false
    property bool _lastWriteChangedModel:true
    property bool _writeNotified:false
    property string _requestedCode:""
    property string _modelBeforeRequest:""

    implicitWidth:240
    implicitHeight:input.implicitHeight
    padding:0;background:null
    // The native editor supplies the composite's one keyboard stop. A second
    // stop on this wrapper would redirect Backtab straight back to the editor.
    focusPolicy:Qt.NoFocus
    BleeckerLayout.minimumWidth:28
    BleeckerLayout.idealWidth:240
    Accessible.ignored:true

    function refreshGetter() {
        if(!_ready)return
        BleeckerOTPTools.validate(code,length)
        input.text=code
    }
    function requestText(text:string) {
        if(!_ready || !enabled)return
        _modelBeforeRequest=code
        _requestedCode=BleeckerOTPTools.filter(text,length)
        _writeNotified=false
        _publishing=true
        codeRequested(_requestedCode)
        _publishing=false
        _lastWriteChangedModel=_writeNotified || code!==_modelBeforeRequest
    }
    function notifyCodeWrite() {
        // Observable owners can publish an accepted write even when its string
        // value is unchanged. A projected value binding does not publish it.
        _writeNotified=true
        _lastWriteChangedModel=true
    }
    function ownerChanged() {
        BleeckerOTPTools.validate(code,length)
        if(!_ready || _publishing)return
        // An asynchronous owner acknowledgement keeps the raw editor intact.
        if(input.activeFocus && code===_requestedCode && code!==_modelBeforeRequest) {
            _lastWriteChangedModel=true
            return
        }
        // Native rejected/unchanged writes can leave a stale field editor until
        // configuration or commit refreshes it. Do not eagerly bind text:code.
        if(input.activeFocus && !_lastWriteChangedModel)return
        refreshGetter()
    }
    function commitGetter() {
        if(!_ready || !enabled)return
        requestText(code)
        refreshGetter()
    }
    onCodeChanged:ownerChanged()
    onLengthChanged:refreshGetter()
    onActiveFocusChanged:if(activeFocus && !input.activeFocus)input.forceActiveFocus(focusReason)
    Component.onCompleted:{_ready=true;refreshGetter()}
    Component.onDestruction:_ready=false

    BleeckerTextField {
        id:input;objectName:"bleeckerOTPEditor"
        anchors.centerIn:control;anchors.alignWhenCentered:false
        width:Math.max(28,control.width);height:implicitHeight
        font:Qt.font({family:BleeckerFonts.monospace,pointSize:BleeckerFonts.pointSizeForPixels(20),weight:Font.DemiBold})
        horizontalAlignment:TextInput.AlignHCenter
        placeholderText:control.placeholder
        placeholderElide:Text.ElideNone
        maximumLength:2147483647
        inputMethodHints:Qt.ImhNone
        clip:true
        Accessible.name:"Verification code"
        onActiveFocusChanged: {
            if(!control._ready)return
            if(activeFocus) {
                control.requestText(control.code)
                control.refreshGetter()
            } else {
                control._pendingEdit=false
                control.refreshGetter()
            }
        }
        onTextEdited: {
            if(inputMethodComposing)control._pendingEdit=true
            else {control._pendingEdit=false;control.requestText(text)}
        }
        onInputMethodComposingChanged: {
            if(!inputMethodComposing && control._pendingEdit) {
                control._pendingEdit=false
                control.requestText(text)
            }
        }
        onEditingFinished:control.commitGetter()
    }
}
