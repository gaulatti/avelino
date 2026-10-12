import QtQuick
import QtTest
import Avelino

TestCase {
    name: "ControlledActionsAndEditing"
    width: 640; height: 400
    when: windowShown
    BleeckerButton { id: button; x: 20; y: 20; text: "Publish" }
    BleeckerTextField { id: field; x: 20; y: 100; placeholderText: "Title" }
    SignalSpy { id: clicks; target: button; signalName: "clicked" }
    function init() { button.enabled = true; button.loading = false; button.variant = "primary"; BleeckerTheme.dark = false; BleeckerTheme.textScale = 1; BleeckerTheme.reducedMotion = true; field.text = ""; clicks.clear() }
    function test_pointer_activation_and_disabled() {
        mouseClick(button)
        compare(clicks.count, 1)
        button.enabled = false
        mouseClick(button)
        compare(clicks.count, 1)
    }
    function test_keyboard_activation() {
        button.forceActiveFocus()
        verify(button.activeFocus)
        keyClick(Qt.Key_Space)
        compare(clicks.count, 1)
    }
    function test_loading_suppresses_actions() {
        // Restore the declaration's loading binding after previous tests override it.
        button.enabled = Qt.binding(function() { return !button.loading })
        button.loading = true
        mouseClick(button)
        compare(clicks.count, 0)
        verify(!button.enabled)
    }
    function test_actual_edit_selection_and_replacement() {
        mouseClick(field)
        verify(field.activeFocus)
        keyClick(Qt.Key_A)
        keyClick(Qt.Key_B)
        compare(field.text, "ab")
        keyClick(Qt.Key_A, Qt.ControlModifier)
        compare(field.selectedText, "ab")
        keyClick(Qt.Key_C)
        compare(field.text, "c")
    }
    function test_host_theme_independent_dark_and_text_scale() {
        BleeckerTheme.dark = true
        compare(button.background.color, Qt.color("#5ba3f5"))
        compare(field.color, Qt.color("#f0f4f8"))
        BleeckerTheme.textScale = 1.5
        compare(field.implicitHeight, 60)
        compare(button.font.pixelSize, 21)
    }
}
