import QtQuick

Item {
    id: control
    property var segments: []
    readonly property color trackColor: BleeckerTheme.palette.muted
    implicitWidth: 120; implicitHeight: 8
    readonly property real segmentExtent: segments.reduce((extent, segment) => extent + Math.max(0, width * segment.value), 0) + Math.max(0, segments.length - 1) * 2
    onSegmentsChanged: track.requestPaint()
    onWidthChanged: track.requestPaint()
    onHeightChanged: track.requestPaint()
    onTrackColorChanged: track.requestPaint()
    Canvas {
      id: track
      objectName: "bleeckerProgressStackTrack"
      width: control.segmentExtent; height: control.height
      onWidthChanged: requestPaint()
      onPaint: {
        const ctx = getContext("2d"), r = Math.min(width, height) / 2
        ctx.reset()
        if (width <= 0 || height <= 0) return
        ctx.beginPath()
        ctx.moveTo(r, 0); ctx.lineTo(width-r, 0)
        ctx.arc(width-r, r, r, -Math.PI/2, 0)
        ctx.lineTo(width, height-r); ctx.arc(width-r, height-r, r, 0, Math.PI/2)
        ctx.lineTo(r, height); ctx.arc(r, height-r, r, Math.PI/2, Math.PI)
        ctx.lineTo(0, r); ctx.arc(r, r, r, Math.PI, Math.PI*1.5)
        ctx.closePath(); ctx.clip()
        ctx.fillStyle = control.trackColor; ctx.fillRect(0, 0, width, height)
        let x = 0
        for (const segment of control.segments) {
            const extent = Math.max(0, control.width * segment.value)
            ctx.fillStyle = segment.color; ctx.fillRect(x, 0, extent, height)
            x += extent + 2
        }
      }
    }
}
