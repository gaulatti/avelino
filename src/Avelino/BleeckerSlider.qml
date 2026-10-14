import QtQuick
import QtQuick.Templates as T

FocusScope {
    id: control
    property real from: 0
    property real to: 1
    property real stepSize: 0
    property real value: 0
    readonly property real intervals: BleeckerValueTools.sliderIntervals(from,to,stepSize)
    readonly property real position: input.position
    readonly property real visualPosition: input.visualPosition
    readonly property bool visualFocus: input.visualFocus
    readonly property Item handle: input.handle
    readonly property Item inputItem: input
    signal moved()
    implicitWidth: 200; implicitHeight: 16
    LayoutMirroring.childrenInherit: true
    Accessible.ignored: true
    PixelAlignment { id: metrics; target: control }
    T.Slider {
        id: input
        objectName: "bleeckerSliderInput"
        anchors.fill: parent; focus: true
        from: control.from
        // SwiftUI's stepped slider offers an integral number of intervals.
        to: control.stepSize > 0 ? control.from+control.intervals*control.stepSize : control.to
        stepSize: control.stepSize; value: control.value
        // Qt 6.8's generic value interface reads these property names.
        readonly property real minimumValue: from
        readonly property real maximumValue: to
        padding: 0; focusPolicy: Qt.StrongFocus
        snapMode: stepSize > 0 ? T.Slider.SnapAlways : T.Slider.NoSnap
        Accessible.name: control.Accessible.name
        Accessible.onIncreaseAction: if (enabled) increase()
        Accessible.onDecreaseAction: if (enabled) decrease()
        onValueChanged: {
            // External values may lie beyond the effective final step. Preserve
            // that caller value while reflecting the native input's clamp.
            const displayed=Math.max(from,Math.min(to,control.value))
            if (value !== displayed) {
                if (enabled) BleeckerValueTools.moveSlider(control,value)
                else BleeckerValueTools.setValue(input,displayed)
            }
        }
        contentItem: Canvas {
            id: ticks
            readonly property real intervals: control.intervals
            readonly property color tickColor: BleeckerTheme.nativeSliderTick
            readonly property real dpr: metrics.devicePixelRatio
            Accessible.ignored: true
            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()
            onIntervalsChanged: requestPaint()
            onTickColorChanged: requestPaint()
            onDprChanged: requestPaint()
            onPaint: {
                const ctx=getContext("2d"),span=Math.max(0,width-20),start=(width-span)/2,r=1,cy=height-1
                ctx.reset();ctx.clearRect(0,0,width,height)
                if (intervals < 0) return
                ctx.fillStyle=tickColor
                const spacing=intervals > 0 ? span/intervals : span+1
                if (spacing > 2*r) {
                    for (let i=0;i<=intervals;i++) {
                        ctx.beginPath();ctx.arc(start+i*spacing,cy,r,0,Math.PI*2);ctx.fill()
                    }
                } else {
                    // Rasterize the union of overlapping circles by physical
                    // column; work stays bounded even for a million steps.
                    for (let px=Math.floor((start-r)*dpr);px<=Math.ceil((start+span+r)*dpr);px++) {
                        const x=(px+0.5)/dpr
                        const i=intervals > 0 ? Math.max(0,Math.min(intervals,Math.round((x-start)/spacing))) : 0
                        const dx=x-(start+i*spacing)
                        if (Math.abs(dx)<=r) {
                            const half=Math.sqrt(r*r-dx*dx)
                            ctx.fillRect(px/dpr,cy-half,1/dpr,2*half)
                        }
                    }
                }
            }
        }
        background: Rectangle {
            objectName: "bleeckerSliderTrack"
            x: 0
            y: (control.height-height)/2
            width: control.width
            height: 6
            radius: 3; antialiasing: true
            color: BleeckerTheme.nativeSliderTrack
            Rectangle {
                objectName: "bleeckerSliderFill"
                x: input.mirrored ? parent.width-width : 0
                y: 0
                width: input.position*parent.width
                height: parent.height
                radius: parent.radius; antialiasing: true
                color: control.enabled ? BleeckerTheme.nativeSliderFill : BleeckerTheme.nativeSliderDisabledFill
            }
        }
        handle: Item {
            objectName: "bleeckerSliderHandle"
            z: 1
            implicitWidth: 20
            implicitHeight: 16
            x: input.visualPosition*(control.width-width)
            y: (control.height-height)/2
            Accessible.ignored: true
            Canvas {
                id: shadow
                anchors.fill: parent; anchors.margins: -5
                onWidthChanged: requestPaint()
                onHeightChanged: requestPaint()
                onPaint: {
                    const ctx=getContext("2d"),w=parent.width,h=parent.height,r=Math.min(w,h)/2
                    ctx.reset();ctx.clearRect(0,0,width,height);ctx.translate(5,5)
                    ctx.shadowColor=BleeckerTheme.alpha("black",0.12);ctx.shadowBlur=3;ctx.shadowOffsetY=1
                    ctx.fillStyle=BleeckerTheme.nativeSliderHandle
                    ctx.beginPath();ctx.moveTo(r,0);ctx.lineTo(w-r,0)
                    ctx.arc(w-r,r,r,-Math.PI/2,0);ctx.lineTo(w,h-r)
                    ctx.arc(w-r,h-r,r,0,Math.PI/2);ctx.lineTo(r,h)
                    ctx.arc(r,h-r,r,Math.PI/2,Math.PI);ctx.lineTo(0,r)
                    ctx.arc(r,r,r,Math.PI,Math.PI*1.5);ctx.closePath();ctx.fill()
                }
                Connections { target: BleeckerTheme; function onDarkChanged() { shadow.requestPaint() } }
            }
            Rectangle {
                anchors.fill: parent; radius: Math.min(width,height)/2
                color: BleeckerTheme.nativeSliderHandle; antialiasing: true
            }
            Rectangle {
                anchors.fill: parent; anchors.margins: -3
                radius: Math.min(width,height)/2; color: "transparent"
                border.width: input.visualFocus ? 2 : 0; border.color: BleeckerTheme.palette.sea
            }
        }
    }
}
