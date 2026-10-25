import QtQuick
import QtQuick.Templates as T

FocusScope {
    id:field
    required property Item owner
    required property string endpoint
    required property real modelValue
    property real bufferValue:0
    // The native Hebrew separator entry selects the leftmost visible field.
    // Date-field direction is independent of the caller's layout mirroring.
    property int selectedSegment:owner.locale.textDirection===Qt.RightToLeft ? Math.max(0,editable.length-1):0
    property string typing:""
    property bool isTyping:false
    property int textRevision:0
    property bool restoring:false
    readonly property string title:endpoint==="start" ? "From":"To"
    readonly property var formatted:owner.componentReady ? DateRangeTools.formatted(bufferValue,owner.locale.name,owner.calendar,owner.timeZone):({text:"",segments:[]})
    readonly property var editorFormatted:owner.componentReady ? DateRangeTools.editorFormatted(bufferValue,owner.locale.name,owner.calendar,owner.timeZone):({text:"",segments:[]})
    readonly property string typedText:selected ? DateRangeTools.editorFieldText(selected.kind,typing):typing
    readonly property var editable:editorFormatted.segments.filter(item=>item.kind!=="literal")
    readonly property var selected:editable[Math.min(selectedSegment,Math.max(0,editable.length-1))]
    readonly property string currentText:isTyping &&selected ? editorFormatted.text.slice(0,selected.first)+typedText+editorFormatted.text.slice(selected.last):editorFormatted.text
    readonly property font editorFont:DateRangeTools.systemFont(owner.dateStyle.fontPixels)
    readonly property var reservedWidths:owner.componentReady ? DateRangeTools.fieldWidths(owner.locale.name,owner.calendar,owner.timeZone,owner.dateStyle.fontPixels):[]
    readonly property Item editor:editorLoader.item
    readonly property Item input:editor ? editor.textInput:null
    readonly property Item inlineCalendar:editor ? editor.inlineCalendarItem:null
    readonly property Item popupCalendar:editor ? editor.popupCalendarItem:null
    readonly property Item inputItem:editor ? editor.inputItem:null
    readonly property var panel:editor ? editor.calendarPanel:null
    readonly property var calendarPanel:panel
    readonly property real naturalTextWidth:reservedWidths.reduce((total,width)=>total+width,0)
    implicitWidth:owner.dateStyle.graphical ? 138.5:Math.ceil((naturalTextWidth+5)*2)/2+owner.dateStyle.stepperWidth
    implicitHeight:owner.dateStyle.graphical ? 148:owner.dateStyle.fieldHeight
    property real layoutX:0
    property real layoutY:0
    // Snap both ideal edges in scene coordinates. Adjacent half-point calendar
    // allocations can therefore occupy different whole-pixel widths at DPR 1.
    PixelAlignment {id:leadingEdge;target:field.parent;origin:Qt.point(field.layoutX,field.layoutY)}
    PixelAlignment {id:trailingEdge;target:field.parent;origin:Qt.point(field.layoutX+field.implicitWidth,field.layoutY+field.implicitHeight)}
    x:layoutX+leadingEdge.offset.x;y:layoutY+leadingEdge.offset.y
    width:implicitWidth+trailingEdge.offset.x-leadingEdge.offset.x
    height:implicitHeight+trailingEdge.offset.y-leadingEdge.offset.y
    Accessible.ignored:true
    function synchronize():void {
        if(!owner.componentReady||!editor)return
        bufferValue=DateRangeTools.clamped(modelValue,owner.range);typing="";isTyping=false
        inlineCalendar.resetView();popupCalendar.resetView();restoreSelection()
    }
    onModelValueChanged:synchronize()
    onBufferValueChanged:Qt.callLater(restoreSelection)
    onEnabledChanged:if(!enabled&&panel)panel.close()
    function restoreSelection():void {
        if(!input||!input.activeFocus||!selected)return
        input.select(selected.first,isTyping ? selected.first+typedText.length:selected.last)
    }
    function request(value:real):void {
        if(!enabled)return
        bufferValue=value;typing="";isTyping=false
        if(endpoint==="start")owner.startRequested(value);else owner.endRequested(value)
    }
    function activate(position:int):void {
        if(!enabled)return
        commitTyping()
        for(let i=0;i<editable.length;++i)if(position>=editable[i].first &&(position<editable[i].last ||i===editable.length-1&&position===editable[i].last)){selectedSegment=i;break}
        restoreSelection()
        if(owner.dateStyle.overlay&&!panel.visible)Qt.callLater(openCalendar)
    }
    function openCalendar():void {
        if(!enabled||!owner.dateStyle.overlay||panel.visible)return
        popupCalendar.resetView();panel.open();input.forceActiveFocus(Qt.MouseFocusReason)
        restoreSelection();request(bufferValue)
    }
    function cancelEditing():void {
        typing="";isTyping=false;textRevision++;bufferValue=DateRangeTools.clamped(modelValue,owner.range)
        inlineCalendar.resetView();popupCalendar.resetView();panel.close();restoreSelection()
    }
    function commitTyping():bool {
        if(!isTyping||!selected){textRevision++;return true}
        const parsed=DateRangeTools.parsedField(bufferValue,selected.kind,typing,owner.locale.name,owner.calendar,owner.timeZone)
        typing="";isTyping=false
        if(!parsed.valid){restoreSelection();return false}
        request(DateRangeTools.replaced(bufferValue,selected.kind,parsed.number,owner.locale.name,owner.calendar,owner.timeZone,owner.range));return true
    }
    function appendTyping(text:string):void {
        if(!isTyping){isTyping=true;typing=text}else typing+=text
        if(!selected)return
        const parsed=DateRangeTools.parsedField(bufferValue,selected.kind,typing,owner.locale.name,owner.calendar,owner.timeZone)
        if(parsed.valid&&parsed.complete)commitTyping();else restoreSelection()
    }
    function step(amount:int):void {
        if(!enabled||!selected)return
        commitTyping()
        const value=DateRangeTools.stepped(bufferValue,selected.kind,amount,owner.locale.name,owner.calendar,owner.timeZone,owner.range)
        popupCalendar.viewValue=value;request(value)
    }
    function moveSegment(amount:int):void {commitTyping();selectedSegment=Math.max(0,Math.min(editable.length-1,selectedSegment+amount));restoreSelection()}
    Loader {
        id:editorLoader
        width:field.width;height:field.height
        // The reference branches on optional range presence; changes between two
        // supplied ranges keep the existing editor instance.
        sourceComponent:owner.range===null ||owner.range===undefined ? unrestrictedEditor:restrictedEditor
        onLoaded:field.synchronize()
    }
    Component {id:unrestrictedEditor;DateRangeEditor {field:editorLoader.parent}}
    Component {id:restrictedEditor;DateRangeEditor {field:editorLoader.parent}}
}
