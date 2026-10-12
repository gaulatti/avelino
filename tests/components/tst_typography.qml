import QtQuick
import QtTest
import Avelino

Item {
    width: 500; height: 200
    Component { id: component; BleeckerButton { text: "Publish" } }
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
            const width = label.implicitWidth
            BleeckerTheme.textScale = data.scale
            tryCompare(label, "logicalPixelSize", data.pixels * data.scale)
            verify(Math.abs(label.implicitWidth - width * data.scale) < 0.000001)
            compare(label.resolvedFamily, "Encode Sans")
            compare(label.resolvedStyle, "Medium")
        }
        function test_consumer_font_size_override() {
            const button = createTemporaryObject(component, parent)
            const label = findChild(button, "bleeckerButtonLabel")
            button.font.pixelSize = 18
            tryCompare(label, "logicalPixelSize", 18)
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
