import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

Item {
    id: root
    width: 750; height: 340
    property string query: ""
    property int edits: 0
    Component { id: factory; BleeckerSearchField { width: 300; placeholderText: "Search editions" } }
    Component { id: nextFactory; BleeckerTextField { width: 180 } }
    Component { id: slot; Rectangle { implicitWidth: 20; implicitHeight: 22 } }
    Component { id: inheritedFactory; T.Control { font.bold: true; contentItem: BleeckerSearchField { objectName: "inheritedSearch" } } }
    Component {
        id: boundFactory
        BleeckerSearchField {
            width: 300; placeholderText: "Search editions"; text: root.query
            onTextEdited: { root.query=text; root.edits++ }
        }
    }
    TestCase {
        name: "SearchFieldContracts"
        when: windowShown
        function init() { BleeckerTheme.dark=false; BleeckerTheme.textScale=1; root.query=""; root.edits=0; failOnWarning(/Binding loop/) }
        function cleanup() { BleeckerTheme.dark=false; BleeckerTheme.textScale=1 }
        function typeValue(text) { for (const ch of text) keyClick(ch.toUpperCase().charCodeAt(0)) }
        function test_source_sizes_data() {
            const rows=[]
            for (const size of ["sm","md","lg"]) for (const dark of [false,true])
                for (const scale of [1,1.5]) for (const text of ["","Morning edition"])
                    rows.push({tag:size+"-"+dark+"-"+scale+"-"+text,size,dark,scale,text})
            return rows
        }
        function test_source_sizes(data) {
            BleeckerTheme.dark=data.dark; BleeckerTheme.textScale=data.scale
            const field=createTemporaryObject(factory,root,{size:data.size,text:data.text})
            const leading=findChild(field,"bleeckerTextFieldLeading"),trailing=findChild(field,"bleeckerTextFieldTrailing")
            const padding=data.size==="sm" ? 12 : data.size==="lg" ? 16 : 14
            compare(field.height,(data.size==="sm" ? 36 : data.size==="lg" ? 44 : 40)*data.scale)
            compare(leading.width,16.5); compare(leading.x,padding)
            compare(field.leftPadding,padding+26.5)
            compare(field.rightPadding,padding+(data.text==="" ? 0 : 28.5))
            compare(Boolean(trailing.item),data.text!=="")
            compare(field.Accessible.name,"Search editions")
            if (trailing.item) {
                compare(trailing.item.Accessible.role,Accessible.Button)
                compare(trailing.item.Accessible.name,"Clear search")
                mouseClick(trailing.item)
                compare(field.text,""); verify(field.activeFocus)
                compare(field.rightPadding,padding); compare(trailing.item,null)
            }
        }
        function test_caller_model_and_disabled_clear() {
            const field=createTemporaryObject(boundFactory,root)
            mouseClick(field,60,20); typeValue("news")
            compare(root.query,"news"); compare(root.edits,4)
            let action=findChild(field,"bleeckerSearchClear")
            mouseClick(action); compare(root.query,""); compare(root.edits,5); verify(field.activeFocus)
            root.query="External query"; compare(field.text,root.query)
            field.enabled=false; action=findChild(field,"bleeckerSearchClear")
            mouseClick(action); typeValue("x"); compare(root.query,"External query"); compare(root.edits,5)
            field.enabled=true; field.readOnly=true; action=findChild(field,"bleeckerSearchClear")
            verify(!action.enabled); mouseClick(action); compare(root.query,"External query")
        }
        function test_keyboard_clear_and_traversal() {
            const field=createTemporaryObject(factory,root,{text:"Morning edition"})
            const disabled=createTemporaryObject(factory,root,{x:320,width:140,enabled:false})
            const next=createTemporaryObject(nextFactory,root,{x:500})
            const action=findChild(field,"bleeckerSearchClear")
            field.forceActiveFocus(Qt.TabFocusReason); keyClick(Qt.Key_Tab); verify(action.activeFocus)
            keyClick(Qt.Key_Tab); verify(next.activeFocus); verify(!disabled.activeFocus)
            keyClick(Qt.Key_Backtab); verify(action.activeFocus)
            keyClick(Qt.Key_Space); compare(field.text,""); verify(field.activeFocus)
            keyClick(Qt.Key_Tab); verify(next.activeFocus)
        }
        function test_generic_slots_resize_and_remove() {
            const field=createTemporaryObject(nextFactory,root)
            compare(field.leftPadding,14); compare(field.rightPadding,14)
            field.leading=slot; field.trailing=slot
            compare(field.leftPadding,44); compare(field.rightPadding,44)
            const leading=findChild(field,"bleeckerTextFieldLeading")
            leading.item.implicitWidth=35; compare(field.leftPadding,59)
            leading.item.implicitHeight=80; compare(field.implicitHeight,80)
            field.leading=null; field.trailing=null
            compare(field.leftPadding,14); compare(field.rightPadding,14); compare(field.implicitHeight,40)
        }
        function test_narrow_input_and_return() {
            const field=createTemporaryObject(factory,root,{width:160,text:"A longer fictional search query for the native fixture"})
            field.forceActiveFocus(); keyClick(Qt.Key_End)
            verify(field.contentWidth>field.width-field.leftPadding-field.rightPadding)
            verify(field.cursorRectangle.x+field.cursorRectangle.width<=field.width-field.rightPadding+1)
            const signal=Qt.createQmlObject('import QtTest; SignalSpy {}',root)
            signal.target=field; signal.signalName="accepted"
            keyClick(Qt.Key_Return); compare(signal.count,1); signal.destroy()
        }
        function test_source_regular_and_explicit_font_override() {
            const host=createTemporaryObject(inheritedFactory,root)
            const field=findChild(host,"inheritedSearch")
            compare(field.font.weight,Font.Normal)
            field.font.weight=Font.Bold; compare(field.font.weight,Font.Bold)
        }
    }
}
