import QtQuick
import QtTest
import Avelino

Item {
    id: root
    width: 500; height: 200
    PixelAlignment { id: metrics; target: root }
    Component { id: component; BleeckerButton { text: "Publish" } }
    Component { id: eyebrowComponent; BleeckerEyebrow { text: "Cards and badges" } }
    TestCase {
        name: "ButtonLogicalTypography"
        when: windowShown
        function init() { BleeckerTheme.textScale = 1; BleeckerTheme.reducedMotion = true }
        function cleanup() { BleeckerTheme.textScale = 1 }
        function test_fractional_scale_data() {
            const rows = []
            const sizes = {xs:12, sm:13, md:14, lg:15}
            for (const size of Object.keys(sizes)) {
                for (const scale of [1, 1.125, 1.25, 1.5])
                    rows.push({tag:size + "-" + scale, size:size, pixels:sizes[size], scale:scale})
            }
            return rows
        }
        function test_fractional_scale(data) {
            const button = createTemporaryObject(component, parent, {size:data.size})
            verify(button)
            const label = findChild(button, "bleeckerButtonLabel")
            BleeckerTheme.textScale = data.scale
            tryCompare(label, "logicalPixelSize", data.pixels * data.scale)
            const reference = nativeTypography.find(row => row.family === "primary" && row.weight === "medium"
                && row.mode === "button" && row.requestedSize === data.pixels * data.scale
                && row.dpr === metrics.devicePixelRatio)
            verify(reference, "The exact requested size must have a measured source case")
            compare(label.resolvedPixelSize, reference.metrics.resolvedPointSize)
            compare(label.implicitWidth, reference.width)
            compare(label.naturalHeight, reference.height)
            compare(label.baselineOffset, reference.baseline)
            compare(label.resolvedFamily, "Encode Sans")
            compare(label.resolvedStyle, "Medium")
        }
        function test_consumer_font_size_override() {
            const button = createTemporaryObject(component, parent)
            const label = findChild(button, "bleeckerButtonLabel")
            button.font.pixelSize = 18
            tryCompare(label, "logicalPixelSize", 18)
        }
        function test_source_eyebrow_tracking_data() {
            const rows = []
            for (const scale of [1, 1.5])
                for (const dark of [false, true])
                    rows.push({tag:scale + "-" + dark, scale:scale, dark:dark})
            return rows
        }
        function test_source_eyebrow_tracking(data) {
            BleeckerTheme.textScale = data.scale; BleeckerTheme.dark = data.dark
            const label = createTemporaryObject(eyebrowComponent, parent)
            // All eight pinned desktop eyebrow proposal cases measure 103x12,
            // including the final 1.15-unit tracking space at both DPRs.
            compare(label.implicitWidth, 103)
            compare(label.implicitHeight, 12)
            BleeckerTheme.dark = false
        }
        function test_literal_label_and_line_break() {
            const button = createTemporaryObject(component, parent)
            const label = findChild(button, "bleeckerButtonLabel")
            button.text = "<b>Publish</b>"
            compare(label.text, "<b>Publish</b>")
            const literalWidth = label.implicitWidth
            button.text = "Publish"
            verify(label.implicitWidth < literalWidth)
            const height = label.naturalHeight
            button.text = "Publish\nAgain"
            tryCompare(label, "naturalHeight", height * 2)
            verify(button.implicitHeight >= label.height)
        }
    }
}
