import QtQuick

ButtonLabel {
    id: label
    font.family: BleeckerTheme.primaryFont
    font.pointSize: BleeckerFonts.pointSizeForPixels(14)
    color: BleeckerTheme.palette.textPrimary
    height: Math.ceil(naturalHeight * alignment.devicePixelRatio) / alignment.devicePixelRatio
    PixelAlignment { id: alignment; target: label.parent; origin: Qt.point(label.x, label.y + label.baselineOffset) }
    transform: Translate { x: alignment.offset.x; y: alignment.offset.y }
    Accessible.ignored: true
}
