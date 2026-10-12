import QtQuick
import QtQuick.Window
import QtTest
import Avelino

Item {
    id: fixture
    width: 640; height: 400
    Item {
        id: ancestor
        width: 300; height: 200
        BleeckerButton { id: button; x: 80.23; y: 60.17; text: "Publish"; size: "sm" }
    }
    Window { id: otherWindow; width: 400; height: 200; visible: false }
    SignalSpy { id: clicks; target: button; signalName: "clicked" }
    TestCase {
        name: "ButtonPaintPlacement"
        when: windowShown
        function init() {
            BleeckerTheme.reducedMotion = true
            BleeckerTheme.textScale = 1
            button.variant = "primary"; button.size = "sm"
            button.parent = ancestor
            ancestor.x = 0; ancestor.y = 0; ancestor.scale = 1; ancestor.rotation = 0
            clicks.clear()
        }
        function cleanup() { button.parent = ancestor; otherWindow.visible = false }
        function placementIsAligned() {
            const surface = findChild(button, "bleeckerButtonSurface")
            const label = findChild(button, "bleeckerButtonLabel")
            if (!surface || !label || !button.Window.window) return false
            const dpr = button.Screen.devicePixelRatio
            const origin = surface.mapToItem(null, 0, 0)
            const baseline = label.mapToItem(null, 0, label.baselineOffset)
            return [origin.x, origin.y, baseline.x, baseline.y].every(function (value) {
                const physical = value * dpr
                // Rotated scene-graph matrices store Float32 values. Allow two
                // rounding units here; image comparisons still allow zero pixels.
                const rounding = 2 * Math.pow(2, -23) * Math.max(1, Math.abs(physical))
                return Math.abs(physical - Math.round(physical)) <= rounding
            })
        }
        function test_ancestor_motion_data() {
            return [
                { tag: "translation", x: 23.37, y: 11.13, scale: 1, rotation: 0 },
                { tag: "scale", x: 20.17, y: 10.23, scale: 1.25, rotation: 0 },
                { tag: "rotation", x: 19.13, y: 13.37, scale: 1, rotation: 8 },
                { tag: "combined", x: 21.23, y: 17.13, scale: 0.9, rotation: -6 }
            ]
        }
        function test_ancestor_motion(data) {
            tryVerify(placementIsAligned)
            const width = button.implicitWidth
            const height = button.implicitHeight
            ancestor.x = data.x; ancestor.y = data.y
            ancestor.scale = data.scale; ancestor.rotation = data.rotation
            tryVerify(placementIsAligned)
            compare(button.x, 80.23); compare(button.y, 60.17)
            compare(button.implicitWidth, width); compare(button.implicitHeight, height)
            mouseClick(button)
            compare(clicks.count, 1)
        }
        function test_reparent_between_displayed_windows() {
            tryVerify(placementIsAligned)
            otherWindow.visible = true
            button.parent = otherWindow.contentItem
            tryCompare(button.Window.window, "visible", true)
            tryVerify(placementIsAligned)
            button.parent = ancestor
            tryVerify(placementIsAligned)
            compare(button.x, 80.23); compare(button.y, 60.17)
        }
        function test_link_label_centering_data() {
            return ["xs", "sm", "md", "lg"].map(function (size) { return {tag: size, size: size} })
        }
        function test_link_label_centering(data) {
            button.variant = "link"; button.size = data.size
            const label = findChild(button, "bleeckerButtonLabel")
            tryVerify(function () { return label.height === label.parent.height })
            compare(label.y, 0)
            compare(button.implicitHeight, label.height)
            tryVerify(placementIsAligned)
        }
    }
}
