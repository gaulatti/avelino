.pragma library

// Measured native path coefficients; see evidence/geometry/native-rounded-rectangle.json.
var extent = 1.5286649465560913
var tangent = 1.0884900093078613
var shoulder = 0.8684070110321045
var diagonal = 0.6314939856529236
var edge = 0.07491140067577362
var middle = 0.3728240132331848
var intermediate = 0.16906000673770905

function axis(length, radius) {
    var a = Math.min(extent, Math.fround(length / (2 * radius)))
    var blend = (a - 1) / (extent - 1)
    return [a * radius,
            Math.fround(0.9599999785423279 + (tangent - 0.9599999785423279) * blend) * radius,
            Math.fround(0.8199999928474426 + (shoulder - 0.8199999928474426) * blend) * radius]
}

function elements(width, height, radius, inset) {
    var l = inset, t = inset, r = width - inset, b = height - inset
    if (r <= l || b <= t) return []
    var corner = Math.min(Math.max(0, radius - inset), (r - l) / 2, (b - t) / 2)
    var path = []
    function add(kind, coordinates) {
        var points = []
        for (var i = 0; i < coordinates.length; i += 2)
            points.push([coordinates[i], coordinates[i + 1]])
        path.push({kind: kind, points: points})
    }
    add("move", [r, (t + b) / 2])
    if (corner === 0) {
        add("line", [r, b]); add("line", [l, b]); add("line", [l, t]); add("line", [r, t])
    } else {
        var x = axis(r - l, corner), y = axis(b - t, corner)
        var d = diagonal * corner, e = edge * corner
        var f = middle * corner, g = intermediate * corner
        add("line", [r, b - y[0]])
        add("cubic", [r, b - y[1], r, b - y[2], r - e, b - d])
        add("cubic", [r - g, b - f, r - f, b - g, r - d, b - e])
        add("cubic", [r - x[2], b, r - x[1], b, r - x[0], b])
        add("line", [l + x[0], b])
        add("cubic", [l + x[1], b, l + x[2], b, l + d, b - e])
        add("cubic", [l + f, b - g, l + g, b - f, l + e, b - d])
        add("cubic", [l, b - y[2], l, b - y[1], l, b - y[0]])
        add("line", [l, t + y[0]])
        add("cubic", [l, t + y[1], l, t + y[2], l + e, t + d])
        add("cubic", [l + g, t + f, l + f, t + g, l + d, t + e])
        add("cubic", [l + x[2], t, l + x[1], t, l + x[0], t])
        add("line", [r - x[0], t])
        add("cubic", [r - x[1], t, r - x[2], t, r - d, t + e])
        add("cubic", [r - f, t + g, r - g, t + f, r - e, t + d])
        add("cubic", [r, t + y[2], r, t + y[1], r, t + y[0]])
    }
    add("close", [])
    return path
}

function svg(width, height, radius, inset) {
    var commands = {move: "M", line: "L", cubic: "C", close: "Z"}
    return elements(width, height, radius, inset).map(function(element) {
        return commands[element.kind] + element.points.map(function(point) {
            return point[0] + "," + point[1]
        }).join(" ")
    }).join(" ")
}
