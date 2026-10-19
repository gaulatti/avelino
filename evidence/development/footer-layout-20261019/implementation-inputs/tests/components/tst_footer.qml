import QtQuick
import QtTest
import Avelino
import "../consumer" as Fixtures

Item {
    id: root
    width: 400; height: 180
    PixelAlignment { id: metrics; target: root }
    Component { id: factory; Fixtures.FooterCase {} }
    TestCase {
        name: "FooterSourceLayout"
        when: windowShown
        function init() {
            BleeckerTheme.dark = false
            BleeckerTheme.textScale = 1
            failOnWarning(/Binding loop/)
        }
        function cleanup() { BleeckerTheme.dark = false; BleeckerTheme.textScale = 1 }
        function test_source_frames_data() {
            return nativeFooterCaptures.filter(row => row.dpr === metrics.devicePixelRatio)
                .map(row => ({ tag: row.path, row: row }))
        }
        function frame(item) {
            const point = item.mapToItem(root, 0, 0)
            return { x: point.x, y: point.y, width: item.width, height: item.height }
        }
        function compareFrame(actual, expected, name) {
            for (const key of ["x", "y", "width", "height"])
                compare(actual[key], expected[key], name + " " + key)
        }
        function test_source_frames(data) {
            const row = data.row
            BleeckerTheme.dark = row.appearance === "dark"
            BleeckerTheme.textScale = row.textScale
            const item = createTemporaryObject(factory, root, { definition: row })
            verify(item)
            item.x = Qt.binding(() => (root.width - item.width) / 2)
            item.y = Qt.binding(() => (root.height - item.height) / 2)
            wait(25)
            compareFrame(frame(item), row.frames.component, "footer")
            for (const name of ["first", "second"]) {
                if (row.frames[name] === undefined) continue
                const child = findChild(item, name)
                verify(child, "Source child " + name)
                compareFrame(frame(child), row.frames[name], name)
            }
            if (row.variant === "hidden-block")
                compare(findChild(item, "first").visible, false)
        }
    }
}
