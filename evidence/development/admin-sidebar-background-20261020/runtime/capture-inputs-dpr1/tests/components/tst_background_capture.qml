import QtQuick
import QtTest
import Avelino
import "../consumer" as Fixtures
import "witnesses.js" as Native
Item {
    id: root
    width: 1100; height: 700
    Component { id: factory; Fixtures.AdminShellCase {} }
    TestCase {
        name: "AdminSidebarBackgroundCapture"
        when: windowShown
        function test_capture_data() {
            return Native.data.profiles.filter(row => row.definition.id === "standard" && row.initial)
                .map(row => Object.assign({tag:row.name}, row))
        }
        function test_capture(row) {
            BleeckerTheme.dark = row.dark
            const fixture = createTemporaryObject(factory, root, {definition:row.definition, initial:true})
            verify(fixture); wait(40)
            const background = findChild(fixture, "bleeckerAdminSidebarBackground")
            verify(background.visible)
            const p = background.mapToItem(fixture, 0, 0)
            compare(p.x, 44); compare(p.y, 0)
            compare(background.width, 212); compare(background.height, 500)
            let finished = false, saved = false
            verify(fixture.grabToImage(function(result) {
                saved = result.saveToFile("/capture/" + row.name + ".png"); finished = true
            }))
            tryVerify(function() { return finished }, 5000)
            verify(saved)
        }
    }
}
