import QtQuick
import QtTest
import QtQuick.Templates as T
import Avelino

Item {
    id: root
    width: 700; height: 400
    property bool chosen: false
    property int changes: 0
    Component { id: factory; BleeckerCheckbox { text: "Keep edition" } }
    Component {
        id: inheritedFactory
        T.Control {
            font.bold: true
            contentItem: BleeckerCheckbox { objectName: "inheritedCheckbox"; text: "Keep edition" }
        }
    }
    Component {
        id: boundFactory
        BleeckerCheckbox {
            text: "Keep edition"; checked: root.chosen
            onToggled: { root.chosen = checked; root.changes++ }
        }
    }
    TestCase {
        name: "CheckboxContracts"
        when: windowShown
        function init() {
            BleeckerTheme.dark = false; BleeckerTheme.textScale = 1
            root.chosen = false; root.changes = 0
            failOnWarning(/Binding loop/)
        }
        function cleanup() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1 }
        function test_geometry_state_and_input_data() {
            const rows = []
            for (const dark of [false, true]) for (const size of ["sm", "md", "lg"])
                for (const checked of [false, true]) for (const scale of [1, 1.5])
                    rows.push({tag: dark+"-"+size+"-"+checked+"-"+scale, dark, size, checked, scale})
            return rows
        }
        function test_geometry_state_and_input(data) {
            BleeckerTheme.dark = data.dark; BleeckerTheme.textScale = data.scale
            const item = createTemporaryObject(factory, root, {size: data.size, checked: data.checked})
            const indicator = findChild(item, "bleeckerCheckboxIndicator")
            const label = findChild(item, "bleeckerCheckboxLabel")
            const glyph = findChild(item, "bleeckerCheckboxGlyph")
            const edge = data.size === "sm" ? 14 : data.size === "lg" ? 22 : 18
            const fontSize = data.size === "sm" ? 11 : data.size === "lg" ? 16 : 14
            compare(indicator.width, edge); compare(indicator.height, edge); compare(indicator.radius, 4)
            compare(label.x, edge + (data.size === "sm" ? 6 : 10))
            compare(label.logicalPixelSize, fontSize * data.scale)
            compare(glyph.width, 10); compare(glyph.visible, data.checked)
            compare(indicator.color.toString(), (data.checked ? BleeckerTheme.palette.primary : BleeckerTheme.palette.card).toString())
            compare(item.Accessible.name, "Keep edition")
            compare(item.Accessible.role, Accessible.CheckBox)
            compare(item.Accessible.description, data.checked ? "Selected" : "Not selected")
            mouseClick(item, item.width - 2, item.height / 2)
            compare(item.checked, !data.checked)
            item.forceActiveFocus(); keyClick(Qt.Key_Space); compare(item.checked, data.checked)
            item.enabled = false
            mouseClick(item); keyClick(Qt.Key_Space); compare(item.checked, data.checked)
            compare(item.opacity, 0.5)
        }
        function test_bound_state_and_focus_path() {
            const first = createTemporaryObject(boundFactory, root)
            const disabled = createTemporaryObject(factory, root, {x: 200, enabled: false})
            const next = createTemporaryObject(factory, root, {x: 400})
            mouseClick(first); compare(root.chosen, true); compare(root.changes, 1)
            root.chosen = false; compare(first.checked, false)
            root.chosen = true; compare(first.checked, true)
            first.forceActiveFocus(Qt.TabFocusReason); keyClick(Qt.Key_Space)
            compare(root.chosen, false); compare(root.changes, 2)
            keyClick(Qt.Key_Tab); verify(next.activeFocus); verify(!disabled.activeFocus)
            keyClick(Qt.Key_Backtab); verify(first.activeFocus)
            verify(first.visualFocus); verify(findChild(first, "bleeckerCheckboxFocus").visible)
        }
        function test_wrapping_empty_and_scaling() {
            const item = createTemporaryObject(factory, root, {width: 160, text: "Keep selected editions available for review"})
            const label = findChild(item, "bleeckerCheckboxLabel")
            tryVerify(() => label.naturalHeight > 17.5)
            compare(item.height, label.height)
            const indicator = findChild(item, "bleeckerCheckboxIndicator")
            compare(indicator.y, (item.height - 18) / 2)
            BleeckerTheme.textScale = 1.5
            compare(label.logicalPixelSize, 21); compare(indicator.width, 18)
            const empty = createTemporaryObject(factory, root, {text: "", checked: true})
            compare(empty.width, 28); compare(empty.height, 18)
            verify(findChild(empty, "bleeckerCheckboxGlyph").visible)
            item.LayoutMirroring.enabled = true
            compare(indicator.x, item.width - 18); compare(label.x, 0)
        }
        function test_source_font_weight_overrides_parent_font() {
            const parent = createTemporaryObject(inheritedFactory, root)
            const item = findChild(parent, "inheritedCheckbox")
            compare(item.font.weight, Font.Normal)
            compare(findChild(item, "bleeckerCheckboxLabel").resolvedStyle, "Regular")
        }
    }
}
