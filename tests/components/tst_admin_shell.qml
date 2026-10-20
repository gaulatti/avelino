import QtQuick
import QtQuick.Window
import QtQuick.Templates as T
import QtTest
import Avelino
import "../consumer" as Fixtures
import "native-admin-divider.js" as Divider
import "../consumer/native-admin-shell-colours.js" as SourceColours

Item {
    id: root
    width: 1100; height: 700
    Component { id: factory; Fixtures.AdminShellCase {} }
    Component { id: controlCaller; T.Button { width:180; height:90; property int activations:0; onClicked:++activations } }
    Component { id: windowFactory; Fixtures.AdminShell { property bool consumerDark:false; property real consumerTextScale:1 } }
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
            compareCallerColours(fixture, row.dark)
            const background = findChild(fixture, "bleeckerAdminSidebarBackground")
            verify(background)
            compare(background.visible, row.initial && row.state.frames.sidebar !== undefined)
            if (row.initial && row.state.frames.sidebar !== undefined) {
                const caller = row.state.frames.sidebar
                const position = background.mapToItem(fixture, 0, 0)
                compare(position.x, caller.x - 16)
                compare(position.y, row.state.frames.root.y)
                compare(background.width, caller.width + 32)
                compare(background.height, Math.max(row.state.frames.root.height, caller.height + 32))
            }
        }
        function compareCallerColours(fixture, dark) {
            const inputs = SourceColours.environments[dark ? "dark" : "light"]
            const items = {root:findChild(fixture, "adminShellFixtureBackground"), sidebar:fixture.shell.sidebarItem,
                header:fixture.shell.headerItem, content:fixture.shell.contentSlotItem}
            verify(items.root)
            for (const role of Object.keys(items)) {
                if (!items[role]) continue
                const v = inputs[role].encodedSRGB
                compare(items[role].color, Qt.rgba(v[0], v[1], v[2], v[3]), role + " source colour")
            }
        }
        function test_source_colour_scheme_updates_retained_callers() {
            const row = nativeAdminShellWitnesses.profiles.find(row => row.definition.id === "standard" && row.initial && !row.dark)
            const fixture = createTemporaryObject(factory, root, {definition:row.definition, initial:true})
            verify(fixture); wait(30)
            const sidebar = fixture.shell.sidebarItem, header = fixture.shell.headerItem, content = fixture.shell.contentSlotItem
            compareCallerColours(fixture, false)
            BleeckerTheme.dark = true; wait(30)
            compare(fixture.shell.sidebarItem, sidebar); compare(fixture.shell.headerItem, header)
            compare(fixture.shell.contentSlotItem, content)
            compareCallerColours(fixture, true)
            compareState(fixture, row.state, "appearance update")
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
        function test_native_divider_view_data() { return Divider.rows }
        function test_native_divider_view(row) {
            BleeckerTheme.dark = row.dark
            const fixture = createTemporaryObject(factory, root, {definition:nativeAdminShellWitnesses.profiles[0].definition, initial:row.initial})
            verify(fixture); wait(30)
            const divider = findChild(fixture, "bleeckerAdminDivider")
            verify(divider)
            compare(divider.visible, row.visible)
            compare(divider.color, Qt.rgba(row.rgba[0], row.rgba[1], row.rgba[2], row.rgba[3]))
            if (row.visible) {
                const position = divider.mapToItem(fixture, 0, 0)
                compare(position.x + divider.width, row.frame.x + row.frame.width)
                compare(position.y, row.frame.y)
                compare(divider.height, row.frame.height)
                compare(divider.width * root.Screen.devicePixelRatio, row.frame.width * row.sourceDpr)
            }
        }
        function test_toolbar_keyboard_and_shortcut() {
            const fixture = createTemporaryObject(factory, root, {definition:nativeAdminShellWitnesses.profiles[0].definition, initial:true})
            verify(fixture); wait(30)
            const toolbar = fixture.toolbarItem
            toolbar.parent = root; toolbar.x = 940; toolbar.width = 104; toolbar.height = 52
            toolbar.visibilityButton.forceActiveFocus(Qt.TabFocusReason)
            keyClick(Qt.Key_Tab); verify(toolbar.requestButton.activeFocus)
            keyClick(Qt.Key_Space); wait(30)
            // Applying a caller request also produces native visibility
            // feedback. This Qt keyboard check does not accept native timing.
            verify(!fixture.navigation); compare(fixture.requests, [false, false])
            keyClick(Qt.Key_S, Qt.MetaModifier | Qt.ControlModifier); wait(30)
            verify(fixture.navigation); compare(fixture.requests, [false, false, true, true])
        }
        function test_window_host_and_resize() {
            const window = createTemporaryObject(windowFactory, root)
            verify(window); wait(60)
            compare(window.width, 840); compare(window.height, 552)
            compare(window.header, window.primaryFixture.toolbarItem)
            const row = nativeAdminShellWitnesses.profiles[0]
            window.configure(row, "delay"); wait(60)
            compare(window.primaryFixture.owner, "delay")
            compare(window.primaryFixture.navigation, false)
            compare(window.primaryFixture.pending, false)
            const fixture = window.primaryFixture
            window.applyStep("external-true"); wait(30)
            window.applyStep("resize-360"); wait(30)
            compare(window.primaryFixture, fixture)
            compare(window.width, 360); compare(fixture.width, 360)
            compare(fixture.snapshot().frames.root, {x:-60, y:0, width:480, height:500})
            const side = fixture.shell.sidebarItem
            window.resizeViewport(840, 24); wait(30)
            compare(window.primaryFixture, fixture); compare(fixture.shell.sidebarItem, side)
            compare(fixture.snapshot().frames.root, {x:0, y:-49, width:840, height:122})
        }
    }
}
