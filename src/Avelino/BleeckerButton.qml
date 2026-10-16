import QtQuick
import QtQuick.Templates as T

FocusScope {
    id: control
    property alias text: nativeButton.text
    property string accessibleName: text
    readonly property Item inputItem: nativeButton
    property alias font: nativeButton.font
    property alias background: nativeButton.background
    property alias contentItem: nativeButton.contentItem
    property alias focusPolicy: nativeButton.focusPolicy
    readonly property bool down: nativeButton.down
    readonly property bool effectiveEnabled: nativeButton.enabled
    signal clicked()
    property string variant: "primary"
    property string size: "md"
    property bool loading: false
    // A finite layout proposal for the label; -1 keeps intrinsic sizing.
    property real maximumWidth: -1
    readonly property real effectiveMaximumWidth: BleeckerLayout.proposedWidth<0 ? maximumWidth
        : maximumWidth<0 ? BleeckerLayout.proposedWidth:Math.min(maximumWidth,BleeckerLayout.proposedWidth)
    readonly property real contentMinimumWidth:contentItem===defaultContent ? 0
        :Math.max(0,contentItem.BleeckerLayout.minimumWidth>=0 ? contentItem.BleeckerLayout.minimumWidth:contentItem.implicitWidth)
    BleeckerLayout.minimumWidth:leftPadding+rightPadding+contentMinimumWidth
    BleeckerLayout.idealWidth:(contentItem===defaultContent ? label.unwrappedWidth+(loading ? spinner.width+BleeckerTokens.spacing.inline:0):contentItem.implicitWidth)+leftPadding+rightPadding
    readonly property var p: BleeckerTheme.palette
    readonly property int minimumHeight: size === "xs" ? 28 : size === "sm" ? 36 : size === "lg" ? 48 : 40
    readonly property int textSize: size === "xs" ? 12 : size === "sm" ? 13 : size === "lg" ? 15 : 14
    readonly property color foregroundColor: variant === "primary" ? p.primaryForeground : variant === "outline" ? p.sea : variant === "destructive" ? p.destructiveForeground : p.textPrimary
    readonly property color fillColor: {
        switch (variant) {
        case "primary": return down ? p.deepSea : p.primary
        case "secondary": return down ? p.muted : p.card
        case "outline": return down ? BleeckerTheme.alpha(p.sea, 0.08) : "transparent"
        case "subtle": return down ? BleeckerTheme.alpha(p.sand, 0.3) : BleeckerTheme.alpha(p.lightSand, 0.75)
        case "ghost": case "link": return down ? p.muted : "transparent"
        case "destructive": return down ? BleeckerTheme.alpha(p.destructive, 0.9) : p.destructive
        default: throw new Error("Unknown Bleecker button variant: " + variant)
        }
    }
    readonly property color strokeColor: variant === "primary" ? p.primary : variant === "secondary" ? p.border : variant === "outline" ? BleeckerTheme.alpha(p.sea, 0.5) : variant === "destructive" ? p.destructive : "transparent"
    implicitWidth: effectiveMaximumWidth===-1 ? contentItem.implicitWidth+leftPadding+rightPadding
        : Math.ceil(Math.min(contentItem.implicitWidth+leftPadding+rightPadding,Math.max(leftPadding+rightPadding+contentMinimumWidth,effectiveMaximumWidth))*controlAlignment.devicePixelRatio)/controlAlignment.devicePixelRatio
    implicitHeight: Math.max(contentItem.implicitHeight, variant === "link" ? 0 : minimumHeight)
    readonly property real leftPadding: size === "xs" ? 10 : size === "sm" ? 14 : size === "lg" ? 24 : 18
    readonly property real rightPadding: leftPadding
    opacity: effectiveEnabled ? 1 : 0.45
    PixelAlignment {id:controlAlignment;target:control}
    transform: [
        Translate { y: control.down ? 1 : 0; Behavior on y { NumberAnimation { duration: BleeckerTheme.reducedMotion ? 0 : BleeckerTokens.durations.control; easing.type: Easing.OutCubic } } },
        Scale { origin.x: control.width / 2; origin.y: control.height / 2; xScale: control.down ? 0.99 : 1; yScale: xScale
            Behavior on xScale { NumberAnimation { duration: BleeckerTheme.reducedMotion ? 0 : BleeckerTokens.durations.control; easing.type: Easing.OutCubic } } }
    ]
    T.Button {
        id: nativeButton
        anchors.fill: parent
        enabled: !control.loading
        focus: true
        focusPolicy: Qt.StrongFocus
        font.family: BleeckerTheme.primaryFont
        font.pointSize: BleeckerFonts.pointSizeForPixels(control.textSize * BleeckerTheme.textScale)
        font.weight: Font.Medium
        leftPadding: control.leftPadding
        rightPadding: control.rightPadding
        Accessible.name: control.accessibleName
        Accessible.description: control.loading ? qsTr("Loading") : ""
        onClicked: control.clicked()
        contentItem: Item {
            id:defaultContent
            implicitWidth: label.implicitWidth + (control.loading ? spinner.width + BleeckerTokens.spacing.inline : 0)
            implicitHeight: Math.max(label.height, control.loading ? spinner.height : 0)
            BleeckerLoadingSpinner {
                id: spinner
                visible: control.loading
                size: "sm"
                y: (parent.height - height) / 2
            }
            ButtonLabel {
                id: label
                objectName: "bleeckerButtonLabel"
                text: control.text
                wrapWidth: BleeckerTextTools.proposedWidth(control.effectiveMaximumWidth,control.leftPadding+control.rightPadding+(control.loading ? spinner.width+BleeckerTokens.spacing.inline : 0))
                width:control.effectiveMaximumWidth<0 ? implicitWidth:Math.min(implicitWidth,Math.max(0,parent.width-x))
                clip:control.effectiveMaximumWidth>=0
                font: control.font
                color: control.foregroundColor
                height: Math.ceil(naturalHeight * labelAlignment.devicePixelRatio) / labelAlignment.devicePixelRatio
                x: control.loading ? spinner.width + BleeckerTokens.spacing.inline : 0
                y: (parent.height - height) / 2
                PixelAlignment { id: labelAlignment; target: label.parent; origin: Qt.point(label.x, label.y + label.baselineOffset) }
                transform: Translate { x: labelAlignment.offset.x; y: labelAlignment.offset.y }
            }
        }
        background: ContinuousSurface {
            objectName: "bleeckerButtonSurface"
            radius: BleeckerTokens.radii.button
            color: control.fillColor
            borderWidth: 1
            borderColor: control.strokeColor
            Behavior on color { ColorAnimation { duration: BleeckerTheme.reducedMotion ? 0 : BleeckerTokens.durations.control; easing.type: Easing.OutCubic } }
        }
    }
}
