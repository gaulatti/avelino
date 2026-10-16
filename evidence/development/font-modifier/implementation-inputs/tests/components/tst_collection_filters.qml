import QtQuick
import QtTest
import Avelino

Item {
    id: root
    width: 760; height: 360
    property string query: ""
    property int edits: 0
    Component { id: chipFactory; BleeckerFilterChip { text: "Edition"; removable: true } }
    Component { id: tall; Rectangle { implicitWidth: 100; implicitHeight: 84 } }
    Component {
        id: collectionFactory
        BleeckerCollectionFilters {
            width: 620; query: root.query
            onQueryEdited: { root.query=query; root.edits++ }
            content: BleeckerFilterChip { text: "Edition"; removable: true }
        }
    }
    TestCase {
        name: "CollectionFilterContracts"
        when: windowShown
        function init() { BleeckerTheme.dark=false; BleeckerTheme.textScale=1; root.query=""; root.edits=0; failOnWarning(/Binding loop/) }
        function cleanup() { BleeckerTheme.textScale=1; BleeckerTheme.dark=false }
        function spy(target,name) { const s=createTemporaryQmlObject('import QtTest; SignalSpy {}',root); s.target=target; s.signalName=name; return s }
        function test_fixed_chip_layout_data() {
            const rows=[]
            for (const dark of [false,true]) for (const scale of [1,1.5]) for (const selected of [false,true]) for (const removable of [false,true])
                rows.push({tag:[dark,scale,selected,removable].join('-'),dark,scale,selected,removable})
            return rows
        }
        function test_fixed_chip_layout(d) {
            BleeckerTheme.dark=d.dark; BleeckerTheme.textScale=d.scale
            const chip=createTemporaryObject(chipFactory,root,{selected:d.selected,removable:d.removable})
            compare(chip.height,28); fuzzyCompare(chip.width,d.removable ? 74.5 : 58.5,0.51)
            compare(chip.font.weight,Font.Medium); compare(chip.font.pointSize,9)
            const action=findChild(chip,"bleeckerFilterAction"),remove=findChild(chip,"bleeckerFilterRemove")
            const activated=spy(chip,"clicked"),removed=spy(chip,"removeRequested")
            mouseClick(action); compare(activated.count,1); compare(removed.count,0); compare(chip.selected,d.selected)
            if (d.removable) { mouseClick(remove); compare(activated.count,1); compare(removed.count,1); verify(chip.visible); compare(chip.selected,d.selected) }
            chip.enabled=false; mouseClick(action); mouseClick(remove); compare(activated.count,1); compare(removed.count,d.removable ? 1 : 0)
        }
        function test_empty_and_wrapped() {
            const chip=createTemporaryObject(chipFactory,root,{text:""})
            compare(chip.width,36); compare(chip.height,28)
            chip.removable=false; compare(chip.width,20)
            chip.width=140; chip.text="A longer filter label wraps in its allocation"
            compare(chip.height,30); chip.removable=true; compare(chip.height,45)
        }
        function test_independent_keyboard_actions() {
            const chip=createTemporaryObject(chipFactory,root)
            const action=findChild(chip,"bleeckerFilterAction"),remove=findChild(chip,"bleeckerFilterRemove")
            const activated=spy(chip,"clicked"),removed=spy(chip,"removeRequested")
            action.forceActiveFocus(Qt.TabFocusReason); keyClick(Qt.Key_Space); compare(activated.count,1)
            keyClick(Qt.Key_Tab); verify(remove.activeFocus); keyClick(Qt.Key_Space); compare(removed.count,1)
            compare(remove.Accessible.name,"Remove Edition"); compare(action.Accessible.role,Accessible.Button)
        }
        function test_collection_binding_layout_and_content() {
            const filters=createTemporaryObject(collectionFactory,root)
            const search=filters.searchField,chip=filters.contentItem
            fuzzyCompare(search.width,620-chip.width-10,0.001); compare(filters.height,40)
            mouseClick(search,60,20); for (const c of "news") keyClick(c.toUpperCase().charCodeAt(0))
            compare(root.query,"news"); compare(root.edits,4)
            mouseClick(findChild(search,"bleeckerSearchClear")); compare(root.query,""); compare(root.edits,5); verify(search.activeFocus)
            root.query="External query"; compare(filters.query,root.query)
            filters.width=320; fuzzyCompare(search.width,320-chip.width-10,0.001)
            chip.width=110; compare(search.width,200)
            filters.content=tall; compare(filters.height,84); compare(search.y,22); compare(search.width,210)
            filters.content=chipFactory; compare(filters.height,40); fuzzyCompare(search.width,320-filters.contentItem.width-10,0.001)
            filters.content=null; compare(search.width,320); compare(filters.height,40)
            BleeckerTheme.textScale=1.5; compare(filters.height,60)
        }
    }
}
