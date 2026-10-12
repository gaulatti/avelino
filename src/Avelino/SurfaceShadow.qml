import QtQuick
import "continuouscorners.js" as Corners

Canvas {
    id: shadow
    property real surfaceWidth: 0
    property real surfaceHeight: 0
    property real radius: BleeckerTokens.radii.card
    property real blurRadius: 10
    property real offsetY: 3
    property color shadowColor: "transparent"
    property color fillColor: "transparent"
    readonly property real margin: Math.ceil(blurRadius * 3 + Math.abs(offsetY))
    readonly property real dpr: alignment.devicePixelRatio
    x: -margin; y: -margin
    width: surfaceWidth + margin * 2; height: surfaceHeight + margin * 2
    visible: shadowColor.a > 0 && surfaceWidth > 0 && surfaceHeight > 0
    renderTarget: Canvas.Image
    canvasSize: Qt.size(Math.ceil(width * dpr),Math.ceil(height * dpr))
    canvasWindow: Qt.rect(0,0,canvasSize.width,canvasSize.height)
    PixelAlignment { id: alignment; target: shadow.parent }
    Accessible.ignored: true
    onSurfaceWidthChanged: requestPaint()
    onSurfaceHeightChanged: requestPaint()
    onRadiusChanged: requestPaint()
    onBlurRadiusChanged: requestPaint()
    onOffsetYChanged: requestPaint()
    onShadowColorChanged: requestPaint()
    onFillColorChanged: requestPaint()
    onDprChanged: requestPaint()
    onPaint: {
        const ctx = getContext("2d")
        ctx.reset(); ctx.clearRect(0,0,canvasSize.width,canvasSize.height)
        ctx.scale(dpr,dpr); ctx.translate(margin,margin)
        ctx.shadowColor = shadowColor
        ctx.shadowBlur = blurRadius * dpr
        ctx.shadowOffsetY = offsetY * dpr
        ctx.fillStyle = fillColor
        ctx.beginPath()
        for (const e of Corners.elements(surfaceWidth,surfaceHeight,radius,0)) {
            if (e.kind === "move") ctx.moveTo(e.points[0][0],e.points[0][1])
            else if (e.kind === "line") ctx.lineTo(e.points[0][0],e.points[0][1])
            else if (e.kind === "cubic") ctx.bezierCurveTo(e.points[0][0],e.points[0][1],e.points[1][0],e.points[1][1],e.points[2][0],e.points[2][1])
            else ctx.closePath()
        }
        ctx.fill()
    }
}
