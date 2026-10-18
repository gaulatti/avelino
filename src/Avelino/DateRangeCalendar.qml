import QtQuick
import QtQuick.Templates as T

T.Control {
    id:calendar
    required property Item field
    property real viewValue:field.bufferValue
    readonly property var owner:field.owner
    readonly property var grid:DateRangeTools.month(viewValue,owner.locale.name,owner.calendar,owner.timeZone,owner.range)
    readonly property font dayFont:DateRangeTools.systemFont(11)
    readonly property font titleFont:Qt.font({family:dayFont.family,pixelSize:12,weight:Font.Bold})
    implicitWidth:138.5;implicitHeight:148
    width:implicitWidth;height:implicitHeight
    padding:0;contentItem:null;background:null;focusPolicy:Qt.StrongFocus
    Accessible.ignored:true
    function resetView():void {viewValue=field.bufferValue}
    function navigate(amount:int):void {if(enabled)viewValue=DateRangeTools.stepped(viewValue,"month",amount,owner.locale.name,owner.calendar,owner.timeZone,null)}
    function preview(amount:int):void {
        if(!enabled)return
        field.bufferValue=DateRangeTools.previewedDay(field.bufferValue,amount,owner.locale.name,owner.calendar,owner.timeZone,owner.range)
        viewValue=field.bufferValue
    }
    function candidate(index:int):real {return DateRangeTools.selectingDay(field.bufferValue,grid.days[index].instant,owner.locale.name,owner.calendar,owner.timeZone,owner.range)}
    function pressDate(value:real):void {
        const changed=field.bufferValue!==value
        field.bufferValue=value;viewValue=value
        if(owner.dateStyle.graphical&&changed)field.request(value)
    }
    Keys.onPressed:event=>{
        if(event.key===Qt.Key_Left){preview(owner.mirrored ? 1:-1);event.accepted=true}
        else if(event.key===Qt.Key_Right){preview(owner.mirrored ? -1:1);event.accepted=true}
        else if(event.key===Qt.Key_Up){preview(-7);event.accepted=true}
        else if(event.key===Qt.Key_Down){preview(7);event.accepted=true}
        else if(event.key===Qt.Key_Space||event.key===Qt.Key_Return||event.key===Qt.Key_Enter){event.accepted=true;field.request(field.bufferValue)}
        else if(event.key===Qt.Key_Escape){event.accepted=true;field.cancelEditing()}
    }
    Text {
        x:2;y:1;width:parent.width-43;height:18;text:calendar.grid.title
        font:calendar.titleFont;color:BleeckerTheme.nativeEditorText;elide:Text.ElideRight
        renderType:Text.NativeRendering;Accessible.ignored:true
    }
    Row {
        x:parent.width-width-1;y:0;spacing:1
        Repeater {
            model:[{name:"Previous Month",amount:-1},{name:"Current Month",amount:0},{name:"Next Month",amount:1}]
            T.Button {
                required property var modelData
                width:13;height:18;padding:0;focusPolicy:Qt.NoFocus
                Accessible.name:modelData.name
                onClicked:if(modelData.amount)calendar.navigate(modelData.amount);else calendar.viewValue=DateRangeTools.fromUnixSeconds(Date.now()/1000)
                background:null
                contentItem:Canvas {
                    property color ink:BleeckerTheme.nativeEditorPlaceholder
                    onInkChanged:requestPaint()
                    onPaint:{const p=getContext("2d");p.reset();p.fillStyle=ink;p.beginPath()
                        if(modelData.amount===0)p.arc(6.5,9,3,0,Math.PI*2)
                        else if(modelData.amount<0){p.moveTo(8.5,5.5);p.lineTo(3.5,9);p.lineTo(8.5,12.5);p.closePath()}
                        else{p.moveTo(4.5,5.5);p.lineTo(9.5,9);p.lineTo(4.5,12.5);p.closePath()}
                        p.fill()}
                    Accessible.ignored:true
                }
            }
        }
    }
    Rectangle {x:2;y:35;width:parent.width-4;height:0.5;color:BleeckerTheme.nativeSeparator;Accessible.ignored:true}
    Repeater {
        model:7
        Text {
            required property int index
            x:2+(calendar.owner.mirrored ? 6-index:index)*(calendar.width-4)/7;y:20
            width:(calendar.width-4)/7;height:15;text:calendar.grid.weekdays[index]
            font:Qt.font({family:calendar.dayFont.family,pixelSize:10,weight:Font.Bold})
            horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter;color:BleeckerTheme.nativeEditorPlaceholder
            renderType:Text.NativeRendering;Accessible.ignored:true
        }
    }
    Repeater {
        model:42
        T.Button {
            id:dayButton
            required property int index
            readonly property var day:calendar.grid.days[index]
            readonly property bool selected:calendar.field.bufferValue>=day.instant && calendar.field.bufferValue<day.end
            property real pressedDate:0
            objectName:"bleeckerDateDay-"+index
            x:2+(calendar.owner.mirrored ? 6-index%7:index%7)*(calendar.width-4)/7
            y:36+Math.floor(index/7)*18;width:(calendar.width-4)/7;height:18
            enabled:day.enabled;padding:0;focusPolicy:Qt.NoFocus
            onPressed:{pressedDate=calendar.candidate(index);calendar.forceActiveFocus(Qt.MouseFocusReason);calendar.pressDate(pressedDate)}
            onClicked:calendar.field.request(pressedDate)
            Accessible.ignored:true
            background:Rectangle {radius:3;color:dayButton.selected ? (calendar.activeFocus ? "#b5d7ff":"#dedede"):"transparent"}
            contentItem:Text {
                text:dayButton.day.text;font:calendar.dayFont
                color:!dayButton.enabled ? BleeckerTheme.nativeEditorDisabledText:dayButton.day.inMonth ? BleeckerTheme.nativeEditorText:BleeckerTheme.nativeEditorPlaceholder
                horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter
                renderType:Text.NativeRendering;Accessible.ignored:true
            }
        }
    }
}
