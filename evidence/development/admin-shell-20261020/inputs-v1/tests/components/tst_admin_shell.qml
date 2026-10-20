import QtQuick
import QtQuick.Templates as T
import QtTest
import Avelino
import "../consumer" as Fixtures

Item {
    id: root
    width: 1100; height: 700
    Component { id: factory; Fixtures.AdminShellCase {} }
    Component { id: controlCaller; T.Button { width:180; height:90; property int activations:0; onClicked:++activations } }
    TestCase {
        name: "DesktopAdminShellSource"
        when: windowShown
        function init() { BleeckerTheme.dark = false; failOnWarning(/Binding loop/) }
        function cleanup() { BleeckerTheme.dark = false }
        function compareState(fixture, state, step) {
            const actual = fixture.snapshot()
            for (const key of ["navigation", "requests", "pending", "displayedNavigation", "columnWidth"])
                compare(actual[key], state[key], step + " " + key)
            compare(Object.keys(actual.frames).sort(), Object.keys(state.frames).sort())
            for (const name of Object.keys(state.frames)) for (const axis of ["x", "y", "width", "height"])
                compare(actual.frames[name][axis], state.frames[name][axis], step + " " + name + " " + axis)
        }
        function test_native_profiles_data() { return nativeAdminShellWitnesses.profiles.map(row => Object.assign({tag:row.name}, row)) }
        function test_native_profiles(row) {
            BleeckerTheme.dark = row.dark
            const fixture = createTemporaryObject(factory, root, {definition:row.definition, initial:row.initial})
            verify(fixture); wait(30)
            compare(fixture.toolbarItem.parent, null, "Body must not host its toolbar")
            compareState(fixture, row.state, row.name)
        }
        function test_native_histories_data() { return nativeAdminShellWitnesses.histories.map(row => Object.assign({tag:row.owner + "-" + row.initial}, row)) }
        function test_native_histories(row) {
            const fixture = createTemporaryObject(factory, root, {definition:row.definition, initial:row.initial, owner:row.owner})
            verify(fixture)
            for (const state of row.states) { fixture.applyStep(state.step); wait(30); compareState(fixture, state, state.step) }
        }
        function test_native_divider_boundaries_data() { return nativeAdminShellWitnesses.boundaries.map(row => Object.assign({tag:row.columnWidth + "-" + row.initial + "-" + row.requestedPosition}, row)) }
        function test_native_divider_boundaries(row) {
            const definition = Object.assign({}, nativeAdminShellWitnesses.profiles[0].definition, {columnWidth:row.columnWidth})
            const fixture = createTemporaryObject(factory, root, {definition:definition, initial:row.initial, owner:"ignore"})
            verify(fixture); wait(30)
            fixture.shell.setDividerPosition(row.requestedPosition); wait(30)
            compare(fixture.shell.displayedNavigation, !row.after[0].collapsed)
            compare(fixture.shell.columnWidth, row.after[0].width)
            compare(fixture.navigation, row.navigation)
            compare(fixture.requests, row.requests)
        }
        function test_toolbar_owner_and_retained_controls() {
            const fixture = createTemporaryObject(factory, root, {definition:nativeAdminShellWitnesses.profiles[0].definition,
                initial:true, owner:"ignore", sidebarOverride:controlCaller, headerOverride:controlCaller})
            verify(fixture); wait(30)
            const toolbar = fixture.toolbarItem
            toolbar.parent = root; toolbar.x = 940; toolbar.width = 104; toolbar.height = 52
            const side = fixture.shell.sidebarItem, head = fixture.shell.headerItem
            mouseClick(side, 90, 45); compare(side.activations, 1)
            mouseClick(toolbar.visibilityButton, 18, 18); wait(30)
            verify(!fixture.shell.displayedNavigation); verify(fixture.navigation)
            compare(fixture.requests, [false])
            compare(fixture.shell.sidebarItem, side); compare(fixture.shell.headerItem, head)
            mouseClick(toolbar.requestButton, 18, 18); wait(30)
            compare(fixture.requests, [false, false], "Explicit action must toggle the caller's true value")
            verify(!fixture.shell.displayedNavigation)
            mouseClick(toolbar.visibilityButton, 18, 18); wait(30)
            verify(fixture.shell.displayedNavigation); compare(fixture.requests, [false, false, true])
            mouseClick(side, 90, 45); compare(side.activations, 2)
            fixture.shell.enabled = false
            verify(!toolbar.visibilityButton.enabled); verify(!toolbar.requestButton.enabled)
            mouseClick(toolbar.requestButton, 18, 18); compare(fixture.requests, [false, false, true])
        }
        function test_pointer_divider_retains_caller_binding() {
            const fixture = createTemporaryObject(factory, root, {definition:nativeAdminShellWitnesses.profiles[0].definition, initial:true})
            verify(fixture); wait(30)
            const split = fixture.shell.splitItem
            const caller = fixture.shell.sidebarItem
            mousePress(split, 300, 150); mouseMove(split, 260, 150, 30); mouseRelease(split, 260, 150); wait(30)
            compare(fixture.shell.columnWidth, 260)
            mousePress(split, 260, 150); mouseMove(split, 0, 150, 30); mouseRelease(split, 0, 150); wait(30)
            verify(!fixture.shell.displayedNavigation); compare(fixture.navigation, false)
            compare(fixture.shell.sidebarItem, caller)
            mousePress(split, 1, 150); mouseMove(split, 181, 150, 30); mouseRelease(split, 181, 150); wait(30)
            verify(fixture.shell.displayedNavigation); compare(fixture.navigation, true)
            compare(fixture.shell.columnWidth, 220); compare(fixture.shell.sidebarItem, caller)
            compare(caller.width, 180); compare(caller.height, 90)
        }
    }
}
