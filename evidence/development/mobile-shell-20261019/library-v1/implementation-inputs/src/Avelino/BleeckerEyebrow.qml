import QtQuick

OwnedText {
    id: control
    font.pointSize: BleeckerFonts.pointSizeForPixels(10)
    font.weight: Font.Bold; tracking: 1.15
    color: BleeckerTheme.palette.desert
    Accessible.ignored: false; Accessible.role: Accessible.StaticText; Accessible.name: text
}
