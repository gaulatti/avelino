import QtQuick
import QtTest
import Avelino
import "../consumer" as Fixtures
import "witnesses.js" as Native
import "../consumer/native-admin-shell-colours.js" as Inputs
Item {
    id: root
    width: 1100; height: 700
    Component { id: factory; Fixtures.AdminShellCase {} }
    TestCase {
        name: "AdminSourceColourFixtureCapture"
        when: windowShown
        function test_capture_data() { return Native.data.profiles.map(row => Object.assign({tag:row.name}, row)) }
        function test_capture(row) {
            BleeckerTheme.dark = row.dark
            const fixture = createTemporaryObject(factory, root, {definition:row.definition, initial:row.initial})
            verify(fixture); wait(40)
            const actual = fixture.snapshot()
            for (const key of ["navigation", "requests", "pending", "displayedNavigation", "columnWidth"])
                compare(actual[key], row.state[key], row.name + " " + key)
            compare(Object.keys(actual.frames).sort(), Object.keys(row.state.frames).sort())
            for (const role of Object.keys(row.state.frames)) for (const axis of ["x", "y", "width", "height"])
                compare(actual.frames[role][axis], row.state.frames[role][axis], role + " " + axis)
            const items = {root:findChild(fixture, "adminShellFixtureBackground"), sidebar:fixture.shell.sidebarItem,
                header:fixture.shell.headerItem, content:fixture.shell.contentSlotItem}
            const colours = {}
            for (const role of Object.keys(items)) {
                if (!items[role]) continue
                const value = Inputs.environments[row.dark ? "dark" : "light"][role].encodedSRGB
                compare(items[role].color, Qt.rgba(value[0], value[1], value[2], value[3]))
                const c = items[role].color
                colours[role] = [c.r, c.g, c.b, c.a]
            }
            let finished = false, saved = false
            verify(fixture.grabToImage(function(result) {
                saved = result.saveToFile("/capture/" + row.name + ".png"); finished = true
            }))
            tryVerify(function() { return finished }, 5000); verify(saved)
            console.log("SOURCE_COLOUR " + JSON.stringify({name:row.name, dark:row.dark, initial:row.initial,
                width:fixture.width, height:fixture.height, state:actual, colours:colours}))
        }
    }
}
