import QtQuick
import QtTest
import Avelino

Item {
    id: root
    width: 500; height: 240
    PixelAlignment { id: metrics; target: root }
    Component { id: labelFactory; ButtonLabel {} }
    TestCase {
        name: "NativeTypographyBoundaries"
        when: windowShown
        function test_source_metrics_data() {
            return nativeTypography.filter(row => row.dpr === metrics.devicePixelRatio)
                .map(row => Object.assign({tag:row.path},row))
        }
        function test_source_metrics(data) {
            const label = createTemporaryObject(labelFactory, root)
            label.font.family = data.family === "primary" ? "Encode Sans" : "Libre Franklin"
            label.font.weight = data.weight === "bold" ? Font.Bold : data.weight === "medium" ? Font.Medium : Font.Normal
            label.font.pointSize = BleeckerFonts.pointSizeForPixels(data.requestedSize)
            label.text = data.text
            if (data.mode === "wrapped") { label.width = 132; label.wrapWidth = 132 }
            fuzzyCompare(label.logicalPixelSize, data.requestedSize, 0.000001)
            compare(label.resolvedPixelSize, data.metrics.resolvedPointSize)
            compare(label.naturalHeight, data.height)
            compare(label.baselineOffset, data.baseline)
            // QtTest's numeric comparison allows arithmetic drift. These
            // source line metrics are exact logical integers, also consumed
            // directly by the independently installed package.
            verify(label.naturalHeight === data.height, "exact logical line height")
            verify(label.baselineOffset === data.baseline, "exact logical baseline")
            if (data.mode !== "wrapped") compare(label.implicitWidth, data.width)
            compare(label.resolvedFamily, data.family === "primary" ? "Encode Sans" : "Libre Franklin")
        }
        function test_explicit_line_height_keeps_source_baseline() {
            const label = createTemporaryObject(labelFactory, root)
            label.font.family = "Encode Sans"
            label.font.pointSize = BleeckerFonts.pointSizeForPixels(14)
            label.text = "First line\nSecond line"; label.lineHeight = 24
            compare(label.naturalHeight, 48); compare(label.baselineOffset, 14)
            label.lineHeight = 0; compare(label.naturalHeight, 34)
        }
    }
}
