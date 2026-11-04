import QtQuick
import Avelino

Item {
    id:fixture
    width:640;height:400
    property var definition:({id:"default",start:1710000000.625,end:1710864000.125,locale:"en_US",calendar:"gregorian",timeZone:"UTC",controlSize:"regular",pickerStyle:"inherit",owner:"echo",rtl:false,disabled:false,parentFont:false,parentRed:false})
    property real modelStart:1710000000.625
    property real modelEnd:1710864000.125
    property var requests:[]
    property var pending:({})
    property int appearances:0
    property int disappearances:0
    property int instances:0
    property bool mounted:true
    readonly property Item picker:loader.item
    function configure(value):void {
        definition=Object.assign({},value)
        modelStart=DateRangeTools.fromUnixSeconds(definition.start);modelEnd=DateRangeTools.fromUnixSeconds(definition.end)
        requests=[];pending={}
    }
    function resetCounters():void {appearances=0;disappearances=0;instances=0}
    function updateConfiguration(value):void {
        replaceConfiguration(Object.assign({},definition,value))
    }
    function replaceConfiguration(value):void {
        const style=definition.pickerStyle
        definition=Object.assign({},value)
        if(style!==definition.pickerStyle){mounted=false;mounted=true}
        else Qt.callLater(function(){if(fixture.picker)fixture.picker.synchronize()})
    }
    function externalStart(value:real):void {modelStart=DateRangeTools.fromUnixSeconds(value)}
    function externalEnd(value:real):void {modelEnd=DateRangeTools.fromUnixSeconds(value)}
    function applyPending():void {
        const value=pending;pending={}
        if(value.start!==undefined)modelStart=value.start
        if(value.end!==undefined)modelEnd=value.end
    }
    function receive(endpoint:string,value:real):void {
        requests=requests.concat([{endpoint:endpoint,requested:value,previousStart:modelStart,previousEnd:modelEnd}])
        if(definition.owner==="echo"){if(endpoint==="start")modelStart=value;else modelEnd=value}
        else if(definition.owner==="delay")pending=Object.assign({},pending,{[endpoint]:value})
        else if(definition.owner!=="ignore")throw new Error("Unknown date binding owner")
    }
    function box(item):var {
        const p=item.mapToItem(fixture,0,0)
        return {x:p.x,y:p.y,width:item.width,height:item.height}
    }
    function literalInputState(endpoint:string):var {
        const field=picker[endpoint+"Field"],input=field.input
        return {selectedSegment:field.selectedSegment,selectionStart:input.selectionStart,selectionEnd:input.selectionEnd,
            text:input.text,activeFocus:input.activeFocus,calendarVisible:field.panel.visible}
    }
    function prepareLiteralInput(value):var {
        const field=picker[value.endpoint+"Field"],input=field.input
        const selected=field.editable.findIndex(piece=>piece.kind===value.selectedKind)
        if(selected<0)throw new Error("Native selected field missing")
        field.selectedSegment=selected;input.forceActiveFocus(Qt.OtherFocusReason);field.restoreSelection()
        const literals=[];for(let i=0;i<input.fields.length;++i)if(input.fields[i].kind==="literal")literals.push(i)
        const index=literals[value.literalOrdinal]
        if(index===undefined||input.reservedWidths[index]<=0)throw new Error("Native literal reservation missing")
        let advance=0;for(let i=0;i<index;++i)advance+=input.reservedWidths[i]
        const reserved=input.reservedWidths[index]
        const left=input.horizontalAlignment===TextInput.AlignRight ? input.width-input.rightPadding-advance-reserved:input.leftPadding+advance
        const x=left+reserved/2,y=input.height/2
        return {x:x,y:y,literal:input.fields[index].text,position:input.positionAt(x,y,TextInput.CursorOnCharacter)}
    }
    function snapshot():var {
        if(!picker)return {ready:false}
        const arrow=picker.presentationItem.children.find(item=>item.objectName==="bleeckerDateArrow")
        return {ready:true,model:{start:modelStart,end:modelEnd,requests:requests,pending:pending,appearances:appearances,disappearances:disappearances,wrapperInstances:instances},
            frames:{caller:box(picker),picker:box(picker.presentationItem),start:box(picker.startField),end:box(picker.endField),arrow:box(arrow)},
            displayed:[picker.startField.bufferValue,picker.endField.bufferValue],
            editorText:[picker.startField.input.text,picker.endField.input.text],
            editorRoles:[picker.startField.editable.map(segment=>segment.kind),picker.endField.editable.map(segment=>segment.kind)],
            editorVisible:!picker.dateStyle.graphical,
            calendarParts:[DateRangeTools.parts(picker.startField.bufferValue,picker.locale.name,picker.calendar,picker.timeZone),DateRangeTools.parts(picker.endField.bufferValue,picker.locale.name,picker.calendar,picker.timeZone)],
            startText:picker.startField.formatted.text,endText:picker.endField.formatted.text,
            enabled:picker.enabled,mirrored:picker.mirrored,controlSize:picker.controlSize,
            style:picker.pickerStyle,locale:picker.locale.name,calendar:picker.calendar,timeZone:picker.timeZone}
    }
    Component.onCompleted:configure(definition)
    Rectangle {anchors.fill:parent;color:BleeckerTheme.palette.background;Accessible.ignored:true}
    Item {
        id:caller;anchors.centerIn:parent;anchors.alignWhenCentered:false
        width:fixture.definition.width!==undefined ? fixture.definition.width:(fixture.picker ? fixture.picker.implicitWidth:0)
        height:fixture.definition.height!==undefined ? fixture.definition.height:(fixture.picker ? fixture.picker.implicitHeight:0)
        Loader {
            id:loader;anchors.fill:parent;active:fixture.mounted
            sourceComponent:Component {
                BleeckerDateRangePicker {
                    start:fixture.modelStart;end:fixture.modelEnd
                    range:fixture.definition.lower===undefined ? null:({lower:fixture.definition.lower,upper:fixture.definition.upper})
                    locale:Qt.locale(fixture.definition.locale);calendar:fixture.definition.calendar;timeZone:fixture.definition.timeZone
                    controlSize:fixture.definition.controlSize;pickerStyle:fixture.definition.pickerStyle
                    enabled:!fixture.definition.disabled
                    font.family:fixture.definition.parentFont ? DateRangeTools.systemFont(28).family:BleeckerFonts.primary
                    font.pointSize:BleeckerFonts.pointSizeForPixels(fixture.definition.parentFont ? 28:13)
                    font.weight:fixture.definition.parentFont ? Font.Bold:Font.Normal
                    palette.windowText:fixture.definition.parentRed ? BleeckerTheme.nativeRed:BleeckerTheme.nativeTextPrimary
                    LayoutMirroring.enabled:fixture.definition.rtl
                    onStartRequested:requestedValue=>fixture.receive("start",requestedValue)
                    onEndRequested:requestedValue=>fixture.receive("end",requestedValue)
                    Component.onCompleted:{fixture.appearances++;fixture.instances++}
                    Component.onDestruction:fixture.disappearances++
                }
            }
        }
    }
}
