import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

Item {
    id: root
    width: 680; height: 320
    property string value: ""
    property int changes: 0
    Component { id: factory; BleeckerSecureField { width: 300; placeholderText: "Passphrase" } }
    Component {
        id: boundFactory
        BleeckerSecureField {
            width: 300; placeholderText: "Passphrase"
            text: root.value
            onTextEdited: { root.value = text; root.changes++ }
        }
    }
    Component {
        id: inheritedFactory
        T.Control {
            font.bold: true
            contentItem: BleeckerSecureField { objectName: "inheritedSecureField" }
        }
    }
    TestCase {
        name: "SecureFieldContracts"
        when: windowShown
        function init() {
            BleeckerTheme.dark=false; BleeckerTheme.textScale=1
            root.value=""; root.changes=0; failOnWarning(/Binding loop/)
        }
        function cleanup() { BleeckerTheme.dark=false; BleeckerTheme.textScale=1 }
        function typeValue(text) {
            for (const character of text) keyClick(character.toUpperCase().charCodeAt(0))
        }
        function test_source_geometry_and_reveal_data() {
            const rows=[]
            for (const dark of [false,true]) for (const scale of [1,1.5])
                for (const value of ["","Sample entry","A longer fictional entry for the native fixture"])
                    rows.push({tag:dark+"-"+scale+"-"+value,dark,scale,value})
            return rows
        }
        function test_source_geometry_and_reveal(data) {
            BleeckerTheme.dark=data.dark; BleeckerTheme.textScale=data.scale
            const field=createTemporaryObject(factory,root,{text:data.value})
            const action=findChild(field,"bleeckerSecureReveal")
            const placeholder=findChild(field,"bleeckerSecurePlaceholder")
            compare(field.height,40); compare(field.leftPadding,14); compare(field.rightPadding,44)
            compare(field.font.weight,Font.Normal)
            fuzzyCompare(field.font.pointSize,BleeckerFonts.pointSizeForPixels(14),0.000001)
            compare(field.echoMode,TextInput.Password); compare(field.revealed,false)
            compare(field.passwordMaskDelay,0); compare(field.passwordCharacter,"\u2022")
            compare(placeholder.visible,data.value==="")
            compare(action.Accessible.name,"Show contents")
            compare(action.Accessible.role,Accessible.Button)
            mouseClick(action)
            compare(field.revealed,true); compare(field.echoMode,TextInput.Normal)
            compare(field.text,data.value); compare(field.displayText,data.value)
            compare(action.Accessible.name,"Hide contents")
            action.forceActiveFocus(Qt.TabFocusReason); keyClick(Qt.Key_Space)
            compare(field.revealed,false); compare(field.text,data.value)
            if (data.value!=="") verify(field.displayText!==data.value)
        }
        function test_bound_editing_disabled_and_external_value() {
            const field=createTemporaryObject(boundFactory,root)
            const action=findChild(field,"bleeckerSecureReveal")
            mouseClick(field,20,20); typeValue("sample")
            compare(root.value,"sample"); compare(root.changes,6)
            verify(field.displayText!==field.text)
            root.value="External entry"; compare(field.text,root.value)
            mouseClick(action); compare(field.displayText,root.value)
            field.forceActiveFocus(); keyClick(Qt.Key_A,Qt.ControlModifier); typeValue("updated")
            compare(root.value,"updated")
            field.enabled=false; const before=root.changes
            mouseClick(action); typeValue("x")
            compare(field.revealed,true); compare(root.value,"updated"); compare(root.changes,before)
            field.enabled=true; mouseClick(action)
            compare(field.revealed,false); compare(field.text,"updated")
        }
        function test_focus_order_and_narrow_scrolling() {
            const field=createTemporaryObject(factory,root,{width:160,text:"A longer fictional entry for the native fixture"})
            const action=findChild(field,"bleeckerSecureReveal")
            const disabled=createTemporaryObject(factory,root,{x:200,enabled:false})
            const next=createTemporaryObject(factory,root,{x:400,width:180})
            field.forceActiveFocus(Qt.TabFocusReason); keyClick(Qt.Key_Tab)
            verify(action.activeFocus); verify(action.visualFocus)
            keyClick(Qt.Key_Space); compare(field.revealed,true)
            keyClick(Qt.Key_Tab); verify(next.activeFocus); verify(!disabled.activeFocus)
            keyClick(Qt.Key_Backtab); verify(action.activeFocus)
            keyClick(Qt.Key_Backtab); verify(field.activeFocus)
            verify(field.contentWidth>field.width-field.leftPadding-field.rightPadding)
            keyClick(Qt.Key_End); compare(field.cursorPosition,field.length)
            verify(field.cursorRectangle.x+field.cursorRectangle.width<=field.width-field.rightPadding+1)
        }
        function test_source_font_overrides_inherited_bold() {
            const host=createTemporaryObject(inheritedFactory,root)
            compare(findChild(host,"inheritedSecureField").font.weight,Font.Normal)
        }
        function test_read_only_keeps_value_while_revealing() {
            const field=createTemporaryObject(factory,root,{text:"Sample entry",readOnly:true})
            field.forceActiveFocus(); typeValue("x"); compare(field.text,"Sample entry")
            mouseClick(findChild(field,"bleeckerSecureReveal"))
            compare(field.displayText,"Sample entry"); compare(field.readOnly,true)
        }
    }
}
