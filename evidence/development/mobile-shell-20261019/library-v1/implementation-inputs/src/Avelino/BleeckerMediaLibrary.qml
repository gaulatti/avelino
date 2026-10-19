import QtQuick

MediaLibraryBase {
    items: []
    mirrored: LayoutMirroring.enabled
    LayoutMirroring.childrenInherit: true
    BleeckerLayout.minimumWidth: 0
    BleeckerLayout.idealWidth: naturalWidth
    BleeckerLayout.fillsWidth: true
}
