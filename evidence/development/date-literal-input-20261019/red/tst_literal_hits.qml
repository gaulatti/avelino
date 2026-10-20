import QtQuick
import QtTest
import Avelino
import "date_literal_cases.js" as NativeLiteral
Item {
    id:root;width:900;height:600
    Component {
        id:factory
        BleeckerDateRangePicker {
            property bool callerRtl:false
            property int requests:0
            LayoutMirroring.enabled:callerRtl
            start:1710000000.625;end:1710864000.125;timeZone:"UTC"
            onStartRequested:value=>{++requests;start=value}
            onEndRequested:value=>{++requests;end=value}
        }
    }
    TestCase {
        name:"DateLiteralHitContract";when:windowShown
        function init(){BleeckerTheme.dark=false;BleeckerTheme.textScale=1;failOnWarning(/Binding loop/)}
        function test_literal_does_not_activate_calendar_data(){
            const profiles=NativeLiteral.profiles
            let rows=[]
            for(const profile of profiles)for(const callerRtl of [false,true])for(const endpoint of ["start","end"])
                rows.push({tag:profile.nativeCase+"-caller"+callerRtl+"-"+endpoint,profile:profile,callerRtl:callerRtl,endpoint:endpoint})
            return rows
        }
        function test_literal_does_not_activate_calendar(data){
            const p=data.profile,item=createTemporaryObject(factory,root,{locale:Qt.locale(p.locale),calendar:p.calendar,callerRtl:data.callerRtl})
            verify(item);wait(30)
            const field=item[data.endpoint+"Field"],input=field.input
            verify(input);const selected=field.editable.findIndex(piece=>piece.kind===p.selectedKind);verify(selected>=0)
            field.selectedSegment=selected;input.forceActiveFocus(Qt.OtherFocusReason);tryCompare(input,"activeFocus",true);field.restoreSelection()
            const beforeText=input.text,beforeFirst=input.selectionStart,beforeLast=input.selectionEnd
            const literalIndices=[];for(let i=0;i<input.fields.length;++i)if(input.fields[i].kind==="literal")literalIndices.push(i)
            const index=literalIndices[p.literalOrdinal];verify(index!==undefined)
            let advance=0;for(let i=0;i<index;++i)advance+=input.reservedWidths[i]
            const reserved=input.reservedWidths[index];verify(reserved>0)
            const left=input.horizontalAlignment===TextInput.AlignRight ? input.width-input.rightPadding-advance-reserved:input.leftPadding+advance
            const position=input.positionAt(left+reserved/2,input.height/2,TextInput.CursorOnCharacter)
            console.info("LITERAL_HIT",data.tag,JSON.stringify({literal:input.fields[index].text,position:position,selectedKind:p.selectedKind}))
            mouseClick(input,left+reserved/2,input.height/2);wait(30)
            compare(field.panel.visible,false,"Literal click must not open the calendar")
            compare(item.requests,0,"Literal click must not send an owner request")
            compare(field.selectedSegment,selected);compare(input.selectionStart,beforeFirst);compare(input.selectionEnd,beforeLast)
            compare(input.text,beforeText);verify(input.activeFocus)
            keyClick(Qt.Key_Up);wait(20);compare(item.requests,1)
            if(data.endpoint==="start"){
                compare(item.start,p.nativeStartAfterUp,"Up keeps the native selected field after a literal click")
                compare(item.end,1710864000.125)
            }else compare(item.start,1710000000.625)
        }
    }
}
