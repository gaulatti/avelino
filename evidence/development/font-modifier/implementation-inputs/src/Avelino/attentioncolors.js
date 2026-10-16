.pragma library

function urgency(value) { return Math.min(10,Math.max(0,Number.isFinite(value) ? value : 0)) }
function components(hue,intensity) {
    const normalized = (((Number.isFinite(hue) ? hue : 210) % 360 + 360) % 360) / 360
    const amount = urgency(intensity) / 10
    const segment = normalized * 6, chroma = 0.66 * 0.52
    const secondary = chroma * (1 - Math.abs(segment % 2 - 1)), base = 0.52 - chroma
    const sectors = [[chroma,secondary,0],[secondary,chroma,0],[0,chroma,secondary],
                     [0,secondary,chroma],[secondary,0,chroma],[chroma,0,secondary]]
    const rgb = sectors[Math.floor(segment)], red = [0.94,0.25,0.18]
    return rgb.map((v,i) => (v + base) * (1 - amount) + red[i] * amount)
}
function labelComponents(hue,intensity,dark) {
    const amount = dark ? 0.45 : 0.12, destination = dark ? 1 : 0
    return components(hue,intensity).map(v => v * (1 - amount) + destination * amount)
}
