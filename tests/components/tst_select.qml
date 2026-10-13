import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino

Item {
    id: root
    width: 760; height: 560
    property var chosen: "a"
    property int activations: 0
    Component {
        id: selectFactory
        BleeckerSelect {
            x: 40; y: 420; width: 280
            selection: root.chosen
            options: [{value:"a",label:"Morning"},{value:"b",label:"Disabled",disabled:true},{value:"c",label:"Evening"}]
            onActivated: value => { root.chosen=value; root.activations++ }
        }
    }
    Component { id: nextFieldFactory; BleeckerTextField { x: 400; y: 420; width: 200; placeholderText: "Next field" } }
    TestCase {
        name: "SelectContracts"
        when: windowShown
        function init() { root.chosen="a"; root.activations=0; BleeckerTheme.dark=false; BleeckerTheme.textScale=1; BleeckerTheme.reducedMotion=true }
        function cleanup() { BleeckerTheme.dark=false; BleeckerTheme.textScale=1 }
        function test_pointer_options_authoritative_selection_and_disabled() {
            const item=createTemporaryObject(selectFactory,root)
            mouseClick(item); tryCompare(item,"presented",true)
            const list=item.popup.contentItem
            tryCompare(list,"count",3)
            const disabled=list.itemAtIndex(1), last=list.itemAtIndex(2)
            verify(disabled); verify(last); compare(disabled.enabled,false)
            mouseClick(disabled); compare(root.chosen,"a"); compare(root.activations,0); compare(item.presented,true)
            mouseClick(last); tryCompare(item,"presented",false); compare(root.chosen,"c"); compare(item.displayText,"Evening")
            root.chosen="a"; compare(item.displayText,"Morning")
            item.enabled=false; mouseClick(item); compare(item.presented,false); compare(root.activations,1)
        }
        function test_keyboard_skip_disabled_commit_escape_and_focus() {
            const item=createTemporaryObject(selectFactory,root)
            item.forceActiveFocus(); keyClick(Qt.Key_Space); tryCompare(item,"presented",true)
            const list=item.popup.contentItem
            tryCompare(list,"currentIndex",0)
            keyClick(Qt.Key_Down); compare(list.currentIndex,2); compare(root.chosen,"a")
            keyClick(Qt.Key_Return); tryCompare(item,"presented",false); compare(root.chosen,"c"); verify(item.activeFocus)
            keyClick(Qt.Key_Space); tryCompare(item,"presented",true)
            keyClick(Qt.Key_Home); compare(list.currentIndex,0)
            keyClick(Qt.Key_Escape); tryCompare(item,"presented",false); compare(root.chosen,"c"); verify(item.activeFocus)
            keyClick(Qt.Key_Space); tryCompare(item,"presented",true)
            keyClick(Qt.Key_Up); compare(list.currentIndex,0)
            keyClick(Qt.Key_Space); tryCompare(item,"presented",false); compare(root.chosen,"a")
        }
        function test_unknown_empty_and_model_mutation_do_not_select_defaults() {
            root.chosen="missing"
            const item=createTemporaryObject(selectFactory,root)
            compare(item.displayText,"Select…"); compare(root.chosen,"missing")
            mouseClick(item); tryCompare(item,"presented",true)
            item.options=[]; tryCompare(item.popup.contentItem,"count",0); compare(item.presented,true); compare(item.displayText,"Select…"); compare(root.activations,0)
            keyClick(Qt.Key_Return); compare(root.activations,0); compare(root.chosen,"missing")
            keyClick(Qt.Key_Escape); tryCompare(item,"presented",false)
            item.options=[{value:0,label:"Zero"},{value:false,label:"False"}]; root.chosen=0; compare(item.displayText,"Zero")
            root.chosen=false; compare(item.displayText,"False")
        }
        function test_scrolling_end_selection_and_disabling_open_popup() {
            const rows=[]; for (let i=0;i<40;i++) rows.push({value:i,label:"Edition "+i,disabled:i===39})
            root.chosen=0
            const item=createTemporaryObject(selectFactory,root,{options:rows})
            mouseClick(item); tryCompare(item,"presented",true); compare(item.popup.height,288)
            const list=item.popup.contentItem
            keyClick(Qt.Key_End); compare(list.currentIndex,38); verify(list.contentY>0)
            const scrollbar=findChild(list,"bleeckerSelectScrollBar"); verify(scrollbar.size<1)
            keyClick(Qt.Key_Return); compare(root.chosen,38); compare(root.activations,1)
            mouseClick(item); tryCompare(item,"presented",true)
            item.enabled=false; tryCompare(item,"presented",false); compare(root.chosen,38)
        }
        function test_outside_dismissal_tab_focus_and_constrained_label() {
            const item=createTemporaryObject(selectFactory,root), field=createTemporaryObject(nextFieldFactory,root)
            item.forceActiveFocus(); keyClick(Qt.Key_Space); tryCompare(item,"presented",true)
            mouseClick(root,700,520); tryCompare(item,"presented",false); compare(root.activations,0)
            item.forceActiveFocus(); keyClick(Qt.Key_Tab); verify(field.activeFocus)
            root.chosen="a"; item.options=[{value:"a",label:"A substantially longer choice with accents é and an emoji 👩‍💻"}]
            item.width=160; BleeckerTheme.textScale=1.5
            const label=findChild(item,"bleeckerSelectLabel")
            verify(label.unwrappedWidth>label.width); compare(label.elideWidth,label.width); verify(label.implicitWidth<=label.width)
            BleeckerTheme.dark=true
            compare(findChild(item,"bleeckerSelectSurface").color.toString(),BleeckerTheme.palette.card.toString())
        }
    }
}
