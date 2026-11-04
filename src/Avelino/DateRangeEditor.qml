import QtQuick
import QtQuick.Templates as T

Item {
    id:editor
    required property Item field
    readonly property Item owner:field.owner
    readonly property bool dateMirrored:owner.locale.textDirection===Qt.RightToLeft
    readonly property Item textInput:input
    readonly property Item inlineCalendarItem:inlineCalendar
    readonly property Item popupCalendarItem:popupCalendar
    readonly property var calendarPanel:panel
    readonly property Item inputItem:owner.dateStyle.graphical ? inlineCalendar:input
    property bool retiring:false
    width:field.width;height:field.height
    Component.onDestruction:retiring=true
    DateRangeCalendar {id:inlineCalendar;field:editor.field;width:editor.field.width;visible:owner.dateStyle.graphical}
    Item {
        id:editorContainer;objectName:"bleeckerDateEditorContainer"
        visible:!owner.dateStyle.graphical;width:field.width;height:field.height
        LayoutMirroring.enabled:false;LayoutMirroring.childrenInherit:true
        DateRangeInput {
            id:input;objectName:"bleeckerDateEditor"
            x:editor.dateMirrored ? owner.dateStyle.stepperWidth:0
            width:editorContainer.width-owner.dateStyle.stepperWidth;height:editorContainer.height
            padding:0;leftPadding:editor.dateMirrored ? 2:3;rightPadding:editor.dateMirrored ? 3:2;topPadding:0;bottomPadding:0
            font:field.editorFont;text:{field.textRevision;return field.currentText}
            fields:field.editorFormatted.segments;reservedWidths:field.reservedWidths;activeSegment:field.selectedSegment
            color:field.enabled ? BleeckerTheme.nativeEditorText:BleeckerTheme.nativeEditorDisabledText
            horizontalAlignment:editor.dateMirrored ? TextInput.AlignRight:TextInput.AlignLeft
            selectionColor:"#1769db";selectedTextColor:"white";verticalAlignment:TextInput.AlignVCenter
            focusPolicy:Qt.StrongFocus;selectByMouse:false;Accessible.name:field.title
            background:Rectangle {
                radius:4;color:BleeckerTheme.dark ? "#222222":"#ffffff"
                border.width:panel.visible ? 0:1;border.color:BleeckerTheme.nativeSeparator
                Rectangle {anchors.fill:parent;anchors.margins:-2;radius:5;color:"transparent";border.width:input.visualFocus&&!panel.visible ? 2:0;border.color:"#7eb4f1"}
            }
            onFieldActivated:position=>field.activate(position)
            onFieldSelectionRequested:field.restoreSelection()
            onActiveFocusChanged:if(activeFocus)field.restoreSelection()
            onEditingFinished:if(!editor.retiring&&!field.restoring)field.commitTyping()
            onTextEdited:{
                if(preeditText.length)return
                const parsed=DateRangeTools.parsedDate(field.bufferValue,text,owner.locale.name,owner.calendar,owner.timeZone,owner.range)
                if(parsed.valid)field.request(parsed.instant)
            }
            Keys.priority:Keys.BeforeItem
            Keys.onPressed:event=>{
                if(event.key===Qt.Key_Up){field.step(1);event.accepted=true}
                else if(event.key===Qt.Key_Down){field.step(-1);event.accepted=true}
                else if(event.key===Qt.Key_Left){field.moveSegment(-1);event.accepted=true}
                else if(event.key===Qt.Key_Right){field.moveSegment(1);event.accepted=true}
                else if(event.key===Qt.Key_Escape){field.cancelEditing();event.accepted=true}
                else if(event.key===Qt.Key_Return||event.key===Qt.Key_Enter){field.commitTyping();panel.close();event.accepted=true}
                else if(event.key===Qt.Key_Backspace){if(!field.isTyping){field.isTyping=true;field.typing=""}else field.typing=field.typing.slice(0,-1);event.accepted=true}
                else if(event.key===Qt.Key_Tab){
                    field.commitTyping()
                    if(panel.visible){panel.close();field.selectedSegment=0;field.restoreSelection();event.accepted=true}
                    else if(field.selectedSegment<field.editable.length-1){field.moveSegment(1);event.accepted=true}
                }
                else if(event.key===Qt.Key_Backtab){field.commitTyping();if(field.selectedSegment>0){field.moveSegment(-1);event.accepted=true}}
                else if(event.text.length &&!(event.modifiers&(Qt.ControlModifier|Qt.MetaModifier|Qt.AltModifier))){field.appendTyping(event.text);event.accepted=true}
            }
        }
        Column {
            objectName:"bleeckerDateStepper"
            x:editor.dateMirrored ? 0:input.width+2;y:0;width:Math.max(0,owner.dateStyle.stepperWidth-2);height:parent.height
            visible:owner.dateStyle.stepperWidth>0
            Repeater {
                model:2
                T.Button {
                    required property int index
                    objectName:index===0 ? "bleeckerDateIncrement":"bleeckerDateDecrement"
                    width:parent.width;height:editorContainer.height/2;padding:0;focusPolicy:Qt.NoFocus;autoRepeat:true
                    Accessible.name:(index===0 ? "Increase ":"Decrease ")+field.title
                    onClicked:field.step(index===0 ? 1:-1)
                    background:Rectangle {color:BleeckerTheme.dark ? "#383838":"#ededed";radius:3}
                    contentItem:Canvas {
                        readonly property color ink:field.enabled ? BleeckerTheme.nativeEditorPlaceholder:BleeckerTheme.nativeEditorDisabledText
                        onInkChanged:requestPaint()
                        onPaint:{const p=getContext("2d"),cx=width/2,cy=height/2;p.reset();p.strokeStyle=ink;p.lineWidth=1.25;p.lineCap="round";p.lineJoin="round";p.beginPath();p.moveTo(cx-3,cy+(index===0 ? 1.5:-1.5));p.lineTo(cx,cy+(index===0 ? -1.5:1.5));p.lineTo(cx+3,cy+(index===0 ? 1.5:-1.5));p.stroke()}
                        Accessible.ignored:true
                    }
                }
            }
        }
    }
    T.Popup {
        id:panel;objectName:"bleeckerDateCalendarPanel"
        parent:field;popupType:T.Popup.Window;x:0;y:-4
        width:Math.max(field.width,138.5);height:172
        padding:0;modal:false;dim:false;focus:true
        closePolicy:T.Popup.CloseOnEscape|T.Popup.CloseOnPressOutside
        background:Rectangle {color:BleeckerTheme.dark ? "#242424":"white";radius:5;border.width:0.5;border.color:BleeckerTheme.nativeSeparator}
        contentItem:Item {DateRangeCalendar {id:popupCalendar;field:editor.field;x:0;y:24}}
        onOpened:{input.forceActiveFocus(Qt.OtherFocusReason);field.restoreSelection()}
        onClosed:{field.restoring=true;field.typing="";field.isTyping=false;field.restoring=false}
    }
    states:State {when:panel.visible;ParentChange {target:editorContainer;parent:panel.contentItem;x:0;y:4}}
}
