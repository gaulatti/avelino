import QtQuick
import QtTest
import "../../src/Avelino/continuouscorners.js" as Corners

TestCase {
    name: "ContinuousCornerGeometry"
    function test_native_contours_data() {
        var rows = []
        for (var i = 0; i < nativeGeometry.length; i++) {
            var item = nativeGeometry[i]
            for (var j = 0; j < 2; j++) {
                var kind = j === 0 ? "fill" : "border"
                rows.push({tag: item.width + "x" + item.height + "-" + kind,
                    width: item.width, height: item.height, radius: item.radius,
                    inset: j / 2, expected: item[kind]})
            }
        }
        return rows
    }
    function test_native_contours(data) {
        var actual = Corners.elements(data.width, data.height, data.radius, data.inset)
        compare(actual.length, data.expected.length)
        for (var i = 0; i < actual.length; i++) {
            compare(actual[i].kind, data.expected[i].kind)
            compare(actual[i].points.length, data.expected[i].points.length)
            for (var j = 0; j < actual[i].points.length; j++) {
                for (var axis = 0; axis < 2; axis++) {
                    // Only Float32 arithmetic precision; visual comparisons stay at zero tolerance.
                    verify(Math.abs(actual[i].points[j][axis] - data.expected[i].points[j][axis]) <= 0.000001,
                        "Native path differs at element " + i + ", point " + j + ", axis " + axis)
                }
            }
        }
    }
    function test_empty_and_square_surfaces_have_finite_paths() {
        compare(Corners.svg(0, 20, 7, 0), "")
        compare(Corners.svg(20, 1, 7, 0.5), "")
        var square = Corners.svg(20, 20, 0, 0)
        verify(square.length > 0)
        verify(square.indexOf("NaN") === -1)
        verify(square.indexOf("Infinity") === -1)
    }
}
