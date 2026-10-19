import QtQuick

Item {
    id: control
    required property string name
    property url source: ""
    property string size: "md"
    readonly property string initials: BleeckerTextTools.avatarInitials(name)
    readonly property int imageStatus: image.status
    readonly property real edge: {
        switch (size) {
        case "xs": return 24
        case "sm": return 32
        case "md": return 40
        case "lg": return 52
        case "xl": return 72
        default: throw new Error("Unknown Bleecker avatar size: " + size)
        }
    }
    implicitWidth: edge; implicitHeight: edge
    Accessible.role: Accessible.Graphic; Accessible.name: name
    Item {
        id: face
        width: control.edge; height: width
        x: (control.width-width)/2; y: (control.height-height)/2
        Rectangle { anchors.fill: parent; radius: width/2; color: BleeckerTheme.palette.muted; Accessible.ignored: true }
        Image {
            id: image
            source: control.source; visible: false
            onStatusChanged: canvas.requestPaint()
            onSourceSizeChanged: canvas.requestPaint()
            Accessible.ignored: true
        }
        Canvas {
            id: canvas
            objectName: "bleeckerAvatarImage"
            anchors.fill: parent
            readonly property real dpr: alignment.devicePixelRatio
            renderTarget: Canvas.Image
            PixelAlignment { id: alignment; target: canvas.parent }
            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()
            onDprChanged: requestPaint()
            onPaint: {
                const ctx = getContext("2d")
                ctx.reset(); ctx.clearRect(0,0,width,height)
                if (image.status !== Image.Ready) return
                ctx.beginPath(); ctx.arc(width/2,height/2,width/2,0,Math.PI*2); ctx.clip()
                const square = Math.min(image.sourceSize.width,image.sourceSize.height)
                ctx.drawImage(image,(image.sourceSize.width-square)/2,(image.sourceSize.height-square)/2,
                    square,square,0,0,width,height)
            }
            Accessible.ignored: true
        }
        OwnedText {
            objectName: "bleeckerAvatarInitials"
            text: control.initials; visible: control.source.toString() === ""
            x: (parent.width-width)/2; y: (parent.height-height)/2
            font.pointSize: BleeckerFonts.pointSizeForPixels(control.edge*0.32)
            font.weight: Font.DemiBold; color: BleeckerTheme.palette.sea
        }
        Rectangle {
            objectName: "bleeckerAvatarBorder"
            anchors.fill: parent; radius: width/2; color: "transparent"
            border.width: 1; border.color: BleeckerTheme.palette.border; antialiasing: true
            Accessible.ignored: true
        }
    }
}
